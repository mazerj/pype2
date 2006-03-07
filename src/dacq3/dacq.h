/* title:   dacq.h
** author:  jamie mazer
** created: Wed Jan  6 23:14:57 1999 mazer 
** info:    generic dacq interface structure
** history:
**
** Wed Jan  6 23:15:08 1999 mazer 
**   This is a generalized version of the original das_server.h
**   file.  The idea is to encapsulate a more general purpose
**   driver abstraction, not so directly tied to the das1600's
**   capabilities.  New devices will be able to use the same
**   interface.
**
** Sun Dec 16 16:27:10 2001 mazer 
**   added pp_XXXX functions to access a parallel port device..
**
** Tue Feb 19 13:08:43 2002 mazer 
**   added [xy]pow to dacq_eye_params()
**
** Sun Mar  9 13:25:58 2003 mazer 
**   added dacq_bar_transitions(int reset)
**
** Mon Mar 10 12:19:07 2003 mazer 
**   added dacq_bar_genint(int b) -- if you set this, then
**   each bar transition will generate a SIGUSR1 interuprt that
**   must be caught and handled..
*/

extern int dacq_start(int boot, int testmode, char *tracker_type,
		      char *dacq_server, char *arg1, char *arg2);
extern void dacq_stop(void);
extern int dacq_release(void);

extern int dacq_dig_in(int n);
extern void dacq_dig_out(int n, int val);

extern int dacq_eye_x(void);
extern int dacq_eye_y(void);

extern int dacq_eye_params(float xgain, float ygain,
			   int xoff, int yoff);
extern int dacq_eye_read(int which);


extern int dacq_ad_n(int n);
extern unsigned long dacq_ts(void);

extern int dacq_bar(void);
extern int dacq_bar_transitions(int reset);
extern int dacq_bar_genint(int b);

extern int dacq_sw1(void);
extern int dacq_sw2(void);
extern void dacq_juice(int on);
extern int dacq_juice_drip(int ms);

extern void dacq_fixbreak_tau(int n);
extern int dacq_fixwin(int n, int cx, int cy, int radius, float vbias);
extern int dacq_fixwin_genint(int n, int b);
extern int dacq_fixwin_reset(int n);
extern int dacq_fixwin_state(int n);
extern int dacq_fixwin_broke(int n);
extern long dacq_fixwin_break_time(int n);

extern int dacq_adbuf_toggle(int on);
extern void dacq_adbuf_clear();

extern int dacq_adbuf_size();
extern unsigned long dacq_adbuf_t(int ix);
extern int dacq_adbuf_x(int ix);
extern int dacq_adbuf_y(int ix);
extern int dacq_adbuf_pa(int ix);
extern int dacq_adbuf_c0(int ix);
extern int dacq_adbuf_c1(int ix);
extern int dacq_adbuf_c2(int ix);
extern int dacq_adbuf_c3(int ix);
extern int dacq_adbuf_c4(int ix);

extern int dacq_adbuf_photo(int ix);	/* aka c2 */
extern int dacq_adbuf_spikes(int ix);	/* aka c3 */

extern int dacq_eye_smooth(int kn);
extern void dacq_set_pri(int dacq_pri, int iscan_pri);

extern int pp_init(int base);
extern int pp_bar(void);
extern int pp_sw1(void);
extern int pp_sw2(void);
extern int pp_sw3(void);
extern void pp_juice(int on);
extern int pp_juice_drip(int ms);
extern void pp_out(int x);


/* this is because python1.5 doesn't have seteuid --> new to 2.0 */
extern int dacq_set_rt(int rt);
extern int dacq_seteuid(int uid);
extern int dacq_set_mypri(int pri);

extern int dacq_int_class(void);
extern int dacq_int_arg(void);
