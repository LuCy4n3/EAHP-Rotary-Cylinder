/*
 * CallbackFun.c
 *
 * Created: 12/20/2024 4:45:31 AM
 *  Author: simon
 */ 
#include "../CallbackFun.h"


static uint8_t          USART_RADIO_rxbuf[USART_RADIO_RX_BUFFER_SIZE];
static volatile uint8_t USART_RADIO_rx_head;
static volatile uint8_t USART_RADIO_rx_tail;
static volatile uint8_t USART_RADIO_rx_elements;
static uint8_t          USART_RADIO_txbuf[USART_RADIO_TX_BUFFER_SIZE];
static volatile uint8_t USART_RADIO_tx_head;
static volatile uint8_t USART_RADIO_tx_tail;
static volatile uint8_t USART_RADIO_tx_elements;

void initCB(void)
{
	uint8_t x = 0;

	USART_RADIO_rx_tail     = x;
	USART_RADIO_rx_head     = x;
	USART_RADIO_rx_elements = x;
	USART_RADIO_tx_tail     = x;
	USART_RADIO_tx_head     = x;
	USART_RADIO_tx_elements = x;
}
void resetRxCB(void)
{
	uint8_t x = 0;

	USART_RADIO_rx_tail     = x;
	USART_RADIO_rx_head     = x;
	USART_RADIO_rx_elements = x;
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
	if (USART_RADIO_rxbuf[1] == 0x15)
	{
		if (USART_RADIO_rxbuf[2] == 0x3)
		{
			switch (USART_RADIO_rxbuf[3])
			{
				case 0x2:
				writeOneByte(PORTA_get_pin_level(1) == true ? 0x0 : 0xFF);
				break;

				case 0x3:
				PORTA_set_pin_level(1, USART_RADIO_rxbuf[4] == 0x1 ? true : false);
				break;

				case 0x4:
				PWM_0_load_duty_cycle_ch0(USART_RADIO_rxbuf[4] << 8 | USART_RADIO_rxbuf[4]);
				break;

				case 0x5:
				PWM_LED_load_duty_cycle_ch0(USART_RADIO_rxbuf[4] << 8 | USART_RADIO_rxbuf[4]);
				break;

				default:
				errorGenerator(3, USART_RADIO_rxbuf[3]);
				break;
			}
		}
		else
		{
			errorGenerator(2, USART_RADIO_rxbuf[2]);
		}
	}
	else
	{
		errorGenerator(1, USART_RADIO_rxbuf[1]);
	}


}
void newCbTx(void)
{
	uint8_t tmptail;

	/* Check if all data is transmitted */
	if (USART_RADIO_tx_elements != 0) {
		/* Calculate buffer index */
		tmptail = (USART_RADIO_tx_tail + 1) & USART_RADIO_TX_BUFFER_MASK;
		/* Store new index */
		USART_RADIO_tx_tail = tmptail;
		/* Start transmission */
		USART2.TXDATAL = USART_RADIO_txbuf[tmptail];
		USART_RADIO_tx_elements--;
	}

	if (USART_RADIO_tx_elements == 0) {
		/* Disable UDRE interrupt */
		USART2.CTRLA &= ~(1 << USART_DREIE_bp);
	}
}
void newCbRx(void)
{
	{
		uint8_t data;
		uint8_t tmphead;

		/* Read the received data */
		data = USART2.RXDATAL;
		/* Calculate buffer index */
		tmphead = (USART_RADIO_rx_head + 1) & USART_RADIO_RX_BUFFER_MASK;

		 
		/* Store new index */
		USART_RADIO_rx_head = tmphead;

		/* Store received data in buffer */
		USART_RADIO_rxbuf[tmphead] = data;
		
		
		
		USART_RADIO_rx_elements++;
		if(USART_RADIO_rx_elements == 4)
		{
			
			testHeader(USART_RADIO_rxbuf);
			
			resetRxCB();
		}
		
		
	}
}
void writeOneByte(const uint8_t data)
{
	uint8_t tmphead;

	/* Calculate buffer index */
	tmphead = (USART_RADIO_tx_head + 1) & USART_RADIO_TX_BUFFER_MASK;
	/* Wait for free space in buffer */
	while (USART_RADIO_tx_elements == USART_RADIO_TX_BUFFER_SIZE)
	;
	/* Store data in buffer */
	USART_RADIO_txbuf[tmphead] = data;
	/* Store new index */
	USART_RADIO_tx_head = tmphead;
	ENTER_CRITICAL(W);
	USART_RADIO_tx_elements++;
	EXIT_CRITICAL(W);
	/* Enable UDRE interrupt */
	USART2.CTRLA |= (1 << USART_DREIE_bp);
	//PWM_LED_load_duty_cycle_ch0(0x0);
}
void drive_slave_select_high_custom(void)
{
	PORTA_set_pin_level(7,true);
}
void drive_slave_select_low_custom(void)
{
	PORTA_set_pin_level(7,false);
}
