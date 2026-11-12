import serial
import time
import csv
from datetime import datetime
import numpy as np
import os

# Configuration defines
SAMPLE_TIME_MS = 2  # Time between samples in milliseconds
MAX_MEASUREMENT_TIME = 30  # Maximum measurement time in seconds
EARLY_STOP_WINDOW = 20  # Number of samples to check for early stabilization
EARLY_STOP_THRESHOLD = 0.08  # Voltage threshold for early stabilization (V)
SETTLING_BAND_PERCENT = 5  # Percentage band for settling time calculation
FINAL_AVG_SAMPLES = 20  # Number of samples to average for final value
MIN_SAMPLES = 10  # Minimum number of samples before checking stabilization
SERIAL_PORT = 'COM4'  # Serial port
BAUD_RATE = 230400  # Baud rate
VOLTAGE_REF = 4.8  # Reference voltage for ADC conversion
ADC_RESOLUTION = 1024  # ADC resolution (10-bit)
PWM_RESOLUTION = 4096


def send_control_command(ser, command,option = 0):
    """Send control bytes to start or stop ADC readings"""
    ser.write(bytes([0x15, command, option]))
    # time.sleep(0.1)  # Small delay to ensure command is processed


def send_step_command(ser, value):
    """Send step command with 12-bit value (0-0xFFF)"""
    msb = (value >> 8) & 0xFF
    lsb = value & 0xFF
    ser.write(bytes([0x14, msb, lsb]))
def send_ref_value(ser,value):
    msb = (value >> 8) & 0xFF
    lsb = value & 0xFF
    ser.write(bytes([0x13, msb, lsb]))


def check_early_stabilization(values, window_size=EARLY_STOP_WINDOW, threshold=EARLY_STOP_THRESHOLD):
    """Check if signal has stabilized early to stop sampling"""
    if len(values) < window_size:
        return False

    recent_values = values[-window_size:]
    mean_value = np.mean(recent_values)
    max_deviation = max(abs(v - mean_value) for v in recent_values)

    return max_deviation <= threshold


def find_settling_time(values, final_value, band_percent=SETTLING_BAND_PERCENT):
    """Find settling time within band_percent of final value"""
    band = final_value * (band_percent / 100)
    upper_limit = final_value + band
    lower_limit = final_value - band

    # Find first point where value stays within band
    for i in range(len(values)):
        if all(lower_limit <= v <= upper_limit for v in values[i:]):
            return i * (SAMPLE_TIME_MS / 1000)  # Convert to seconds
    return None


def get_next_test_number():
    """Get the next test number from counter file"""
    counter_file = 'stepResponse/test_counter.txt'
    os.makedirs('stepResponse', exist_ok=True)

    if os.path.exists(counter_file):
        with open(counter_file, 'r') as f:
            count = int(f.read().strip())
    else:
        count = 0

    count += 1
    with open(counter_file, 'w') as f:
        f.write(str(count))

    return count
def detect_settling(values, final_value=None):
    """Detect when signal has settled within SETTLING_BAND_PERCENT of final value"""
    if len(values) < MIN_SAMPLES:
        return None

    if final_value is None:
        final_value = np.mean(values[-FINAL_AVG_SAMPLES:])

    band = final_value * (SETTLING_BAND_PERCENT / 100)

    window_size = 5
    for i in range(len(values) - window_size):
        window = values[i:i + window_size]
        if all(abs(v - final_value) <= band for v in window):
            if i + window_size + 5 <= len(values):
                if all(abs(v - final_value) <= band for v in values[i:i + window_size + 5]):
                    settling_time = i * (SAMPLE_TIME_MS / 1000)
                    return settling_time
    return None


