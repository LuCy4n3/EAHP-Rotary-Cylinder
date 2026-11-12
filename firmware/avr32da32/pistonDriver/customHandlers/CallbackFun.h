/*
 * CallbackFun.h
 *
 * Created: 12/20/2024 4:43:00 AM
 *  Author: simon
 */ 


#ifndef CALLBACKFUN_H_
#define CALLBACKFUN_H_
#include <atmel_start.h>
#include <compiler.h>
#include <clock_config.h>
#include <usart_basic.h>
#include <atomic.h>


void initCB(void);

void newCbTx(void);

void newCbRx(void);

void writeOneByte(const uint8_t data);

void drive_slave_select_high_custom(void);

void drive_slave_select_low_custom(void);



#endif /* CALLBACKFUN_H_ */