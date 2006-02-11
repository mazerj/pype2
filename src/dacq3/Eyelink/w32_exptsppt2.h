/*   EYELINK WINDOWS 95/NT EXPT SUPPORT      */
/*   (c) 1997-2002 by SR Research            */
/*   24 Nov '97 by Dave Stampe               */
/*   EYELINK II / V2.0: 5 March 2002         */
/*   For non-commercial use only             */
/*				             */

// 18 Sept 2002: added new functions for
// file name check, in_realtime_mode()

/* Header file for EYELINK_EXPTKIT.DLL V2            */
/* YOU MUST replace w32_exptsppt.h  to use new DLL!  */
/* Updated for v2.10 with new functions              */

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

#ifndef SIMLINKINCL
  #include "eyelink.h"
#endif

#ifndef W32EXPTSPPTINCL
#define W32EXPTSPPTINCL

/************ SYSTEM SETUP *************/

                // Set up the EyeLink system and connect to tracker
                // If <dummy> is  0, opens a connection with the eye tracker
                // If <dummy> is  1, will create a dummy connection
                // If <dummy> is -1, initializes the DLL but does not open a connection
                // where eyelink_is_connected() will return -1
                // Returns: 0 if success, else error code
INT16 CALLTYPE open_eyelink_connection(INT16 dummy);

                // Close any EyeLink connection, release EyeLink system
void CALLTYPE close_eyelink_connection(void);

                // Sets IP address for connection to EyeLink tracker
                // Argument is IP address (default is "100.1.1.1")  
                // An address of "255.255.255.255" will broadcast 
                // (broadcast may not work with multiple Ethernet cards) 
                // Returns: 0 if success, -1 if could not parse address string
INT16 CALLTYPE set_eyelink_address(char *addr);

               // Converts IP address string (e.g "100.1.1.1")
               // to an EyeLink node
               // <remote> is 0 for a tracker, 1 for another EyeLink application
INT16 CALLTYPE text_to_elinkaddr(char *addr, ELINKADDR node, int remote);

                // copies pointer to DLL version string
void CALLTYPE eyelink_dll_version(char FARTYPE *c);

/*********** SET APPLICATION PRIORITY **********/

                // Changes the multitasking proirity of current application
                // Using THREAD_PRIORITY_ABOVE_NORMAL may reduce latency
                // Reset priority with THREAD_PRIORITY_NORMAL
                // Too high priority will stop the link from functioning!
INT32 CALLTYPE set_application_priority(INT32 priority);

                // Sets up for realtime execution (minimum delays)
                // This may take some time (assume up to 100 msec)
                // <delay> sets min time so delay may be useful
                // Effects vary by operating system
                // Keyboard, mouse, and sound may be disabled in some OS
                // Has little effect in Win9x/ME
void CALLTYPE begin_realtime_mode(UINT32 delay);

                // Exits realtime execution mode
                // Typically just lowers priority
void CALLTYPE end_realtime_mode(void);

                // Raise application priority
                // May interfere with other applications
void CALLTYPE set_high_priority(void);

                // Sets application priority to system normal
void CALLTYPE set_normal_priority(void);

                // returns 1 if in realtime mode, else 0
INT32 in_realtime_mode(void);


/*********** KEYBOARD SUPPORT **********/

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

	// EYELINK tracker (MS-DOS) key scan equivalent
        // Processes Windows messages, records key events
        /* Returns 0 if no key pressed */
        /* returns 1-255 for non-extended keys */
        /* returns 0x##00 for extended keys (##=hex code) */
UINT16 CALLTYPE getkey(void);

         // Similar to getkey(), bt also sends key to tracker
         // Supports reporting of repeating keys
UINT16 CALLTYPE echo_key(void);

         // Translate WM_KEYDOWN or WM_CHAR message into EyeLink key                                          
         // Returns 0 if not a translatable key, else EyeLink key code