def measure_step_response(ser, step_value, max_time=MAX_MEASUREMENT_TIME):
    """Measure ADC response for a given step value with early stabilization detection"""
    # Clear any existing data
    while ser.in_waiting:
        ser.read(ser.in_waiting)

    values = []
    times = []
    buffer = bytearray()
    start_time = time.perf_counter()
    sample_count = 0

    send_control_command(ser, 0x02)  # Start ADC
    send_step_command(ser, step_value)  # Send step command

    settled = False
    confirm_counter = 0

    while (time.perf_counter() - start_time) < max_time:
        if ser.in_waiting > 0:
            buffer.extend(ser.read(ser.in_waiting))

            while len(buffer) >= 3:
                if buffer[0] == 0x15:
                    precise_time = sample_count * (SAMPLE_TIME_MS / 1000.0)
                    msb = buffer[1]
                    lsb = buffer[2]
                    raw_value = (msb << 8) | lsb
                    voltage = (raw_value / ADC_RESOLUTION) * VOLTAGE_REF

                    values.append(voltage)
                    times.append(precise_time)
                    sample_count += 1
                    buffer = buffer[3:]

                    # Start checking only after minimum samples collected
                    if len(values) >= MIN_SAMPLES:
                        if not settled:
                            if check_early_stabilization(values):
                                settled = True
                                confirm_counter = 0
                        else:
                            if check_early_stabilization(values):
                                confirm_counter += 1
                                if confirm_counter >= EARLY_STOP_WINDOW:
                                    send_control_command(ser, 0x03)  # Stop ADC
                                    return values, times
                            else:
                                settled = False  # Reset if signal breaks band

                else:
                    buffer = buffer[1:]  # Remove unexpected byte

    send_control_command(ser, 0x03)  # Stop if max time reached
    return values, times

