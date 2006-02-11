/* EYELINK PORTABLE EXPT SUPPORT      */
/* (c) 1996, 1997 by SR Research      */
/*     8 June '97 by Dave Stampe      */
/*     For non-commercial use only    */
/*				      */
/* Header file for standard functions */

/* This module is for user applications   */
/* Use is granted for non-commercial      */
/* applications by Eyelink licencees only */

/************** WARNING **************/
/*                                   */
/* UNDER NO CIRCUMSTANCES SHOULD     */
/* PARTS OF THESE FILES BE COPIED OR */
/* COMBINED.  This will make your    */
/* code impossible to upgrade to new */
/* releases in the future, and       */
/* SR Research will not give tech    */
/* support for reorganized code.     */
/*                                   */
/* This file should not be modified. */
/* If you must modify it, copy the   */
/* entire file with a new name, and  */
/* change the the new file.          */
/*                                   */
/************** WARNING **************/


#ifdef __cplusplus 	/* For C++ compilers */
extern "C" {
#endif

#ifndef BYTEDEF
  #include "eyetypes.h"
  #include "eyelink.h"
#endif


/*********** EXPTSPPT USER ROUTINES **************/
/*                                               */
/* To use the XPT_xxxx.C experiment support      */
/* code, you need to create these routines in    */
/* a form that supports your needs and platform. */
/* These are general enough to support almost    */
/* any remote-control, windowing, or full-screen */
/* experiment or platform.                       */
/*                                               */
/*************************************************/

/******** CALIBRATION DISPLAY ********/

	/* sets up display for calibration    */
	/* may be called repeatedly,          */
        /* just clear screen if window exists */
	/* return -1 if fails, else 0         */
INT16 setup_cal_display(void);

	/* Clear calibration display.               */
        /* Used by drift correction and calibration */
void clear_cal_display(void);

	/* These routines implement the drawing and erasing */
	/* of the calibration and drift correction targets  */
void erase_cal_target(void);	     	 /* erase target */
void draw_cal_target(INT16 x, INT16 y);  /* draw target at (x,y) */

	/* end of setup: cleanup calibration display            */
        /* potentilly can be called going from setup to d.corr. */
void exit_cal_display(void);

       /* Produce cue sounds during calibration and drift correction */
void cal_target_beep(void);	   /* used to signal new target      */
       /* used to signal end: <error> nonzero if failure tone needed */
void cal_done_beep(INT16 error);

  // NEW sounds added for greater drift correction control
       /* used to signal new drift correction target appearance */
extern void dc_target_beep(void);
       /* used to signal drift correction end */
extern void dc_done_beep(INT16 error);

/******** CAMERA IMAGE DISPLAY ********/

	/* setup for image display:                           */
        /* gives expected image size so you can format screen */
	/* may be called repeatedly: ignore after first call  */
	/* return -1 if can't set up screen, else 0           */
INT16 setup_image_display(INT16 width, INT16 height);

        /* supplies camera ID and threshold for image title */
        /* called whenever data changes                     */
void image_title(INT16 threshold, char *cam_name);

	/* used to display an image line, (<line> = 1..<totlines> */
	/* <pixels> is <width> bytes containing picture colors    */
void draw_image_line(INT16 width, INT16 line, INT16 totlines, byte *pixels);

	/* gives a set of RGB colors to set up for next image */
        /* RGB components range from 0 to 255                 */
void set_image_palette(INT16 ncolors, byte r[], byte g[], byte b[]);

	/* end of image display: only called on real exit */
void exit_image_display(void);


/******** RECORDING ABORT NOTIFICATION ********/

	/* called if abort of record from tracker     */
        /* Usually  used to hide display from subject */
void record_abort_hide(void);


/******** KEY SCANNING ********/

	/* some useful keys returned by getkey()                    */
	/* These keys allow remote control of tracker during setup. */
        /* on non-DOS platforms, you should produce these codes and */
	/* all printable (0x20..0x7F) keys codes as well.           */
	/* Return JUNK_KEY (not 0) if untranslatable key pressed.   */
        /* TERMINATE_KEY can be to break out of EXPTSPPT loops.     */

#define CURS_UP    0x4800
#define CURS_DOWN  0x5000
#define CURS_LEFT  0x4B00
#define CURS_RIGHT 0x4D00

#define ESC_KEY   0x001B
#define ENTER_KEY 0x000D

#define PAGE_UP   0x4900
#define PAGE_DOWN 0x5100

#define JUNK_KEY      1       /* returns this code if untranslatable key */
#define TERMINATE_KEY 0x7FFF  /* returns this code if program should exit */

	/* Returns 0 if no key pressed          */
	/* returns a single UINT16 integer code */
	/* for both standard and extended keys  */
	/* Standard keys == ascii value.        */
	/* MSBy is set for extended codes       */
UINT16 CALLTYPE getkey(void);

        /* Calls getkey(), also sends keys to tracker for remote control */
        /* User implementation allows filtering of keys before sending   */
        /* returns same codes as getkey() */
UINT16 CALLTYPE echo_key(void);




/********** EXPTSPPT SUPPORT ROUTINES ****************/
/*                                                   */
/* These are defined in the XPT_xxxx.C experiment    */
/* support code.  By using these routines, the       */
/* creation of experiments is greatly simplified.    */
/* You will rarely need to bypass these routines,    */
/* unless you need special features such as          */
/* animated calibration targets, etc.                */
/* Bypassing these routines should be the last       */
/* resort.                                           */
/* NEVER MODIFY the EXPTSPPT.H or XPT_xxx.C files:   */
/* copy them with a new name, and modify the copies. */
/*                                                   */
/*****************************************************/

/******** LINK FORMATTED COMMANDS **********/

	/* link command formatting */
	/* use just like printf() */
	/* returns command result */
	/* allows 500 msec. for command to finish */

INT16 eyecmd_printf(char *fmt, ...);

	/* link message formatting */
	/* use just like printf() */
	/* returns any send error */

INT16 eyemsg_printf(char *fmt, ...);



/*********** RECORDING SUPPORT FUNCTIONS ************/

      /* RETURN THESE CODES FROM YOUR RECORDING FUNCTIONS */
      /* These codes are returned by all these functions  */

#define DONE_TRIAL   0  /* return codes for trial result */
#define TRIAL_OK     0
#define REPEAT_TRIAL 1
#define SKIP_TRIAL   2
#define ABORT_EXPT   3

#define TRIAL_ERROR  -1 /* Bad trial: no data, etc. */

	       /* Start recording with data types requested      */
	       /* Check that all requested link data is arriving */
	       /* return 0 if OK, else trial exit code           */
INT16 CALLTYPE start_recording(INT16 file_samples, INT16 file_events,
		   			  INT16 link_samples, INT16 link_events);

	/* Check if we are recording: if not, report an error  */
	/* Also calls record_abort_hide() if recording aborted */
        /* Returns 0 if recording in progress                  */
	/* Returns ABORT_EXPT if link disconnected             */
	/* Handles recors abort menu if trial interrupted      */
	/* Returns TRIAL_ERROR if other non-recording state    */

	/* Typical use is  */
        /*   if((error=check_recording())!=0) return error; */

INT16 CALLTYPE check_recording(void);

       /* halt recording, return when tracker finished mode switch */
void CALLTYPE stop_recording(void);

       /* enter tracker idle mode, wait  till finished mode switch */
void CALLTYPE set_offline_mode(void);

       /* call at end of trial, return result                   */
       /* check if we are in Abort menu after recording stopped */
       /* returns trial exit code                               */
INT16 CALLTYPE check_record_exit(void);


/******** CALIBRATION, DRIFT CORRECTION CONTROL ******/

	/* These control drift correction, setup menu, etc.. */

extern INT16 target_beep;       /* allow beep on target change */

	/* These control use of local keyboard */
	/* during calibration and drift correction */
	/* set to 0 to disable, 1 to enable */

extern INT16 allow_local_trigger;   /* allow local spacebar -> trigger */
extern INT16 allow_local_control;   /* allow all local keys -> tracker */


/********* PERFORM SETUP ON TRACKER  *******/

	/* Starts tracker into Setup Menu. */
	/* From this the operator can do camera setup, calibrations, etc. */
	/* Pressing ESC on the tracker exits. */
	/* Leaving the setup menu on the tracker (ESC) key) also exits. */
	/* RETURNS: 0 if OK, 27 if aborted, TERMINATE_KEY if pressed */
INT16 CALLTYPE do_tracker_setup(void);


/********* PERFORM DRIFT CORRECTION ON TRACKER  *******/

   /* Performs a drift correction, with target at (x,y).     */
   /* If operator aborts with ESC, we assume there's a setup */
   /* problem and go to the setup menu (which may clear the  */
   /* display).  Redraw display if needed and repeat the     */
   /* call to  do_drift_correct() in this case.              */

   /* ARGS: x, y: position of target */
   /*       draw: draws target if 1, 0 if you draw target first */
   /*       allow_setup: 0 disables ESC key setup mode entry */
   /* RETURNS: 0 if OK, 27 if Setup was called, TERMINATE_KEY if pressed */

INT16 CALLTYPE do_drift_correct(INT16 x, INT16 y, INT16 draw, INT16 allow_setup);


/*********** FILE TRANSFER **********/

  /* THIS ROUTINE MAY NEED TO BE CREATED FOR EACH PLATFORM */
  /* This call should be implemented for a standard programming interface */

   /* Copies tracker file <src> to local file <dest>.     */
   /* If specifying full file name, be sure to add ".edf" */
   /* extensions for data files.                          */

   /* If <src> = "", tracker will send last opened data file.            */
   /* If <dest> is NULL or "", creates local file with source file name. */
   /* Else, creates file using <dest> as name.  If <dest_is_path> != 0   */
   /* uses source file name but adds <dest> as directory path. */
   /* returns: file size if OK, negative =  error code       */

INT32 CALLTYPE receive_data_file(char *src, char *dest, INT16 dest_is_path);



/********** EXPTSPPT INTERNAL ROUTINES ************/
/*                                                */
/* These are defined in the XPT_xxxx.C experiment */
/* support code.  These are not intended for use  */
/* in experiments, but are used within the        */
/* EXPTSPPT library.  They are included here for  */
/* creation of extensions or cross-platform       */
/* implementations.                               */
/*                                                */
/**************************************************/


  /* THESE FUNCTIONS IN XPT_GETF.C ARE USED FOR CROSS-PLATFORM SUPPORT */
  /* If required, these may be used to develop alternatives or to      */
  /* implement the receive_data_file() code for specific platforms.    */

        /* Prepares for file receive: gets name */
        /* <srch> has request name, if "" gets last opened EDF file */
        /* <name> will contain actual file name, */
        /* set <full_name> if you want DOS path included */
        /* Returns: negative if error, else file size */
INT32 start_file_receive(char *srch, char *name, int full_name);

        /* receive next file block, at <offset> in file */
        /* return size of block (less than FILE_BLOCK_SIZE if last) */
        /* returns negative error code if can't receive */
        /* FILE_XFER_ABORTED if can't recover */
INT32 receive_file_block(INT32 offset, void *buf);


  /* INTERNAL FUNCTION: YOU DO NOT NEED TO CALL */
	/* If the trial is aborted (CTRL-ALT-A on the tracker) */
	/* we go to user menu 1.  This lets us perform a setup, */
	/* repeat this trial, skip the trial or quit. */
	/* Requires the user menu 1 (Abort) to be set up */
	/* on tracker (the default is preset in KEYS.INI). */
	/* RETURNS: One of REPEAT_TRIAL, SKIP_TRIAL, ABORT_EXPT. */
INT16 record_abort_handler(void);


    /* (USED BY do_tracker_setup(), YOU DO NOT NEED TO CALL */
	/* This handles display of the EyeLink camera images */
	/* While in imaging mode, it contiuously requests */
	/* and displays the current camera image */
	/* It also displays the camera name and threshold setting */
	/* Keys on the subject PC keyboard are sent to the tracker */
	/* so the experimenter can use it during setup. */
	/* It will exit when the tracker leaves */
	/* imaging mode or discannects */

    /* RETURNS: 0 if OK, TERMINATE_KEY if pressed, -1 if disconnect */
INT16 CALLTYPE image_mode_display(void);


        /* (USED BY do_tracker_setup(), YOU DO NOT NEED TO CALL */

	/* While tracker is in any mode with fixation targets... */
	/* Reproduce targets tracker needs. */
	/* Called for you by do_tracker_setup() and do_drift_correct() */

	/* (if allow_local_trigger) Local Spacebar acts as trigger */
	/* (if allow_local_control) Local keys echoes to tracker */
	/* RETURNS: 0 if OK, 27 if aborted, TERMINATE_KEY if pressed */
INT16 CALLTYPE target_mode_display(void);


/********* EDF OPEN, CLOSE ************/

// These functions were added as future revisions of EyeLink
// might require significant time to open and close EDF files

	// Opens EDF file on tracker hard disk
	// Returns 0 if success, else error code
INT16 CALLTYPE open_data_file(char *name);

	// Closes EDF file on tracker hard disk
	// Returns 0 if success, else error code
INT16 CALLTYPE close_data_file(void);

/********** NEW STANDARD FUNCTIONS ***************/

          // Checks state of aplication in message-passing GUI environments
INT16 CALLTYPE application_terminated(void);


#ifdef __cplusplus 	/* For C++ compilation */
}
#endif