UINT16 CALLTYPE translate_key_message(UINT message, WPARAM wParam, LPARAM lParam);

          // Call with WM_CHAR and WM_KEYDOWN messages from window callback
          // Process messages, translates key messages and enqueues
UINT16 CALLTYPE process_key_messages(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
    
          // Initializes and empties local key queue 
void CALLTYPE flush_getkey_queue(void);

	  // Similar to getkey(), but doesnt call message pump
          // Use to build message pump for your own window
UINT16 CALLTYPE read_getkey_queue(void);

/************* BREAK TESTS *********/

                // returns non-zero if ESC key held down
INT16 CALLTYPE escape_pressed(void);

                // returns non-zero if Ctrl-C held down
INT16 CALLTYPE break_pressed(void);


/********* ASYNCHRONOUS BREAKOUTS *********/

    // Because Windows is multi-tasking, some other event (i.e. a timer event or ALT-TAB)
    // may affect your application during loops or calibration.
    // Your event handlers can call these functions to stop ongoing operations

            // call from Windows event handlers when application must exit
            // forces calibration or drift correction to exit with result=27
            // when <assert> is nonzero,  will caused break_pressed() to test trua continuously, 
            // also causes getkey() to return TERMINATE_KEY
            // If <assert> is 0, will restore break_pressed() and getkey() to normal
void CALLTYPE terminal_break(INT16 assert);

              // Call this to stop calibration/drift correction in progress
              // This could be called from a Windows message handler 
void CALLTYPE exit_calibration(void);


/********* SYNC TO DISPLAY RETRACE ********/

            // wait for VGA card retrace to begin		
            // returns immediately if retrace detection not supported
void CALLTYPE wait_for_video_refresh(void);

            // returns 1 if in vertical retrace, 0 if not
            // returns 0 if retrace detection not supported
INT16 CALLTYPE in_vertical_retrace(void);


/********** VIDEO DISPLAY INFORMATION **********/

        // This structure holds information on the display
        // Call get_display_infomation() to fill this with data
        // Check mode before running experiment!

#ifndef DISPLAYINFODEF
  #define DISPLAYINFODEF
  typedef struct {
           INT32 left;      // left of display
           INT32 top;       // top of display
           INT32 right;     // right of display
           INT32 bottom;    // bottom of display
           INT32 width;     // width of display
           INT32 height;    // height of display
           INT32 bits;      // bits per pixel
           INT32 palsize;   // total entries in palette (0 if not indexed display mode)
           INT32 palrsvd;   // number of static entries in palette (0 if not indexed display mode)
           INT32 pages;     // pages supported
           float refresh;   // refresh rate in Hz ( <40 if refresh testing failed)
           INT32 winnt;     // Windows version: 0=9x/Me, 1 if NT, 2 if 2000, 3 if XP
              } DISPLAYINFO;
#endif

      // you should put a global copy of this in your code 
extern DISPLAYINFO dispinfo;

#define SCREEN_LEFT   dispinfo.left
#define SCREEN_TOP    dispinfo.top
#define SCREEN_RIGHT  dispinfo.right
#define SCREEN_BOTTOM dispinfo.bottom
#define SCRHEIGHT     dispinfo.height
#define SCRWIDTH      dispinfo.width

          // get information on video driver and current mode
          // use this to determine if in proper mode for experiment.
          // If <di> not NULL, copies data into it
void CALLTYPE get_display_information(DISPLAYINFO *di);


/************* PAGE SPPT ************/

      // Initialze graphics and calibration system
      // Handle to a full-screen window that will be used during experiment must be supplied
      // If you can't supply a handle, use NULL and make your window the topmost before call
      // If not NULL, the <info> struct wull be filled with information on the display mod
      // Returns 0 if OK
INT16 CALLTYPE init_expt_graphics(HWND hwnd, DISPLAYINFO *info);

      // Close the calibration and graphics, release resources
      // You should only destroy your full-screen window after this call
void CALLTYPE close_expt_graphics(void);

      // Gets a display context to draw on the page
      // This is a static DC, so all settings from your last use are preserved 
HDC CALLTYPE CALLTYPE get_window_dc(void);

      // Release the page DC 
INT16 CALLTYPE CALLTYPE release_window_dc(HDC hdc);

        // Clear a window to a defined color
        // Uses closest of current system palette colors
void CALLTYPE clear_window(HWND hwnd, COLORREF color);

        // forces drawing to begin, waits for drawing to finish
        // HWND may be NULL (will wait for drawing on all displays)
void CALLTYPE wait_for_drawing(HWND hwnd);

/********* CALIBRATION COLORS, TARGET, AND SOUNDS *******/

            // Sets target color and display background color
#ifdef WIN32
void CALLTYPE set_calibration_colors(COLORREF fg, COLORREF bg);
#endif

            // Sets diameter of target and of hole in middle of target
            // Dimensions are in pixels
void CALLTYPE set_target_size(UINT16 diameter, UINT16 holesize);

            // Selects sounds to be played on calibration events
            // If a sound is "", a default ound will be made
            // If a sound is "off", no sound is played
            // Otherwise, this is the name of a .WAV file.
            // If no sound card is present, system beeps will be substituted

            // Set sounds for Setup menu (calibration, validation)
            // New target display, successful operation, error or cancellation                                       
void CALLTYPE set_cal_sounds(char *target, char *good, char *error);

            // Set sounds for drift correction
            // New target display, success, or ESC pressed (Setup begun)                                       
void CALLTYPE set_dcorr_sounds(char *target, char *good, char *setup);


/********* ABORT CALIBRATION / DC LOOP ***********/

              // Call this to stop calibration/drift correction in progress
              // This could be called from a Windows message handler 
void CALLTYPE exit_calibration(void);


/******** LINK FORMATTED COMMANDS **********/

	/* link command formatting */
	/* use just like printf() */
	/* returns command result */
	/* allows 500 msec. for command to finish */

INT16 CALLTYPE eyecmd_printf(char *fmt, ...);

	/* link message formatting */
	/* use just like printf() */
	/* returns any send error */

INT16 CALLTYPE eyemsg_printf(char *fmt, ...);


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


/************* MESSAGE PUMP ************/
                                  
        // allows messages to operate in loops
	// returns nonzero if app terminated                          
	// eats key events, places on key queue for getkey()
        // getkey() and echo_key() also call message_pump()
              
       // calling this in loops allows Windows to process messages
       // returns nonzero if application terminated (ALT-F4 sent to window)
       // set <dialog_hook> to handle of modeless dialog 
       // in order to properly handle its messages as well
INT16 CALLTYPE message_pump(HWND dialog_hook);

        // similar to message_pump(), but only processes keypresses
        // this may help reduce latency
INT16 CALLTYPE key_message_pump(void);

        // Similar to msec_delay(), but allows Widows message process
        // only allows message processing if delay > 20 msec
        // does not process dialog box messages
void CALLTYPE pump_delay(UINT32 del);


/************* GENERAL PURPOSE NUMBER/TEXT DIALOG **************/
                        
                // Create single-line text-edit DB
                // with window <title>, text message <msg>
                // text buffer <txt> contains original text, will get result
                // <maxsize> sets max number of characters  
                // Returns: 0 if OK, 1 if cancelled, -1 if ALT-F4 pressed
INT16 CALLTYPE edit_dialog(HWND hwnd, LPSTR title, LPSTR msg, LPSTR txt, INT16 maxsize);

/********** ALERT BOX ************/

	// displays general STOP-icon alert box
	// text is formatted via printf-like arguments
void CALLTYPE alert_printf(char *fmt, ...);


/********* EDF OPEN, CLOSE ************/

// These functions were added as future revisions of EyeLink
// might require significant time to open and close EDF files

	// Opens EDF file on tracker hard disk
	// Returns 0 if success, else error code
INT16 CALLTYPE open_data_file(char *name);

	// Closes EDF file on tracker hard disk
	// Returns 0 if success, else error code
INT16 CALLTYPE close_data_file(void);


/*************** GAZE-CONTINGENT WINDOW ************/

        // Initial setup of gaze-contingent window before drawing it.
        // Sets size of window, and whether it is a foveal mask.
        // If height or width is -1, the window will be a bar covering the display
        // Supply a bitmap for window and background, <size of display_rect>
        // <window> is the window to display in
        // <display_rect> should be area of display in window.
        // <deadband> sets number of pixels of anti-jitter applied  
void CALLTYPE initialize_gc_window(int wwidth, int wheight, 
                          HBITMAP window_bitmap, HBITMAP background_bitmap,
                          HWND window, RECT display_rect, int is_mask, int deadband);


       // Draw GC window at a new location
       // The first time window is drawn, 
       // the background outside the window will be filled in too.
       // If X or Y is MISSING_DATA (defined in eyelink.h), window is hidden. 
void CALLTYPE redraw_gc_window(int x, int y);


/*************** CALIBRATION GRAPHICS FUNCTION HOOKS ***************/    


// These give access to internal calls similar to those
// that the programmer must supply in the DOS version.
// Each DOS function has a corresponding hook function
// Use set_expt_graphics_hook() to register a function that will
// be called before any operation is performed by the WIN95 exptkit.
// A return value from this hook will prevent the normal operations from being performed


// These functions set the hook functions for calibration graphics. 
// These hooks will be called to before drawing.  
// A NULL hook function can be used to disable hook.
// In most cases the hook functions should work like the DOS (exptsppt.h) functions.
// Return HOOK_CONTINUE to let built-in handler continue
// else HOOK_NODRAW if you have implemented the function yourself.

#define HOOK_ERROR    -1  // if error occurred  
#define HOOK_CONTINUE  0  // if drawing to continue after return from hook
#define HOOK_NODRAW    1  // if drawing should not be done after hook

// Some routines supply a HDC, which is set up for drawing in the
// calibration window, including the palette in 256-color modes.
// The HDC will not be valid if you return HOOK_NODRAW from setup_cal_display_hook()

// For compatibility, <options> in hook-set calls should be 0
// These functions return 0 if OK, else couldn't set hook

// If you return HOOK_NODRAW from setup_cal_display_hook() then 
// you must implement all the calibration graphics functions in your own code.
extern INT16 CALLTYPE set_setup_cal_display_hook(
		INT16 (CALLBACK * setup_cal_display_hook)(void), INT16 options);

extern INT16 CALLTYPE set_clear_cal_display_hook(
		INT16 (CALLBACK * clear_cal_display_hook)(HDC hdc), INT16 options);

// The <x> and <y> values may be changed and HOOK_CONTINUE returned
// to allow the normal drawing to proceed at different locations
extern INT16 CALLTYPE set_erase_cal_target_hook(
		INT16 (CALLBACK * erase_cal_target_hook)(HDC hdc), INT16 options);	     

extern INT16 CALLTYPE set_draw_cal_target_hook(
		INT16 (CALLBACK * draw_cal_target_hook)(HDC hdc, INT16 * x, INT16 * y), INT16 options);

extern INT16 CALLTYPE set_exit_cal_display_hook(
		INT16 (CALLBACK * exit_cal_display_hook)(void), INT16 options);

// This intercepts a trapped tracker recording abort 
// (ESC or CTRL-ALT-A during recording)
extern INT16 CALLTYPE set_record_abort_hide_hook(
		INT16 (CALLBACK * record_abort_hide_hook)(void), INT16 options);

// Uses the constants below to specify predefined sound.
// You can modify <sound> and return HOOK_CONTINUE, or
// produce your own sounds and return HOOK_NODRAW.

extern INT16 CALLTYPE set_cal_sound_hook(
		INT16 (CALLBACK * cal_sound_hook)(INT16 * error), INT16 options);

// These are the constants in the argument to cal_sound_hook():

#define CAL_TARG_BEEP   1
#define CAL_GOOD_BEEP   0
#define CAL_ERR_BEEP   -1

#define DC_TARG_BEEP	3
#define DC_GOOD_BEEP	2
#define DC_ERR_BEEP	   -2

// CAMERA IMAGE DISPLAY FUNCTIONS:
// Usually you use these to monitor start and end of of image mode
// If you need to implement your own image display you have to
// return HOOK_NODRAW from setup_image_display_hook() then 
// implement all functions in your own code.

extern INT16 CALLTYPE set_setup_image_display_hook(
		INT16 (CALLBACK * setup_image_display_hook)(INT16 width, INT16 height), INT16 options);

extern INT16 CALLTYPE set_image_title_hook(
		INT16 (CALLBACK * image_title_hook)(INT16 threshold, char *cam_name), INT16 options);

extern INT16 CALLTYPE set_draw_image_line_hook(
		INT16 (CALLBACK * draw_image_line_hook)(INT16 width, INT16 line, INT16 totlines, byte *pixels), INT16 options);

extern INT16 CALLTYPE set_set_image_palette_hook(
		INT16 (CALLBACK * set_image_palette_hook)(INT16 ncolors, byte r[], byte g[], byte b[]), INT16 options);

extern INT16 CALLTYPE set_exit_image_display_hook(
		INT16 (CALLBACK * exit_image_display_hook)(void), INT16 options);


/***************** SETUP HELPERS *****************/

 // These functions are used by  do_tracker_setup(), 
 // YOU DO NOT NEED TO CALL THESE IN NORMAL EXPERIMENTS.
 // These are included in case you wish to replace setup 
 // or follow EyeLink modes, as the TRACK application does 

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


	/* While tracker is in any mode with fixation targets... */
	/* Reproduce targets tracker needs. */
	/* Called for you by do_tracker_setup() and do_drift_correct() */
	/* Local Spacebar acts as trigger */
	/* Local keys echoes to tracker */
	/* RETURNS: 0 if OK, 27 if aborted, TERMINATE_KEY if pressed */
INT16 CALLTYPE target_mode_display(void);


/***************** EYELINK II EXTENSIONS *****************/

	/* returns tracker version                     */
	/* if not yet connected, c will be ""          */
	/* for EyeLink I,  c will be "EYELINK I"       */
	/* for EyeLink II, c will be "EYELINK II x.xx" */
	/*    where x.xx is version number             */
        /* RETURNS: 0 if unknown, 1 or 2 for EyeLink I or II */
INT16 CALLTYPE eyelink_get_tracker_version(char FARTYPE *c);

	  // Get EyeLink II extended block information
          // Returns 0 if available, 
          //        -1 if not (not in data block or not EyeLink II tracker)
          // copies data if pointers not NULL:
          //    *sample_rate = samples per second
          //    *crmode = 0 if pupil-only, else pupil-CR
          //    *file_filter = 0 if file sample filter off, 1 for std, 2 for double filter
          //    *link_filter = 0 if link sample filter off, 1 for std, 2 for double filter
INT16 CALLTYPE eyelink2_mode_data(INT16 *sample_rate, INT16 *crmode, INT16 *file_filter, INT16 *link_filter);


/// NEW MODE FOR EYELIKN II

#define EL_OPTIONS_MENU_MODE  8  // NEW FOR EYELIKN II


/**************** BITMAP SAVE AND TRANSFER *********************/

// "sv_options" argument is bitwise OR of these constants
    // doesn't save file if it already exists (saves time if duplicate stimuli)
#define SV_NOREPLACE 1
    // creates directory if it doesn't yet exist
#define SV_MAKEPATH 2

// "bx_options" argument is bitwise OR of these constants

    // Controls how bitmap size is reduced to fit tracker display
#define  BX_AVERAGE     0   // average combined pixels
#define  BX_DARKEN      1   // choose darkest (keep thin dark lines)
#define  BX_LIGHTEN     2   // choose darkest (keep thin white lines)  

    // Maximizes contrast for clearest image
#define  BX_MAXCONTRAST 4   // stretch contrast to black->white

    // Image is normally ditheres--disable to get clearest text
#define  BX_NODITHER    8   // No dither, just quantize 

    // grayscale best for EyeLink I, text, etc.
#define  BX_GREYSCALE   16  // Convert to grayscale
#define  BX_GRAYSCALE   16  

  
          // saves entire bitmap as file, and transfers to tracker as backdrop
          // bitmap is at (xs, ys) in source bitmap
          // uses (width, height) of bitmap (set to 0 to use all)
          // determines file type from extension (.PNG, .BMP, .JPG, .TIF)
          // "options" determines how bitmap is processed
          // bitmap top-left to (xd, yd) on tracker display
          // Returns 0 if OK, -1 if coldn't save, -2 if couldn't transfer
int bitmap_save_and_backdrop(HBITMAP hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
                             char *fname, char *path, INT16 sv_options,
			     INT16 xd, INT16 yd, UINT16 bx_options);

          // saves entire bitmap as file
          // bitmap is at (xs, ys) in source bitmap
          // uses (width, height) of bitmap (set to 0 to use all)
          // determines file type from extension (.PNG, .BMP, .JPG, .TIF)
          // Returns 0 if OK, -1 if error
int bitmap_save(HBITMAP hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
                char *fname, char *path, INT16 sv_options);

          // transfers bitmap to tracker as backdrop for gaze cursors
          // bitmap is at (xs, ys) in source bitmap
          // uses (width, height) of bitmap (set to 0 to use all)
          // bitmap top-left to (xd, yd) on tracker display
          // "options" determines how bitmap is processed
          // Returns 0 if OK, -1 or -2 if couldn't transfer
int bitmap_to_backdrop(HBITMAP hbm, INT16 xs, INT16 ys, INT16 width, INT16 height,
                       INT16 xd, INT16 yd, UINT16 bx_options);


/************ FILENAME SUPPORT **************/

#define BAD_FILENAME -2222
#define BAD_ARGUMENT -2223

       // Splice 'path' to 'fname', store in 'ffname'
       // Tries to create valid concatenation
       // If 'fname' starts with '\', just adds drive from 'path'
       // If 'fname' contains drive specifier, it is not changed
void splice_fname(char *fname, char *path, char *ffname);

        // Checks file name for legality
        // Attempts to ensure cross-platform for viewer
        // No spaces allowed as this interferes with messages 
        // assume viewer will translate forward/backward slash  
        // Windows: don't allow "<>?*:|,
int check_filename_characters(char *name);

            // checks if file and/or path exists
            // returns 0 if does not exist
            //         1 if exists
            //        -1 if cannot overwrite   
int file_exists(char *path);

       // Checks if path exists
       // Will create directory if 'create'
       // Creates directory from last name in 'path, unless
       // ends with '\' or 'is_dir' nonzero.
       // Otherwise, last item is assumed to be filename and is dropped   
       // Returns 0 if exists, 1 if created, -1 if failed
int create_path(char *path, INT16 create, INT16 is_dir);


/********* VER 2.39: PRELIM MESSAGE WORK ********/

       // output messages for max <time> msec
void CALLTYPE message_process(UINT32 maxtime);

       // flush message queue to link or disk
void CALLTYPE flush_message_queue(void);

       // flush and close message file
void CALLTYPE close_message_file(void);

       // create message file
       // once open, will not send messages to tracker
INT32 CALLTYPE open_message_file(char *fname);

       // format messages
       // optional time of event (0 = NOW)
       // if file open, writes to file if not in realtime mode
       // writes to link if MSG_IMMED
       // else writes as link available
INT16 CALLTYPE timemsg_printf(UINT32 t, char *fmt, ...);

/*************************************/

#endif //W32EXPTSPPTINCL

#ifdef __cplusplus 	/* For C++ compilation */
}
#endif
