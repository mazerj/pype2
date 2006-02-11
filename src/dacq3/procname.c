/*
** src: http://lightconsulting.com/~thalakan/process-title-notes.html
**   (which originally came from the proftpd sources, apparently)
**
**
*/

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdarg.h>
#include <malloc.h>

#include "procname.h"

/* Globals */
static char **Argv = ((void *)0);
extern char *__progname, *__progname_full;
static char *LastArgv = ((void *)0);

/* example
int main(int argc, char *argv[], char *envp[]) {
  init_set_proc_title(argc, argv, envp);
  set_proc_title("%s", "This is a nifty process title");
  printf("DEBUG: %s\n", Argv[0]);
  
  for(;;) {}
  return 0;
}
*/

void init_set_proc_title(int argc, char *argv[], char *envp[])
{
  int i, envpsize;
  extern char **environ;
  char **p;

  for(i = envpsize = 0; envp[i] != NULL; i++)
    envpsize += strlen(envp[i]) + 1;
  
  if((p = (char **) malloc((i + 1) * sizeof(char *))) != NULL ) {
    environ = p;

    for(i = 0; envp[i] != NULL; i++) {
      if((environ[i] = malloc(strlen(envp[i]) + 1)) != NULL)
	strcpy(environ[i], envp[i]);
    }
    
    environ[i] = NULL;
  }

  Argv = argv;
  
  for(i = 0; envp[i] != NULL; i++) {
    if((LastArgv + 1) == envp[i]) // Not sure if this conditional is needed
      LastArgv = envp[i] + strlen(envp[i]);
  }

  // Pretty sure you don't need this either
  // __progname = strdup("proftpd");
  //__progname_full = strdup(argv[0]);
}

void set_proc_title(char *fmt,...)
{
  va_list msg;
  static char statbuf[8192];
  char *p;
  int i,maxlen = (LastArgv - Argv[0]) - 2;

  //printf("DEBUG: maxlen: %i\n", maxlen);

  va_start(msg,fmt);

  memset(statbuf, 0, sizeof(statbuf));
  vsnprintf(statbuf, sizeof(statbuf), fmt, msg);

  va_end(msg);

  i = strlen(statbuf);

  snprintf(Argv[0], maxlen, "%s", statbuf);
  p = &Argv[0][i];
  
  while(p < LastArgv)
    *p++ = '\0';
  Argv[1] = ((void *)0) ;
}
