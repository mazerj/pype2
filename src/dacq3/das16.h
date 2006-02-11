/* title:   das16.h

** author:  jamie mazer
** created: Mon Mar  4 16:41:26 2002 mazer 
** info:    ports on das160x board
** history:
**
*/


/* Definititions for DAS-1602 ports (from ComputerBoards Manual)
*/

#define	ADLOW	0x00
#define	ADHIGH	0x01
#define	MUX	0x02
#define	DIGIO	0x03
#define	DA0LOW	0x04
#define	DA0HIGH	0x05
#define	DA1LOW	0x06
#define	DA1HIGH	0x07
#define	STATUS	0x08
#define	DMA	0x09
#define	BURST	0x0a
#define	GAIN	0x0b
#define	CTR0	0x0c
#define	CTR1	0x0d
#define	CTR2	0x0e
#define	PACER	0x0f


/* Definititions for DAS-1602 ports (from COMEDI driver)
*/

#define ADC_Low         0x000	/* ADC-Low register */
#define ADC_High        0x001	/* ADC-High register */
#define Channel_Mux     0x002	/* Channel MUX register */
#define Digital_4_Bit   0x003	/* 4-bit digital in/out */
#define DA0_Low         0x004	/* DA0-Low register */
#define DA0_High        0x005	/* DA0-High register */
#define DA1_Low         0x006	/* DA1-Low register */
#define DA1_High        0x007	/* DA1-High register */
#define Status          0x008	/* Status register */
#define Control         0x009	/* DMA, interrupt and trigger control */
#define Pacer_Control   0x00a	/* Pacer clock control */
#define Gain_Control    0x00b	/* Gain control */
#define Counter_0       0x00c	/* 8254 counter 0 data */
#define Counter_1       0x00d	/* 8254 counter 1 data */
#define Counter_2       0x00e	/* 8254 counter 2 data */
#define Counter_Control 0x00f	/* 8254 counter control */
#define Port_A          0x400	/* 8255 port A */
#define Port_B          0x401	/* 8255 port B */
#define Port_C          0x402	/* 8255 port C */
#define Control_8255    0x403	/* 8255 control */
#define Convert_Disable 0x404	/* Disable AD conversion */
#define Mode_Enable     0x405	/* Enable DAS1600 mode */
#define Burst_Enable    0x406	/* Enable burst mode */
#define Burst_Status    0x407	/* Burst mode status */
