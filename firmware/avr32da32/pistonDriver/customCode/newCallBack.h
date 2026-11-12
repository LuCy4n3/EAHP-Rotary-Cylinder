/*
 * newCallBack.h
 *
 * Created: 4/2/2025 11:58:26 PM
 *  Author: simon
 */ 


#ifndef NEWCALLBACK_H_
#define NEWCALLBACK_H_

#include <atmel_start.h>
#include <compiler.h>
#include <clock_config.h>
#include <include/usart_basic.h>
#include <atomic.h>


void initCB();

void newCbTx(void);

void newCbRx(void);

void writeOneByte(const uint8_t data);

void drive_slave_select_high_custom(void);

void drive_slave_select_low_custom(void);

bool getReadComm();

bool getEnableController();

uint8_t getDataOption();

float getStepVal();







#endif /* NEWCALLBACK_H_ */