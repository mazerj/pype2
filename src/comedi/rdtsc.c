#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>

#define RDTSC(x) __asm__ __volatile__ ( ".byte 0x0f,0x31" \
			:"=a" (((unsigned long*)&x)[0]), \
			"=d" (((unsigned long*)&x)[1]))

static unsigned long long ticks_per_ms = 0;

static double find_clockfreq()	/* get clock frequency in mHz */
{
  FILE *fp;
  char buf[100];
  double mhz;

  if ((fp = fopen("/proc/cpuinfo", "r")) == NULL) {
    fprintf(stderr, "Can't open /proc/cpuinfo\n");
    exit(1);
  }
  mhz = -1.0;
  while (fgets(buf, sizeof(buf), fp) != NULL) {
    if (sscanf(buf, "cpu MHz         : %lf", &mhz) == 1) {
      break;
    }
  }
  return(mhz * 1.0e6);
}

static unsigned long timestamp(int init)
{
  static unsigned long long timezero;
  unsigned long long now;

  RDTSC(now);
  if (init) {
    timezero = now;
    return(0);
  } else {
    return((unsigned long)((now - timezero) / ticks_per_ms));
  }
}

main()
{
  double mhz;

  ticks_per_ms = (unsigned long long)(0.5 +
				      ((mhz = find_clockfreq()) / 1000.0));

  printf("clock=%f mhz\n", mhz);

  timestamp(1);
  sleep(10);
  printf("ts=%d\n", timestamp(0));
  sleep(1);
  printf("ts=%d\n", timestamp(0));
}

