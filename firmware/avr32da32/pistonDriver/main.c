#include <atmel_start.h>
#include <util/delay.h>
#include <customCode/newCallBack.h>

#define MAX_CONTROL 4.0 

volatile adc_result_t ADC_0_measurement;
volatile uint8_t      ADC_0_measurement_normalized;

volatile float c[3] = {0.0, 0.0 , 0.0};
volatile float e[3] = {0.0,  0.0 , 0.0};
volatile float realValue = 0;
volatile float control_voltage;
bool prev = true;
float abs_float(float nmb)
{
	return nmb >= 0 ? 1:-1;
}
int getFirst4digits(float f1)
{
	int16_t number=0;
	uint16_t powerOf10=1;
	for(int i = 1;i<= 4;i++)
	{
		powerOf10*=10;
		//printf("%d\n",number);
		number = number*10 + ((int)(f1*powerOf10))%10;
	}
	return number;
}
uint16_t getCommandOfControllerHP(float value)
{
	return ((uint16_t)(value*0xFFF/4.8));
}
void serialPrint(uint8_t* data)
{
	uint8_t idx = 0;
	while(data[idx]!=0)
	{
		writeOneByte(data[idx]);
		idx++;
	}
}
void startup()
{
	
	//writeOneByte(0xB);
	PORTF_set_pin_dir(2,PORT_DIR_OUT);
	PORTF_set_pin_level(2,true);
	_delay_ms(100);
	PORTF_set_pin_level(2,false);
	_delay_ms(100);
	PORTF_set_pin_level(2,true);
	_delay_ms(100);
	PORTF_set_pin_level(2,false);
	_delay_ms(100);
	PORTF_set_pin_level(2,true);
	_delay_ms(100);
	PORTF_set_pin_level(2,false);
	_delay_ms(100);
	PORTF_set_pin_level(2,true);
	_delay_ms(100);
	PORTF_set_pin_level(2,false);
	_delay_ms(100);
	PORTF_set_pin_level(2,true);
	_delay_ms(100);
	PORTF_set_pin_level(2,false);
	_delay_ms(100);
	PORTF_set_pin_level(2,true);
	_delay_ms(100);
	PORTF_set_pin_level(2,false);
	_delay_ms(100);	
	
}
int main(void)
{
	/* Initializes MCU, drivers and middleware */
	atmel_start_init();
	ADC_0_enable();
	//DAC_0_init();
	//DAC_0_enable();
	//DAC_0_set_output(DAC_0_get_resolution() / 2);
	PWM_0_enable();
	PWM_0_enable_output_ch0();

	// Set channel 0 duty cycle value register value to specified value
	PWM_0_load_duty_cycle_ch0(0x3f);

	// Set counter register value
	PWM_0_load_counter(0);
	USART_0_enable();
	USART_0_enable_rx();
	USART_0_enable_tx();
	initCB();
	USART_0_set_ISR_cb(&newCbTx,UDRE_CB);
	USART_0_set_ISR_cb(&newCbRx,RX_CB);
	
	
	PWM_0_load_duty_cycle_ch0(0x0);
	
	startup();
	/* Replace with your application code */
	while (1) {
		if(getReadComm())	
		{
			// REF E 4.8????
			ADC_0_measurement = ADC_0_get_conversion(17);

			// Get 8 MSB of conversion result
			//ADC_0_measurement_normalized = ADC_0_measurement >> (ADC_0_get_resolution() - 8);
			writeOneByte(0x15);
			writeOneByte(ADC_0_measurement>>8);
			writeOneByte(ADC_0_measurement);

			
		}else if(getEnableController())
		{
			if(prev)
			{
				for (uint8_t i = 2; i > 0;i--)
				{
					c[i] = 0;
					e[i] = 0;
				}
				prev = false;
			}
			PORTF_toggle_pin_level(2);
			ADC_0_measurement = ADC_0_get_conversion(17);
			realValue = (float)(ADC_0_measurement/1023.0)*4.6;
			e[0] = (float)(getStepVal() - realValue);
			writeOneByte(0xB);
			int aux = getFirst4digits(e[0]);
			//writeOneByte((int)e[0]/1.0);
			//writeOneByte((int)e[0]/1.0);
			//writeOneByte(aux>>8);
			//writeOneByte(aux);
			// Insert below the calculated discrete control function
			control_voltage = 0;
			
			
			c[0] = e[0]*2.5; // calculam comanda conform regulator gasit cu rltool
			
			if(c[0] > 2)
				c[0] = 2;
			else if(c[0] < -2) // saturatie comanda (am ales 2.2 pemtru erori de aparatura aka nu am 5v pe placuta)
				c[0] = -2;
			
			if(c[0] < 0) // inversam din cauza ca simularea e pe invers
				control_voltage = 2.1;
			else						// comanda con form circuitului care simuleaza valva prop, are "ref" la 2.1V(gnd) si if ul asta ia in considerare daca comanda e poz sau neg, adica peste 2.1V sau sub
				control_voltage = 0;
			control_voltage = 2.1;

			uint16_t duty = (uint16_t)(((-1*c[0]+control_voltage) * 0xFFF) / 5); // adaug la comanda offset ul in fucntie de comanda 
			
			

			// Convert voltage to duty cycle
			
			if(duty>0xFFF)
				duty = 0xFFF;
			PWM_0_load_duty_cycle_ch0(duty);
			
			switch(getDataOption())
			{
				case 0x0:
					writeOneByte(duty>>8);
					writeOneByte(duty);
					break;
				case 0x1:
					writeOneByte(ADC_0_measurement>>8);
					writeOneByte(ADC_0_measurement);
					break;
				case 0x2:
					writeOneByte(ADC_0_measurement>>8); // art trebui sa am eroarea aici, dar nu am reusit sa implementez inca 
					writeOneByte(ADC_0_measurement);
					break;
				default:
					writeOneByte(duty>>8);
					writeOneByte(duty);
					break;
			}
			

			for (int i = 2; i > 0; i--) {
				
				c[i] = c[i - 1];
				//writeOneByte(0xA);
				e[i] = e[i - 1];
				
			}
			//writeOneByte(0xA);
		}
		else 
			prev = true;
		
		
		_delay_ms(2); // 50 good
		//writeOneByte(0xB);
		
		

	
	}
	
}
