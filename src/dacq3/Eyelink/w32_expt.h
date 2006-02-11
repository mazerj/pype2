// W32 LIB INTERNALS VERSION: NOT FOR DISTRIBUTION
// WIN32 programming header for EYELINK demo


#ifndef WIN32
#include "eyetypes.h"
#include <SDL/SDL.h>
#define CALLBACK
typedef  SDL_Palette EPALETTE;
typedef  SDL_Color PALETTEENTRY;
typedef  unsigned int UINT;
typedef  unsigned char CHAR;
typedef  void * HDC;
typedef  SDL_Surface* HWND;
typedef  unsigned int COLORREF;
#define RGB(x)        SDL_MapRGB(eyelink_window->format,(x).r, (x).g, (x).b) 
typedef  SDL_Palette * HPALETTE;
typedef  unsigned short  WPARAM;
typedef  unsigned int    LPARAM;
typedef  void * HBITMAP;
typedef  void * HINSTANCE;
typedef  void * LRESULT;
typedef  void * LPSTR;
typedef  void * HFONT;
typedef  void * WNDPROC;
typedef  void * HPEN;
typedef  void * HBRUSH;
typedef  void   VOID;
typedef  void * POINT;
#define  TRUE  1
#define  FALSE 0
#define  MB_ICONEXCLAMATION 0
#define  MB_TASKMODAL       0
#define PS_NULL             0
#define PS_SOLID	    0
#define BI_RGB	 	    0
#define DIB_PAL_COLORS      0
#define DIB_RGB_COLORS	    0
#define DT_CENTER	    0
#define DT_TOP		    0
#define SYSTEM_FONT	    0
#define OPAQUE		    0
#define SRCCOPY		    0
#define LF_FACESIZE	    0
/*#define WM_CHAR     0
#define WM_KEYDOWN  0
#define VK_ESCAPE   0
#define VK_CONTROL  0
*/
#define PM_REMOVE   0
#define PM_NOYIELD  0
#define WM_QUIT     0
#define WM_KEYFIRST 0
#define WM_KEYLAST  0
#define PC_RESERVED 0

typedef unsigned short WORD;
typedef unsigned int   DWORD;
typedef unsigned int   LONG;
typedef unsigned char  BYTE;

typedef struct tagBITMAPFILEHEADER {
        WORD    bfType;
        DWORD   bfSize;
        DWORD   bfReserved1;
        DWORD   bfOffBits;
} BITMAPFILEHEADER;

typedef struct tagBITMAPINFOHEADER{
        DWORD      biSize;
        LONG       biWidth;
        LONG       biHeight;
        WORD       biPlanes;
        WORD       biBitCount;
        DWORD      biCompression;
        DWORD      biSizeImage;
        LONG       biXPelsPerMeter;
        LONG       biYPelsPerMeter;
        DWORD      biClrUsed;
        DWORD      biClrImportant;
} BITMAPINFOHEADER, * LPBITMAPINFO;


typedef struct {
   BITMAPFILEHEADER bmfHeader;
   BITMAPINFOHEADER bmiHeader;
   unsigned char *image_data;
} BITMAP_IMAGE;
typedef  struct _RECT
{
	int top;
	int left;
	int right;
	int bottom;
}RECT;
typedef struct tagLOGFONTA
{
    LONG      lfHeight;
    LONG      lfWidth;
    LONG      lfEscapement;
    LONG      lfOrientation;
    LONG      lfWeight;
    BYTE      lfItalic;
    BYTE      lfUnderline;
    BYTE      lfStrikeOut;
    BYTE      lfCharSet;
    BYTE      lfOutPrecision;
    BYTE      lfClipPrecision;
    BYTE      lfQuality;
    BYTE      lfPitchAndFamily;
    CHAR      lfFaceName[LF_FACESIZE];
} LOGFONT;
void MessageBox(void *dummy, ...);
HDC GetDC(HWND hWnd);

#define GetRValue(rgb)      ((BYTE)(rgb))
#define GetGValue(rgb)      ((BYTE)(((WORD)(rgb)) >> 8))
#define GetBValue(rgb)      ((BYTE)((rgb)>>16))

