/*
 * CFile1.c
 *
 * Created: 4/2/2025 11:59:07 PM
 *  Author: simon
 */ 

#include <customCode/newCallBack.h>
#include <util/delay.h>

static uint16_t duty_cycle = 0x0;
static uint8_t          USART_0_rxbuf[USART_0_RX_BUFFER_SIZE];
static volatile uint8_t USART_0_rx_head;
static volatile uint8_t USART_0_rx_tail;
static volatile uint8_t USART_0_rx_elements;
static uint8_t          USART_0_txbuf[USART_0_TX_BUFFER_SIZE];
static volatile uint8_t USART_0_tx_head;
static volatile uint8_t USART_0_tx_tail;
static volatile uint8_t USART_0_tx_elements;


bool readComm = false;
bool spabEnable = false;
bool controllerEnable = false;
uint8_t dataOption = 0x0;
uint16_t stepVal = 0xD5;

volatile float *c,*e;

bool getReadComm()
{
	return readComm;
}
bool getEnableController()
{
	return controllerEnable;
}
float getStepVal()
{
	return (float)(stepVal/1023.0*5.0);
}
void resetControl()
{
	for(int i = 1; i < 3; i++)
	{
		c[i] = 0;
		e[i] = 0;
	}
}
uint8_t getDataOption()
{
	return dataOption;
}
void initCB()
{
	uint8_t x = 0;

	USART_0_rx_tail     = x;
	USART_0_rx_head     = x;
	USART_0_rx_elements = x;
	USART_0_tx_tail     = x;
	USART_0_tx_head     = x;
	USART_0_tx_elements = x;

	//for(int i = 0; i < 2; i++)
	//{
		//c[i] = 0;
		//e[i] = 0;
		////writeOneByte(0xB);
	//}
	resetControl();
	//resetAll();
}

void resetAll(void)
{
	uint8_t x = 0;

	USART_0_rx_tail     = x;
	USART_0_rx_head     = x;
	USART_0_rx_elements = x;
	USART_0_tx_tail     = x;
	USART_0_tx_head     = x;
	USART_0_tx_elements = x;
}
void resetRxCB(void)
{
	uint8_t x = 0;

	USART_0_rx_tail     = x;
	USART_0_rx_head     = x;
	USART_0_rx_elements = x;
}
void errorGenerator(uint8_t index, uint8_t value)
{
	switch (index)
	{
		case 1:
		writeOneByte(0x22);
		writeOneByte(value);
		break;

		case 2:
		writeOneByte(0x23);
		writeOneByte(value);
		break;

		case 3:
		writeOneByte(0x24);
		writeOneByte(value);
		break;

		default:
		// Optional: Handle unexpected index values
		writeOneByte(0xFF); // Indicating an unknown error
		writeOneByte(index);
		break;
	}
}

void testHeader()
{
	if (USART_0_rxbuf[1] == 0x15)
	{
		
			switch (USART_0_rxbuf[2])
			{
				case 0x2:
					readComm = true;
					controllerEnable = false;

					//resetControl();
					
					PORTF_set_pin_level(2,true);
					resetAll();
					
						
						//writeonebyte(0xb);
					
					//resetControl();
					//writeOneByte(0xAA);
				break;

				case 0x3:
					readComm = false;
					PORTF_set_pin_level(2,false);
					//resetControl();
					
					resetAll();
					
					//writeOneByte(0xBB);
					
				break;
					
				case 0x4:
					_delay_ms(100);
					writeOneByte(0x16);
					writeOneByte(duty_cycle>>8);
					writeOneByte(duty_cycle);
				break;

				case 0x5:
					controllerEnable = true;
					readComm = false;
					if(USART_0_rxbuf[3] > 0x2)
						errorGenerator(3,USART_0_rxbuf[3]);
					else
						dataOption = USART_0_rxbuf[3];
					resetAll();
					//resetControl();
				break;
				case 0x6:
					controllerEnable = false;
					
					PORTF_set_pin_level(2,false);
					//resetControl();
					resetAll();
				break;
				default:
				errorGenerator(2, USART_0_rxbuf[2]);
				readComm = false;
				break;
			}
			//writeOneByte(0XB);
		
	}
	else if(USART_0_rxbuf[1] == 0x14)
	{
		PWM_0_load_duty_cycle_ch0(USART_0_rxbuf[2]<<8|USART_0_rxbuf[3]);
		duty_cycle = USART_0_rxbuf[2]<<8|USART_0_rxbuf[3];
	}
	else if(USART_0_rxbuf[1] == 0x13)
	{
		stepVal = USART_0_rxbuf[2]<<8|USART_0_rxbuf[3];
		writeOneByte(0x14);
	}
	else
	{
		errorGenerator(1, USART_0_rxbuf[1]);
		readComm = false;
	}
	


}
void newCbTx(void)
{
	uint8_t tmptail;

	/* Check if all data is transmitted */
	if (USART_0_tx_elements != 0) {
		/* Calculate buffer index */
		tmptail = (USART_0_tx_tail + 1) & USART_0_TX_BUFFER_MASK;
		/* Store new index */
		USART_0_tx_tail = tmptail;
		/* Start transmission */
		USART0.TXDATAL = USART_0_txbuf[tmptail];
		USART_0_tx_elements--;
	}

	if (USART_0_tx_elements == 0) {
		/* Disable UDRE interrupt */
		USART0.CTRLA &= ~(1 << USART_DREIE_bp);
	}
}
void newCbRx(void)
{
	
	uint8_t data;
	uint8_t tmphead;

	/* Read the received data */
	data = USART0.RXDATAL;
	/* Calculate buffer index */
	tmphead = (USART_0_rx_head + 1) & USART_0_RX_BUFFER_MASK;

	if (tmphead == USART_0_rx_tail) {
		/* ERROR! Receive buffer overflow */
		} else {
		/* Store new index */
		USART_0_rx_head = tmphead;

		/* Store received data in buffer */
		USART_0_rxbuf[tmphead] = data;
		USART_0_rx_elements++;
	}
	//readComm = false;
	//writeOneByte(data);
	if(USART_0_rx_elements == 3)
	{
		//writeOneByte(0xB);
		//USART0.CTRLB &= ~(USART_TXEN_bm); // disable tx
		testHeader(USART_0_rxbuf);
		//USART_0_enable_tx();
		resetRxCB();
	}
		
		
	
}
void writeOneByte(const uint8_t data)
{
	uint8_t tmphead;

	/* Calculate buffer index */
	tmphead = (USART_0_tx_head + 1) & USART_0_TX_BUFFER_MASK;
	/* Wait for free space in buffer */
	while (USART_0_tx_elements == USART_0_TX_BUFFER_SIZE)
	;
	/* Store data in buffer */
	USART_0_txbuf[tmphead] = data;
	/* Store new index */
	USART_0_tx_head = tmphead;
	ENTER_CRITICAL(W);
	USART_0_tx_elements++;
	EXIT_CRITICAL(W);
	/* Enable UDRE interrupt */
	USART0.CTRLA |= (1 << USART_DREIE_bp);
}
void drive_slave_select_high_custom(void)
{
	PORTA_set_pin_level(7,true);
}
void drive_slave_select_low_custom(void)
{
	PORTA_set_pin_level(7,false);
}

