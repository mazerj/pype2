/* title:   das16_server.c

** author:  jamie mazer
** created: Wed Aug 14 14:45:27 2002 mazer 
** info:    test program for das16 card
** history:
**
*/

#include <sys/types.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/mman.h>
#include <sys/io.h>
#include <signal.h>

#include "sigs.h"

#include "das16.h"

static char *progname = NULL;
static int dbase = 0x260;


static int ad_in(int chan)
{
  int lo, hi, i;

  /* select desired channel */
  outb(chan + (chan << 4), dbase+Channel_Mux);
    
  /* trigger conversion */
  outb(0x00, dbase+ADC_Low);
  
  /* wait for converter to be free.. this is kludge */
  for (i = 0; i < 100; i++) {
    if ((inb(dbase+Status) & 0x80) == 0) {
      break;
    }
  }
  
  /* get converted value */
  lo = inb(dbase+ADC_Low);
  hi = inb(dbase+ADC_High);
  
  /* converts 12bit unsigned # to 12bit signed */
  return((((lo&0xf0) >> 4) | (hi << 4)) - 2048);
}

static void raw_ad_in(int chan, int *lo, int *hi)
{
  int i;

  /* select desired channel */
  outb(chan + (chan << 4), dbase+Channel_Mux);
    
  /* trigger conversion */
  outb(0x00, dbase+ADC_Low);
  
  /* wait for converter to be free.. this is kludge */
  for (i = 0; i < 100; i++) {
    if ((inb(dbase+Status) & 0x80) == 0) {
      break;
    }
  }
  
  /* get converted value */
  *lo = inb(dbase+ADC_Low);
  *hi = inb(dbase+ADC_High);
}

static int init()
{
  /* first get access to IO ports -- this requires root perms */
  if (iopl(3) != 0) {
    perror2("iopl", __FILE__, __LINE__);
    fprintf(stderr, "%s: warning no port access -- using dummy mode\n",
	    progname);
    exit(1);
  } else {
    /* setup for simple polling input on 4 channels */
    outb(0x00, dbase+Pacer_Control);
    outb(0x00, dbase+Status);
    outb(0x00, dbase+Control);
    
    /* set max input gain..
       code	das1601/12	das1602/12
       0	+- 10v		+- 10v
       1	+- 1v		+- 5v
       2	+- 0.1v		+- 2.5v
       3	+- 0.01v	+- 1.25v
    */
    outb(0x02, dbase+Gain_Control);
  }
  return(1);
}

static unsigned long timestamp(int init)
{
  struct timeval now, delta;
  struct timezone tz;
  static struct timeval first;

  if (init) {
    gettimeofday(&first, &tz);

    return(0);
  } else {
    gettimeofday(&now, &tz);
    timersub(&now, &first, &delta);

    return((long)(1 + ((1000 * delta.tv_sec) + delta.tv_usec/1000)));
  }
}

static void perror2(char *s, char *file, int line)
{
  char p[1000];

  sprintf(p, "ERROR (file=%s, line=%d):%s", file, line, s);
  perror(p);
}

int main(int ac, char **av)
{
  int n;
  int lo, hi;

  init();
  while (1) {
    for (n = 0; n < 2; n++) {
      raw_ad_in(n, &lo, &hi);
      printf("0x%02x 0x%02x   ", hi, lo);
      //printf("%10d ", ad_in(n));
    }
    printf("\n");
  }

  exit(0);
}