#endif
/************ SYSTEM SETUP *************/

                // Set up the EyeLink system and connect to tracker
                // If <dummy> not zero, will create a dummy connection
                // where eyelink_is_connected() will return -1
                // Returns: 0 if success, else error code
INT16 CALLTYPE open_eyelink_connection(INT16 dummy);

                // Close any EyeLink connection, release EyeLink system
void CALLTYPE close_eyelink_connection(void);

                // Changes the multitasking proirity of current application
                // Using THREAD_PRIORITY_ABOVE_NORMAL may reduce latency
                // Reset priority with THREAD_PRIORITY_NORMAL
                // Too high priority will stop the link from functioning!
INT32 CALLTYPE set_application_priority(INT32 priority);

extern char eyelink_version[40];
extern int is_eyelink2;


/************* SET CALIBRATION WINDOW ***********/

                // checks window to see if it exists
                // returns NULL if not valid
                // else makes sure window is visible and returns original handle
HWND validate_window(HWND hwnd);


                // set the window to be used for calibration and drift correction
                // This window must not be destroyed during experiment!
INT16 set_eyelink_window(HWND hwnd);

void release_eyelink_window(void);


/************* CALIBRATION COLORS AND TARGET ***********/

            // Sets target color and display background color
#ifdef WIN32
void CALLTYPE set_calibration_colors(COLORREF fg, COLORREF bg);
#else
void CALLTYPE set_calibration_colors(SDL_Color *fg, SDL_Color* bg);
#endif

            // Sets diameter of target and of hole in middle of target
            // Dimensions are in pixels
void CALLTYPE set_target_size(UINT16 diameter, UINT16 holesize);


/********* ABORT CALIBRATION / DC LOOP ***********/

              // Call this to stop calibration/drift correction in progress
              // This could be called from a Windows message handler 
void CALLTYPE exit_calibration(void);


/********** CALIBRATION COLOR SUPPORT ************/

                    // set up the calibration palette for the first time
                    // saves current system palette
                    // returns 0 if OK, -1 if not in indexed color mode 
INT16 init_calibration_palette(void);

        // Creates an identity palette for calibration, camera image, drift correction
        // Use DestroyObject() to delete palette when no longer required
HPALETTE create_calibration_palette(void);

                    // clean up after calibration palette
                    // restores system palette colors
void restore_system_colors(void);





void CALLTYPE set_cal_sounds(char *ontarget, char *ongood, char *onbad);

void CALLTYPE set_dcorr_sounds(char *ontarget, char *ongood, char *onbad);







/************* MESSAGE PUMP ************/
                                  
        // allows messages to operate in loops
	// returns nonzero if app terminated                          
	// eats key events, places on key queue for getkey()
        // getkey() and echo_key() also call this function
              
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

/*********** KEYBOARD SUPPORT **********/
#ifdef WIN32
         // Translate WM_KEYDOWN or WM_CHAR message into EyeLink key                                          
         // Returns 0 if not a translatable key, else EyeLink key code
UINT16 CALLTYPE translate_key_message(UINT message, WPARAM wParam, LPARAM lParam);

          // Call with WM_CHAR and WM_KEYDOWN messages from window callback
          // Process messages, translates key messages and enqueues
UINT16 CALLTYPE process_key_messages(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
#endif
    
          // Initializes and empties local key queue 
void CALLTYPE flush_getkey_queue(void);

	  // Similar to getkey(), but doesnt call message pump
          // Use to build message pump for your own window
UINT16 CALLTYPE read_getkey_queue(void);

         // Similar to getkey(), bt also sends key to tracker
         // Supports reporting of repeating keys
UINT16 CALLTYPE echo_key(void);


	// EYELINK tracker (MS-DOS) key scan equivalent
        // Processes Windows messages, records key events
        /* Returns 0 if no key pressed */
        /* returns 1-255 for non-extended keys */
        /* returns 0x##00 for extended keys (##=hex code) */
UINT16 CALLTYPE getkey(void);

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


/********** ALERT BOX ************/

	// displays general STOP-icon alert box
	// text is formatted via printf-like arguments
void CALLTYPE alert_printf(char *fmt, ...);

/********* SYNC TO DISPLAY RETRACE ********/

            // wait for VGA card retrace to begin		
            // returns immediately if running under Windows NT
void CALLTYPE wait_for_video_refresh(void);

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
           float refresh;   // refresh rate in Hz
           INT32 winnt;     // 0 if Windows 95, 1 if Windows NT
              } DISPLAYINFO;
