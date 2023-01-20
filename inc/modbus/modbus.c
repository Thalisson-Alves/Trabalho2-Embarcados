#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  //Usado para a UART
#include <fcntl.h>   //Usado para a UART
#include <termios.h> //Usado para a UART
#include <string.h>
#include "crc.h"

#define READ_CODE 0x23
#define SEND_CODE 0x16

#define INTERNAL_TEMP 0xc1
#define REFERENCE_TEMP 0xc2
#define REQUEST_COMMAND 0xc3
#define SEND_INT 0xd1
#define SEND_FLOAT 0xd2
#define SEND_SYS_STATE 0xd3
#define SEND_CONTROL_MODE 0xd4
#define SEND_FUNC_STATE 0xd5
#define SEND_AMB_TEMPO 0xd6

int uart_fp;

void uart_init()
{
    uart_fp = open("/dev/serial0", O_RDWR | O_NOCTTY | O_NDELAY);
    if (uart_fp == -1)
    {
        printf("Erro - Porta Serial nao pode ser aberta. Confirme se não está sendo usada por outra aplicação.\n");
        exit(-1);
    }

    struct termios options;
    tcgetattr(uart_fp, &options);
    options.c_cflag = B115200 | CS8 | CLOCAL | CREAD;
    options.c_iflag = IGNPAR;
    options.c_oflag = 0;
    options.c_lflag = 0;
    tcflush(uart_fp, TCIFLUSH);
    tcsetattr(uart_fp, TCSANOW, &options);
}

int uart_send(unsigned char command, void *buf, int buf_size, void *out_buf)
{
    unsigned char buffer[9 + buf_size + 1];
    unsigned buffer_size = 0;
    buffer[buffer_size++] = 0x01;
    buffer[buffer_size++] = (command < 0xd0 ? READ_CODE : SEND_CODE);
    buffer[buffer_size++] = command;
    buffer[buffer_size++] = 7;
    buffer[buffer_size++] = 4;
    buffer[buffer_size++] = 0;
    buffer[buffer_size++] = 1;

    for (int i = 0; i < buf_size; i++)
        buffer[buffer_size++] = ((unsigned char*)buf)[i];

    int crc = calcula_CRC(buffer, buffer_size);
    memcpy(buffer + buffer_size, (void *) &crc, sizeof(short));
    buffer_size += sizeof(short);

    for (int i = 0; i < buffer_size; i++)
        printf("%d%c", buffer[i], " \n"[i + 1 == buffer_size]);

    // if (write(uart0_filestream, &tx_buffer[0], (p_tx_buffer - &tx_buffer[0])) < 0)
    //     return -1;

    // sleep(.5);

    // unsigned char rx_buffer[256];
    // int rx_size = read(uart_fp, (void *)rx_buffer, 255);
    // if (rx_size <= 0)
    //     return -1;

    // for (int i = 0; i < rx_size; i++)
    //     printf("%d%c", rx_buffer[i], " \n"[i == rx_size - 1]);

    // // TODO: interprete response
    // if (calcula_CRC(rx_buffer, rx_size - 2) != *((short *)(rx_buffer + rx_size - 2)))
    //     return -1;

    // if (rx_size > 5)
    //     memcpy(out_buf, rx_buffer + 3, rx_size - 5);

    return 0;
}

// int main(int argc, char **argv)
// {
//     // uart_init();
//     int x = 42;
//     uart_send(SEND_INT, (void *)&x, sizeof(int));

//     return 0;
// }
