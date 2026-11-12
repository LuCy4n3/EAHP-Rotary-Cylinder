# EAHP: Rotary Cylinder and Electronic Simulation

Project files for identifying a semi-rotary pneumatic cylinder driven by a
proportional valve, reproducing its behavior with an op-amp circuit, and
controlling the electronic simulation with an AVR32DA32 board.

[Read the project report](report/ProiectEAHP.pdf).

## Contents

| Path | Contents |
| --- | --- |
| `report/ProiectEAHP.pdf` | Original project report. |
| `simulation/eahpSIM.slx` | Final Simulink model corresponding to the report's diagram. |
| `simulation/init_simulation.m` | Standalone transfer-function setup extracted from the project script. |
| `simulation/run_simulation.m` | Initialize and simulate the final model. |
| `analysis/proiect.m` | Original analysis sections with only machine/data paths made repository-relative. |
| `analysis/control.slx` | Earlier identification/controller trial model. |
| `data/stepResponse/` | The 14 measurement CSV files loaded by active analysis statements. |
| `firmware/avr32da32/` | AVR32DA32 control firmware and the driver/configuration sources required to build it. |
| `firmware/position_display/` | Arduino output-sequencing/position-display sketch. |
| `tools/finalCode.py` | Serial data-acquisition and reference/control test menu. |
| `figures/` | Supplied project diagrams, plots and illustrations. |
| `measurements/` | Working directory for new local hardware recordings. |

This is a focused copy of the rotary-cylinder work. The separate `lab6` hydraulic
exercise, BLDC notebook, Python environment, IDE state, caches, build outputs and
synthetic identification draft are not included. Original source folders remain
unchanged outside this repository. Bundled generated MCU drivers retain their
original vendor notices.

## Run the final simulation

Use MATLAB with Simulink and Control System Toolbox. From the repository root:

```matlab
run(fullfile('simulation', 'run_simulation.m'));
```

The script creates `h_integrator` and `h_filtru`, loads the original model and runs
it. The result is available as `simulation_result`. No hardware is accessed.
To inspect the diagram interactively after setup:

```matlab
open_system('eahpSIM');
```

The saved model uses proportional gain 2.5 and saturation. The setup preserves the
original analysis values: R1/R2 = 4.7 kOhm, integrator C1 = 10 uF and filter C2 =
1 uF. The report states 10 uF for the filter. Change the explicitly labeled C2
value only when comparing that report variant. No sign, gain or saturation was
silently retuned to reconcile the report and implementation.

## Analysis and recorded results

`analysis/proiect.m` remains a section-based MATLAB working script. It includes
identification, validation, control calculations and the recorded reference-test
plots. Run selected sections in order; it is not the simulation startup script,
and some exploratory sections depend on variables from earlier workspace work.
Identification sections also require System Identification Toolbox.

Data paths now resolve through this repository's `data/` directory. Existing
measurements are preserved byte-for-byte. The retained datasets include the
identification/validation runs 118 and 119, the controller/process reference
tests used for the report plots, and the electronic-process batch recording 211.

`analysis/control.slx` is an earlier trial using workspace `numerator`,
`denominator` and `hc`; initialize its matching analysis section before opening
or running that model.

## AVR32DA32 firmware and Arduino display

Open `firmware/avr32da32/pistonDriver.atsln` in Atmel/Microchip Studio with the
AVR32DA32 device support installed. The firmware retains the controller and UART
implementation used in the source project. Build and verify the target/pin setup
before flashing through the board's intended programming interface.

Open the sketch under `firmware/position_display/cilindruPneumaticCod/` with the
Arduino toolchain for the position-display hardware described in the report.

## Python acquisition

From this repository directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Push-Location measurements
..\.venv\Scripts\python.exe ..\tools\finalCode.py
Pop-Location
```

The supplied utility currently uses COM4, 230400 baud, a 4.8 V conversion reference,
a 10-bit ADC scale and a 12-bit command scale. Review these against the connected
firmware and actual circuit before selecting a menu action. The utility can send
control/reference commands; no acquisition or flashing is performed by repository
setup.