#endif

          // get information on video driver and current mode
          // use this to determine if in proper mode for experiment.
          // If <di> not NULL, copies data into it
void CALLTYPE get_display_information(DISPLAYINFO *di);

      // a global copy 
extern DISPLAYINFO dispinfo;

#define SCREEN_LEFT   dispinfo.left
#define SCREEN_TOP    dispinfo.top
#define SCREEN_RIGHT  dispinfo.right
#define SCREEN_BOTTOM dispinfo.bottom
#define SCRHEIGHT     dispinfo.height
#define SCRWIDTH      dispinfo.width

/**************************/

        // Clear a window to a defined color
        // Uses closest of current system palette colors
void CALLTYPE clear_window(HWND hwnd, COLORREF color);


/************ 256-COLOR IDENTITY PALETTE SUPPORT **********/

               // An identity palette that sis optimized for most languages
               // Can reserve entries for add_palette_colors()


extern int colors_available;    // total colors available in palette (236 or 254)
extern int first_palette_color; // first, last non-static colors in palette
extern int last_palette_color;

                // Convert color to work with palettes (supports VB system color codes) 
COLORREF palcolor(COLORREF c);  

                // Fills in data fields of an EPALETTE
                // Will not destroy any RGB colors in it
                // Makes all colors available to add_epalette_color() if <unreserve> not 0
void initialize_epalette(EPALETTE *ep, INT16 unreserve);

              // Translates an ELPALETTE into a HPALETTE
              // If <hp> is NULL, creates a new palette
              // Otherwise, changes the <hp> palette to match <ep>
HPALETTE make_hpalette(HPALETTE hp, EPALETTE *ep);

extern EPALETTE system_epalette;

              // Translates an ELPALETTE into a HPALETTE
              // If <hp> is NULL, creates a new palette
              // Otherwise, changes the <hp> palette to match <ep>
HPALETTE make_hpalette(HPALETTE hp, EPALETTE *ep);

          // Set system palette to be halftone color set
void set_system_halftone_colors(void);

        // Make an identity EPALETTE matching current system palette
        // This is stored in system_epalette: if <ep> not NULL, also copied to *ep 
        // Returns 0 if sucess, else not in indexed color mode
INT16 make_system_epalette(EPALETTE *ep);

            // Initialize palette to system halftone color set
            // Resets list of used colors
            // Returns 0, else not in a 256-color display mode
INT16 create_halftone_epalette(EPALETTE *ep);

            // Sets the displayed system palette to match HPALETTE
            // This will also be done by drawing to screen with palette
void set_display_hpalette(HPALETTE hpal);

            // Sets the displayed system palette to match EPALETTE
            // This will also be done by drawing to screen with palette
void set_display_epalette(EPALETTE *ep);

            // Change a block of color in the palette, and mark as reserved
            // first color cannot be less than first_palette_color (usually 10)
            // last color cannot be greater than last_palette_color (usually 246)
void change_epalette_colors(EPALETTE *ep, UINT16 first, UINT16 count, PALETTEENTRY *colors);

            // Add color to palette, replacing closest color
            // This will avoid colors you have previously set
            // If <use_static> set, will use exact matches to system colors 
            // Returns index of color changed, -1 if couldn't change (all colors used, or not in palette mode)
INT16 add_epalette_color(EPALETTE *ep, COLORREF color, INT16 use_static);


/************** DRAW 256-COLOR PALETTE *********/

          // draw 16x16 grid of all 256 colors in palette
          // palette must be selected into DC and realized
          // can draw to display or bitmap DC
void paldraw(HDC hdc, INT16 x, INT16 y, INT16 size); 

          // draw 16x16 grid containing current system palette to display
void show_system_palette(HWND hwnd);


/************* PAGE SPPT ************/

