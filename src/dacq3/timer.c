#include <stdio.h>
#include <malloc.h>
#include <math.h>
#include <sys/time.h>

#include "timer.h"


void *timer_start(void)
{
  struct timeval *now;
  struct timezone tz;

  now = (struct timeval *)calloc(sizeof(struct timeval), 1);
  gettimeofday(now, &tz);
  return((void *)now);
}

void timer_clear(void *v)
{
  free(v);
}

double timer_us_elapsed(void *v)
{
  struct timeval *pstart = (struct timeval *)v;
  struct timeval now, delta;
  struct timezone tz;
  double us;

  gettimeofday(&now, &tz);
  timersub(&now, pstart, &delta);
  us = (1.0e6 * (double)delta.tv_sec) + (double)delta.tv_usec;
  return(us);
}


int timer_ms_elapsed(void *v)
{
  struct timeval *pstart = (struct timeval *)v;
  struct timeval now, delta;
  struct timezone tz;
  int ms;

  gettimeofday(&now, &tz);
  timersub(&now, pstart, &delta);
  ms = (1000 * delta.tv_sec) + delta.tv_usec / 1000;
  return(ms);
}