def save_test_data(test_number, values_list, step_values, final_values, settling_times):
    """Save test data to CSV files
    values_list: list of (times, values) tuples for each step
    step_values: list of step values
    final_values: list of final voltages
    settling_times: list of settling times
    """
    # Create base directories
    os.makedirs('stepResponse/values', exist_ok=True)
    os.makedirs('stepResponse/prettyValues', exist_ok=True)

    # Create test-specific directories
    test_values_dir = f'stepResponse/values/step_response_values_{test_number:03d}'
    test_pretty_dir = f'stepResponse/prettyValues/step_response_summary_{test_number:03d}'
    os.makedirs(test_values_dir, exist_ok=True)
    os.makedirs(test_pretty_dir, exist_ok=True)

    # Save summary file
    pretty_file = f'{test_pretty_dir}/summary.csv'
    with open(pretty_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Parameter', 'Value'])
        csvwriter.writerow(['Test Number', f"{test_number:03d}"])
        csvwriter.writerow(['Reference Voltage', f"{VOLTAGE_REF}V"])
        csvwriter.writerow(['Sample Time', f"{SAMPLE_TIME_MS}ms"])

        total_samples = sum(len(values) for _, values in values_list)
        csvwriter.writerow(['Total Samples', total_samples])
        csvwriter.writerow(['Total Time', f"{total_samples * 0.1:.3f}s"])

        for step_value, final_value, settling_time in zip(step_values, final_values, settling_times):
            step_voltage = (step_value / 0xFFF) * VOLTAGE_REF
            csvwriter.writerow(['', ''])  # Empty row for separation
            csvwriter.writerow(['Step Value (hex)', f"0x{step_value:03X}"])
            csvwriter.writerow(['Step Voltage', f"{step_voltage:.3f}V"])
            csvwriter.writerow(['Final Voltage', f"{final_value:.3f}V"])
            if settling_time is not None:
                csvwriter.writerow(['Settling Time', f"{settling_time * 1000:.1f}ms"])

    # Calculate total time offset for each step
    time_offsets = [0]  # First step starts at 0
    for i in range(1, len(step_values)):
        # Add the time of all previous steps
        time_offsets.append(sum(len(times) for times, _ in values_list[:i]) * 0.1)

    # Save transition data files
    for i in range(len(step_values)):
        # Calculate input voltages for current and next step
        current_step = step_values[i]
        current_input = (current_step / 0xFFF) * VOLTAGE_REF

        # Get data for this step
        times, values = values_list[i]

        # Save step data with adjusted times
        step_file = f'{test_values_dir}/step_{i + 1:02d}_{current_input:.3f}V.csv'
        with open(step_file, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Time (s)', 'Output Voltage (V)', 'Input Voltage (V)'])

            for time_val, voltage in zip(times, values):
                # Add the time offset to make time relative to test start
                adjusted_time = time_val + time_offsets[i]
                csvwriter.writerow([f"{adjusted_time:.6f}", f"{voltage:.3f}", f"{current_input:.3f}"])

        # If there's a next step, save transition data
        if i < len(step_values) - 1:
            next_step = step_values[i + 1]
            next_input = (next_step / 0xFFF) * VOLTAGE_REF

            # Get data for next step
            next_times, next_values = values_list[i + 1]

            # Combine last samples from current step with first samples from next step
            transition_file = f'{test_values_dir}/transition_{i + 1:02d}_{current_input:.3f}V_to_{i + 2:02d}_{next_input:.3f}V.csv'
            with open(transition_file, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Time (s)', 'Output Voltage (V)', 'Input Voltage (V)'])

                # Add last 10 samples from current step with adjusted time
                for time_val, voltage in zip(times[-10:], values[-10:]):
                    adjusted_time = time_val + time_offsets[i]
                    csvwriter.writerow([f"{adjusted_time:.6f}", f"{voltage:.3f}", f"{current_input:.3f}"])

                # Add first 50 samples from next step with adjusted time
                for time_val, voltage in zip(next_times[:50], next_values[:50]):
                    adjusted_time = time_val + time_offsets[i + 1]
                    csvwriter.writerow([f"{adjusted_time:.6f}", f"{voltage:.3f}", f"{next_input:.3f}"])

    # Save complete data file
    complete_file = f'{test_values_dir}/complete_data.csv'
    with open(complete_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Time (s)', 'Output Voltage (V)', 'Input Voltage (V)'])

        for i, (step_value, (times, voltages)) in enumerate(zip(step_values, values_list)):
            # Calculate input voltage for this step
            input_voltage = (step_value / 0xFFF) * VOLTAGE_REF
            for time_val, voltage in zip(times, voltages):
                # Add the time offset to make time relative to test start
                adjusted_time = time_val + time_offsets[i]
                csvwriter.writerow([f"{adjusted_time:.6f}", f"{voltage:.3f}", f"{input_voltage:.3f}"])


def step_response_test(port=SERIAL_PORT, baud_rate=BAUD_RATE):
    """Perform step response test for specific hex values"""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Starting step response test on {port} at {baud_rate} baud...")

        # Get test number
        test_number = get_next_test_number()
        print(f"Test #{test_number:03d}")

        # First, send 0x00 and wait for settling
        print("\nInitializing with 0x00...")
        values, times = measure_step_response(ser, 0x00)
        final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
        print(f"Initialization complete:")
        print(f"  Samples: {len(values)}")
        print(f"  Final voltage: {final_value:.3f}V")

        # Small delay after initialization
        #time.sleep(0.5)

        # Test values (specific hex values)
        test_values = [0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF]

        # Lists to store all test data
        values_list = []
        final_values = []
        settling_times = []

        for value in test_values:
            print(f"\nTesting step value 0x{value:03X}")

            values, times = measure_step_response(ser, value)
            values_list.append((times, values))

            # Calculate final value and settling time
            final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
            final_values.append(final_value)
            settling_time = detect_settling(values, final_value)
            settling_times.append(settling_time)

            print(f"Completed step 0x{value:03X}:")
            print(f"  Samples: {len(values)}")
            print(f"  Final voltage: {final_value:.3f}V")
            if settling_time is not None:
                print(f"  Settling time: {settling_time * 1000:.1f}ms")

            # Small delay between tests
            #time.sleep(0.5)

        # Save all test data
        save_test_data(test_number, values_list, test_values, final_values, settling_times)
        print(f"\nTest data saved as test #{test_number:03d}")

    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def step_response_test_with_vector(voltage_values, port=SERIAL_PORT, baud_rate=BAUD_RATE):
    """Perform step response test for specified voltage values (in volts)"""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Starting step response test on {port} at {baud_rate} baud...")

        # Get test number
        test_number = get_next_test_number()
        print(f"Test #{test_number:03d}")

        # First, send 0x00 and wait for settling
        print("\nInitializing with 0x00...")
        values, times = measure_step_response(ser, 0x00)
        final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
        print(f"Initialization complete:")
        print(f"  Samples: {len(values)}")
        print(f"  Final voltage: {final_value:.3f}V")

        # Convert input voltages to 12-bit hex values (0x000 to 0xFFF)
        test_values = [int((v / VOLTAGE_REF) * 0xFFF) for v in voltage_values]
        test_values = [min(max(val, 0), 0xFFF) for val in test_values]  # Clamp to valid range

        # Lists to store all test data
        values_list = []
        final_values = []
        settling_times = []

        for voltage, value in zip(voltage_values, test_values):
            print(f"\nTesting step to {voltage:.3f} V (0x{value:03X})")

            values, times = measure_step_response(ser, value)
            values_list.append((times, values))

            final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
            final_values.append(final_value)
            settling_time = detect_settling(values, final_value)
            settling_times.append(settling_time)

            print(f"Completed step to {voltage:.3f} V:")
            print(f"  Samples: {len(values)}")
            print(f"  Final voltage: {final_value:.3f}V")
            if settling_time is not None:
                print(f"  Settling time: {settling_time * 1000:.1f}ms")

        # Save all test data
        save_test_data(test_number, values_list, test_values, final_values, settling_times)
        print(f"\nTest data saved as test #{test_number:03d}")

    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def step_response_test_timed(voltage_values, timeout=2.0, delay_between_steps=1.0, port=SERIAL_PORT, baud_rate=BAUD_RATE):
    """Perform step response test with fixed timeout and delay between steps, no early stabilization."""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Starting timed step response test on {port} at {baud_rate} baud...")

        test_number = get_next_test_number()
        print(f"Test #{test_number:03d}")

        print("\nInitializing with 0x00...")
        values, times = measure_step_response_fixed_time(ser, 0x00, timeout)
        final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
        print(f"Initialization complete:")
        print(f"  Samples: {len(values)}")
        print(f"  Final voltage: {final_value:.3f}V")

        test_values = [int((v / VOLTAGE_REF) * 0xFFF) for v in voltage_values]
        test_values = [min(max(val, 0), 0xFFF) for val in test_values]  # Clamp

        values_list = []
        final_values = []
        settling_times = []  # This will be None since no early stop

        for voltage, value in zip(voltage_values, test_values):
            print(f"\nTesting step to {voltage:.3f} V (0x{value:03X}) for {timeout}s")

            values, times = measure_step_response_fixed_time(ser, value, timeout)
            values_list.append((times, values))

            final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
            final_values.append(final_value)
            settling_times.append(None)  # No settling detection

            print(f"Completed step to {voltage:.3f} V:")
            print(f"  Samples: {len(values)}")
            print(f"  Final voltage: {final_value:.3f}V")

            time.sleep(delay_between_steps)

        save_test_data(test_number, values_list, test_values, final_values, settling_times)
        print(f"\nTest data saved as test #{test_number:03d}")

    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
def step_response_test_timed(voltage_values, timeout=2.0, delay_between_steps=1.0, port=SERIAL_PORT, baud_rate=BAUD_RATE):
    """Perform step response test with fixed timeout and delay between steps, no early stabilization."""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Starting timed step response test on {port} at {baud_rate} baud...")

        test_number = get_next_test_number()
        print(f"Test #{test_number:03d}")

        # Initialization step with 0x00
        print("\nInitializing with 0x00...")
        values, times = measure_step_response_fixed_time(ser, 0x00, timeout)
        final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
        print(f"Initialization complete:")
        print(f"  Samples: {len(values)}")
        print(f"  Final voltage: {final_value:.3f}V")

        # Convert voltages to 12-bit step values
        test_values = [int((v / VOLTAGE_REF) * 0xFFF) for v in voltage_values]
        test_values = [min(max(val, 0), 0xFFF) for val in test_values]  # Clamp

        values_list = []
        final_values = []
        settling_times = []

        for voltage, value in zip(voltage_values, test_values):
            print(f"\nTesting step to {voltage:.3f} V (0x{value:03X}) for {timeout}s")

            values, times = measure_step_response_fixed_time(ser, value, timeout)
            values_list.append((times, values))

            final_value = np.mean(values[-FINAL_AVG_SAMPLES:])
            final_values.append(final_value)
            settling_times.append(None)  # No settling detection

            print(f"Completed step to {voltage:.3f} V:")
            print(f"  Samples: {len(values)}")
            print(f"  Final voltage: {final_value:.3f}V")

            time.sleep(delay_between_steps)

        save_test_data(test_number, values_list, test_values, final_values, settling_times)
        print(f"\nTest data saved as test #{test_number:03d}")

    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def measure_step_response_fixed_time(ser, step_value, duration_sec):
    """Measure ADC response for a given step value, for a fixed duration without early stop."""
    # Clear input buffer
    while ser.in_waiting:
        ser.read(ser.in_waiting)

    values = []
    times = []
    buffer = bytearray()
    sample_count = 0

    send_control_command(ser, 0x02)           # Start ADC reading
    send_step_command(ser, step_value)        # Send step value
    start_time = time.perf_counter()

    while (time.perf_counter() - start_time) < duration_sec:
        if ser.in_waiting > 0:
            buffer.extend(ser.read(ser.in_waiting))

            while len(buffer) >= 3:
                if buffer[0] == 0x15:
                    precise_time = sample_count * (SAMPLE_TIME_MS / 1000.0)
                    msb = buffer[1]
                    lsb = buffer[2]
                    raw_value = (msb << 8) | lsb
                    voltage = (raw_value / ADC_RESOLUTION) * VOLTAGE_REF

                    values.append(voltage)
                    times.append(precise_time)
                    sample_count += 1
                    buffer = buffer[3:]
                else:
                    buffer = buffer[1:]

    send_control_command(ser, 0x03)  # Stop ADC after fixed time
    return values, times
def custom_reference_test(port=SERIAL_PORT, baud_rate=BAUD_RATE):
    """Run a custom reference test: step input, output selection, duration, CSV logging with header 0x0B"""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print("=== Custom Reference Test ===")

        # 1. Cere valoarea de referință (în Volți)
        voltage = float(input("Enter reference step voltage (0 - 4.71V): "))
        voltage = min(max(voltage, 0.0), VOLTAGE_REF)
        ref_value = int((voltage / VOLTAGE_REF) * 0x3FF)
        print("sending "+ str(ref_value))

        # 2. Cere tipul de ieșire
        output_type = int(input("Choose output (1 = Controller, 2 = Process): "))
        if output_type not in [1, 2]:
            print("Invalid output option.")
            return

        send_step_command(ser, 0x0) #set the proces to 0
        time.sleep(5)

        # 3. Cere durata testului
        duration = float(input("Enter test duration in seconds: "))

        # 4. Trimite valoarea de referință
        send_ref_value(ser, ref_value)

        # 5. Trimite comanda de control
        send_control_command(ser, 0x05, output_type-1)

        # 6. Colectează date cu header 0x0B
        values = []
        times = []
        buffer = bytearray()
        start_time = time.perf_counter()
        sample_count = 0

        while (time.perf_counter() - start_time) < duration:
            if ser.in_waiting > 0:
                buffer.extend(ser.read(ser.in_waiting))

                while len(buffer) >= 3:
                    if buffer[0] == 0x0B:
                        msb = buffer[1]
                        lsb = buffer[2]
                        raw = (msb << 8) | lsb
                        if output_type == 2:
                            voltage_out = (raw / ADC_RESOLUTION) * VOLTAGE_REF
                        else:
                            voltage_out = (raw / PWM_RESOLUTION) * VOLTAGE_REF
                        time_stamp = sample_count * (SAMPLE_TIME_MS / 1000.0)
                        values.append((time_stamp, voltage_out))
                        sample_count += 1
                        buffer = buffer[3:]
                    else:
                        buffer = buffer[1:]

        send_control_command(ser, 0x06, output_type)  # Oprește citirea ADC

        # 7. Salvează datele în CSV
        test_number = get_next_test_number()
        os.makedirs("stepResponse/customRef", exist_ok=True)
        file_path = f"stepResponse/customRef/custom_ref_test_{test_number:03d}.csv"

        with open(file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time (s)", "Output Voltage (V)", "Reference (V)"])
            for t, v in values:
                writer.writerow([f"{t:.6f}", f"{v:.3f}", f"{voltage:.3f}"])

        print(f"Test saved to {file_path}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def perform_batch_step_response_test(voltage_values, timeout=2.0, port=SERIAL_PORT, baud_rate=BAUD_RATE):
    """Perform all step responses in one continuous session and save to a single CSV."""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Starting batch step response test on {port} at {baud_rate} baud...")

        test_number = get_next_test_number()
        print(f"Batch Test #{test_number:03d}")
        send_step_command(ser, 0xFFF)  # set the proces to 0
        time.sleep(2)
        test_start_time = time.time()
        all_values = []  # <-- aici salvezi toate valorile
        buffer = bytearray()

        # Convert voltage values to DAC codes
        test_values = [int((v / VOLTAGE_REF) * 0xFFF) for v in voltage_values]
        test_values = [min(max(val, 0), 0xFFF) for val in test_values]
        test_start_time = time.perf_counter()
        for voltage_val, value in zip(voltage_values, test_values):
            print(f"→ Step to {voltage_val:.3f} V (0x{value:03X}) for {timeout}s")
            send_control_command(ser, 0x02)  # Start ADC reading
            send_step_command(ser, value)   # Send step value

            sample_count = 0
            local_start = time.perf_counter()
            while (time.perf_counter() - local_start) < timeout:
                if ser.in_waiting > 0:
                    buffer.extend(ser.read(ser.in_waiting))
                    while len(buffer) >= 3:
                        if buffer[0] == 0x15:
                            #precise_time = sample_count * (SAMPLE_TIME_MS / 1000.0)
                            precise_time =  time.perf_counter() - test_start_time
                            msb = buffer[1]
                            lsb = buffer[2]
                            raw_value = (msb << 8) | lsb
                            voltage = (raw_value / ADC_RESOLUTION) * VOLTAGE_REF

                            all_values.append((precise_time, voltage, voltage_val))  # <--- salvăm global
                            sample_count += 1
                            buffer = buffer[3:]
                        else:
                            buffer = buffer[1:]

        send_control_command(ser, 0x03)  # Stop ADC after all steps

        # Save data
        save_path = f"stepResponse/batch_data_test_{test_number:03d}.csv"
        os.makedirs("stepResponse", exist_ok=True)
        with open(save_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (s)', 'Output Voltage (V)', 'Input Voltage (V)'])
            for t, v_o, v_i in all_values:
                writer.writerow([f"{t:.6f}", f"{v_o:.3f}", f"{v_i:.3f}"])

        print(f"✅ Batch step response test saved to: {save_path}")

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def main_menu():
    while True:
        print("\nADC Reading Menu")
        print("1. Perform step response test")
        print("2. Perform custom step response test")
        print("3. Perform custom timed step response test")
        print("4. Enable comntroller for custom reference")
        print("5. Perform step response test for custom values")

        print("7. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            # Get duration and time unit
            step_response_test()

        elif choice == '2':
            custom_voltages = [0.1, 1.2, 2.5, 3.3, VOLTAGE_REF]
            step_response_test_with_vector(custom_voltages)

        elif choice == '3':
            custom_voltages = [2.1,VOLTAGE_REF-0.1,2.1,0.1]
            step_response_test_timed(custom_voltages,2,10)
        elif choice == '4':
            custom_reference_test()
        elif choice == '5':
            custom_voltages = [2.1,2.19,2.3,1.95]
            perform_batch_step_response_test(custom_voltages,timeout=7.0)
        elif choice == '7':
            print("Exiting program...")
            break
        else:
            print("Invalid choice! Please enter 1, 2, 3, 4, 5, or 6.")


if __name__ == "__main__":
    main_menu()