extern HDC page_dc;
extern HPALETTE page_hpalette;    // Page 0 palette
extern EPALETTE page_epalette;    // Page 0 palette

      // Initialze graphics and calibration system
      // Handle to a full-screen window that will be used during experiment must be supplied
      // If you can't supply a handle, use NULL and make your window the topmost before call
      // The <debug> argument must be 1 for compatibility with debuggers, 0 for real speed
      // If not NULL, the <info> struct wull be filled with information on the display mod
      // Returns 0 if OK
INT16 CALLTYPE init_expt_graphics(HWND hwnd, DISPLAYINFO *info);

      // Close the calibration and graphics, release resources
      // You should only destroy your full-screen window after this call
void CALLTYPE close_expt_graphics(void);

      // Sets the colors of the palette (256-color mode only) for a page
      // If <ep> is NULL, uses page 0's palette (this is the default)
      // Colors are realized on display immediately if page is currently displayed 
      // Returns 0 if OK
INT16 set_window_palette(EPALETTE *ep);

      // Gets a display context to draw on the page
      // This is a static DC, so all settings from your last use are preserved 
      // Page 0 can be drawn on using a standard DC
      // In debug mode, drawing could be to a memory bitmap except for page 0
      // In non-debug mode, DirectDraw will lock the system until release_page_dc() is called
HDC CALLTYPE get_window_dc(void);

      // Release the page DC 
      // In non-debug mode, DirectDraw will lock the system until this call
INT16 CALLTYPE release_window_dc(HDC hdc);

      // Clears entire page to this given color (or closest in palette)
INT16 clear_page(COLORREF color);




/////////////////////////////////////////
/////////////////////////////////////////
/////////////////////////////////////////


               // Draw grid of letters on local display, 
               // Draw boxes for each letter on EyeLink screen
               // Creates memory bitmap 
               // After you're done, delete with DeleteObject(hBitmap)
HBITMAP grid_test_bitmap(void);

               // Copies bitmap to display 
void display_bitmap(HWND hwnd, HBITMAP hbm, int x, int y);


extern COLORREF myGray; // background of grid screen

               // Draw grid of letters on local display, 
               // Draw boxes for each letter on EyeLink screen
void grid_test_screen(void);

extern COLORREF target_foreground_color;  /* target display color */
extern COLORREF target_background_color;  /* calibration screen color */




/*************** CREATE FULL-SCREEN WINDOW **********/

extern HPALETTE our_hpalette;           // the default palette
extern EPALETTE our_epalette;

extern HWND full_screen_window;
extern int full_screen_window_active;

        /* setup the full-screen window */
int make_fullscreen_window(HINSTANCE hInstance);

void clear_full_screen_window(COLORREF c);

                                  // Handles all automatic message functions
                                  // Call from main processing handler  
                                  // Retuens 0 if not handled, else handled 
LRESULT CALLBACK full_screen_window_proc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);


/************* GENERAL PURPOSE NUMBER/TEXT DIALOG **************/
                        
                // Center window <hwnd> on the screen
void CenterWindow(HWND hwnd);
                  
                // Create single-line text-edit DB
                // with window <title>, text message <msg>
                // text buffer <txt> contains original text, will get result
                // <maxsize> sets max number of characters  
INT16 CALLTYPE edit_dialog(HWND hwnd, LPSTR title, LPSTR msg, LPSTR txt, INT16 maxsize);


/************* FILE DIALOGS *************/
         
extern char oldSaveFile[260];   // holds last-save file name & path
extern char oldSavePath[260];    // parts of the name
extern char oldSaveName[60];      

                  // Sets the default file name and path
void set_save_default(char *name);


                    // <filter> will be the default file name
                    // If directory only, uses file name set previously  
                    // if name only, uses previous directory
                    // returns TRUE if file name placed in <path>
int SaveFileNameDB(HWND hwnd, LPSTR path, LPSTR filter);

/**************************/

extern HFONT current_font;

              // Create a font, cache in current_font
HFONT get_new_font(char *name, int size, int bold);

                  // Release the font
void release_font(void);


		// Uses printf() formatting
		// Prints starting at x, y position
		// Uses current font, size, foreground color, bkgr. color & clr mode
                // <bg> is -1 to NOT clear background 
#ifdef WIN32
void graphic_printf(COLORREF fg, COLORREF bg, int center, int x, int y, char *fmt, ...);
#endif


/************* CALIBRATION WINDOW **********/

// NOTE: The window used for calibration must be set by application.
// This allows external programs (Visual Basic or MFC) to set a window
// It's important to use the same window during calibration and experiments 
// to prevent automatic redrawing which could cause flickering

extern char dll_version[30];

extern HWND eyelink_window;  // the window used for calibration  
extern HINSTANCE eyelink_instance;

extern int eyelink_application_active;
extern int eyelink_window_active;
extern int in_calibration;

extern LRESULT CALLBACK eyelink_window_proc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
extern WNDPROC original_window_proc;  

              // redraw camera image during repaint
void refresh_camera_image(void);

              // Releases the message intercept
void unsubclass_window(HWND hwnd);

              // Starts to intercept messages going to window
              // Passes through eyelink_window_proc()
              // Returns -1 if failed, 0 if success
INT16 subclass_window(HWND hwnd);

/********** INDEXED CALIBRATION COLOR SUPPORT *********/

extern INT16 last_drawn_target_x;
extern INT16 last_drawn_target_y; 

extern int target_outside_radius;
extern int target_inside_radius;
                           
#ifndef WIN32
extern SDL_Color cal_foreground_color;  /* target display color */
extern SDL_Color cal_background_color;  /* calibration screen color */
#else
extern COLORREF cal_foreground_color;  /* target display color */
extern COLORREF cal_background_color;  /* calibration screen color */
#endif

extern int use_fixed_fg_index;         // set if we are using fixed index
extern int use_fixed_bg_index;         // else we will find best color indexes
extern int cal_foreground_index;
extern int cal_background_index;

extern PALETTEENTRY old_system_colors[256];   // table of original system colors
extern PALETTEENTRY camera_colors[256];        // camera colors palette

extern int camera_colors_index[3];    // first index in identity palette for camera color table
extern int camera_colors_size[3];     //number of entries: 0 if unused

extern int calibration_palette_mode;      // set if calibration palette currently set up

extern HPALETTE calibration_palette;   // calibration display and camera image palette
extern EPALETTE calibration_epalette;   // calibration display and camera image palette


/************** HOOKS FOR CAL GRAPHICS ****************/

			// Sets a function to be called to before drawing
			// NULL can be used to disable hook
			// Hook function <hookfn> should return:
#define HOOK_ERROR    -1  // if error occurred  
#define HOOK_CONTINUE  0  // if drawing to continue after return from hook
#define HOOK_NODRAW    1  // if drawing should not be done after hook
						   
// These are the functions expected for hooks:

extern INT16 (CALLBACK * setup_cal_display_hook)(void);
extern INT16 (CALLBACK * clear_cal_display_hook)(HDC hdc);
extern INT16 (CALLBACK * erase_cal_target_hook)(HDC hdc);	     
extern INT16 (CALLBACK * draw_cal_target_hook)(HDC hdc, INT16 * x, INT16 * y);
extern INT16 (CALLBACK * exit_cal_display_hook)(void);
extern INT16 (CALLBACK * cal_sound_hook)(INT16 * error);
extern INT16 (CALLBACK * record_abort_hide_hook)(void);

extern INT16 (CALLBACK * setup_image_display_hook)(INT16 width, INT16 height);
extern INT16 (CALLBACK * image_title_hook)(INT16 threshold, char *cam_name);
extern INT16 (CALLBACK * draw_image_line_hook)(INT16 width, INT16 line, INT16 totlines, byte *pixels);
extern INT16 (CALLBACK * set_image_palette_hook)(INT16 ncolors, byte r[], byte g[], byte b[]);
extern INT16 (CALLBACK * exit_image_display_hook)(void);


// These are the constants in the argument to cal_sound_hook():

#define CAL_TARG_BEEP   1
#define CAL_GOOD_BEEP   0
#define CAL_ERR_BEEP   -1

#define DC_TARG_BEEP	3
#define DC_GOOD_BEEP	2
#define DC_ERR_BEEP	   -2


INT16 CALLTYPE set_camera_image_position(INT16 l, INT16 t, INT16 r, INT16 b);

extern INT16 camera_image_window_l;
extern INT16 camera_image_window_t;
extern INT16 camera_image_window_r;
extern INT16 camera_image_window_b;
