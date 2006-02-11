#! /usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

class Plex:
	"""
	A class for defining structures and constants for Plexon data
	"""
	
	PL_SingleWFType = 1
	PL_StereotrodeWFType = 2
	PL_TetrodeWFType = 3
	PL_ExtEventType = 4
	PL_ADDataType = 5
	PL_StrobedExtChannel = 257
	PL_StartExtChannel  = 258
	PL_StopExtChannel = 259
	PL_Pause = 260
	PL_Resume = 261

	# Waveform length	
	MAX_WF_LENGTH = 56
	MAX_WF_LENGTH_LONG = 120

	# Port used by PlexNet on the machine to which the MAP is connected.
	# It can be set in the PlexNet options dialog.
	PLEXNET_PORT = 6000

	# PlexNet commands
	PLEXNET_CMD_SET_TRANSFER_MODE = 10000
	PLEXNET_CMD_START_DATA_PUMP = 10200
	PLEXNET_CMD_STOP_DATA_PUMP = 10300
	PLEXNET_CMD_DISCONNECT = 10999

	# PlexNet Packet size	
	PACKETSIZE = 512

	
	#
	# Structure definitions
	#
		
	fPL_Event = 'cccBLhhcccc'
	"""	
	struct PL_Event{
		char    Type;						// so far, PL_SingleWFType or PL_ExtEventType
		char    NumberOfBlocksInRecord;
		char    BlockNumberInRecord;
		unsigned char    UpperTS;			// fifth byte of the waveform timestamp
		unsigned long    TimeStamp;			// formerly just long
		short   Channel;
		short   Unit;
		char    DataType;					// tetrode stuff, ignore for now
		char    NumberOfBlocksPerWaveform;	// tetrode stuff, ignore for now
		char    BlockNumberForWaveform;		// tetrode stuff, ignore for now
		char    NumberOfDataWords;			// number of shorts (2-byte integers) that follow this header 
	};
	"""
	
	fPL_Wave = 'cccBLhhccc56h'
	"""	
	// the same PL_Event above with Waveform added
	struct PL_Wave {
		char    Type;
		char    NumberOfBlocksInRecord;
		char    BlockNumberInRecord;
		unsigned char    UpperTS;
		unsigned long    TimeStamp;
		short   Channel;
		short   Unit;
		char    DataType; 
		char    NumberOfBlocksPerWaveform; 
		char    BlockNumberForWaveform; 
		char    NumberOfDataWords;		// number of shorts (2-byte integers) that follow this header 
		short   WaveForm[MAX_WF_LENGTH];
	};
	"""

	fPL_WaveLong = 'cccBLhhcccc120h'
	"""
	// extended version of PL_Wave for longer waveforms
	struct PL_WaveLong {
		char    Type;
		char    NumberOfBlocksInRecord;
		char    BlockNumberInRecord;
		unsigned char    UpperTS;
		unsigned long    TimeStamp;
		short   Channel;
		short   Unit;
		char    DataType; 
		char    NumberOfBlocksPerWaveform; 
		char    BlockNumberForWaveform;	// number of shorts (2-byte integers) that follow this header 
		char    NumberOfDataWords;
		short   WaveForm[MAX_WF_LENGTH_LONG];
	}; // size should be 256
	"""


	fPL_FileHeader = 'Ii128siiiiiiiiiiiiiidccccHH48s650h650h512h'
	"""	
	// file header (is followed by the channel descriptors)
	struct  PL_FileHeader {
		unsigned int    MagicNumber;	// = 0x58454c50;
		int     Version;
		char    Comment[128];
		int		ADFrequency;			// Timestamp frequency in hertz
		int		NumDSPChannels;			// Number of DSP channel headers in the file
		int		NumEventChannels;		// Number of Event channel headers in the file
		int		NumSlowChannels;		// Number of A/D channel headers in the file
		int		NumPointsWave;			// Number of data points in waveform
		int		NumPointsPreThr;		// Number of data points before crossing the threshold
		int		Year;					// when the file was created
		int		Month;					// when the file was created
		int		Day;					// when the file was created
		int		Hour;					// when the file was created
		int		Minute;					// when the file was created
		int		Second;					// when the file was created
		int     FastRead;				// 0 - none, 1 - all short events, 2 - all waveforms
		int     WaveformFreq;			// waveform sampling rate; ADFrequency above is timestamp freq 
		double  LastTimestamp;			// duration of the experimental session, in ticks
		
		// New items are only valid if Version >= 103
		char    Trodalness;				// 1 for single, 2 for stereotrode, 4 for tetrode
		char    DataTrodalness;			// trodalness of the data representation
	
		char    BitsPerSpikeSample;		// ADC resolution for spike waveforms in bits (usually 12)
		char    BitsPerSlowSample;		// ADC resolution for slow-channel data in bits (usually 12)
	
		unsigned short SpikeMaxMagnitudeMV; // the zero-to-pk volt in mV for spike waveform adc values (usually 3k00)
		unsigned short SlowMaxMagnitudeMV;  // the zero-to-pk volt in mV for slow-channel waveform adc values (usually 5k)
		char    Padding[48];			// so that this part of the header is 256 bytes
		
		
		// counters
		int     TSCounts[130][5];		// number of timestamps[channel][unit]
		int     WFCounts[130][5];		// number of waveforms[channel][unit]
		int     EVCounts[512];			// number of timestamps[event_number]
	};
	"""	

	fPL_ChanHeader = '32s32siiiiiiiii320h5ii40hi43i'
	"""
	struct PL_ChanHeader {
		char    Name[32];
		char    SIGName[32];
		int     Channel;			// DSP channel, 1-based
		int     WFRate;				// w/f per sec divided by 10
		int     SIG;				// 1 - based
		int     Ref;				// ref sig, 1- based
		int     Gain;				// 1-32, actual gain divided by 1000
		int     Filter;				// 0 or 1
		int     Threshold;			// +- 2048, a/d values
		int     Method;				// 1 - boxes, 2 - templates
		int     NUnits;				// number of sorted units
		short   Template[5][64];	// a/d values
		int     Fit[5];				// template fit 
		int     SortWidth;			// how many points to sort (template only)
		short   Boxes[5][2][4];
		int     SortBeg;
		int     Padding[43];
	};
	"""

	fPL_EventHeader = '32sii64i'
	"""	
	struct PL_EventHeader {
		char    Name[32];
		int     Channel;			// input channel, 1-based
		int     IsFrameEvent;		// frame start/stop signal
		int     Padding[64];
	};
	"""

	fPL_SlowChannelHeader = '32siiiii61i'
	"""	
	struct PL_SlowChannelHeader {
		char    Name[32];
		int     Channel;			// input channel, 0-based
		int     ADFreq; 
		int     Gain;
		int     Enabled;
		int     PreAmpGain;
		int     Padding[61];
	};
	"""

	fPL_DataBlockHeader = 'hHLhhhh'
	"""	
	// the record header used in the datafile (*.plx)
	// it is followed by NumberOfWaveforms*NumberOfWordsInWaveform
	// short integers that represent the waveform(s)
	
	struct PL_DataBlockHeader{
		short   Type;
		unsigned short   UpperByteOf5ByteTimestamp;
		unsigned long    TimeStamp;
		short   Channel;
		short   Unit;
		short   NumberOfWaveforms;
		short   NumberOfWordsInWaveform; 
	};
	"""
	
	
	fDigFileHeader = "iidiiiiiiii128sB64B191B"
	"""	
	///////////////////////////////////////////////////////////////////////////////
	// Plexon continuous data file (.DDT) File Structure Definitions
	///////////////////////////////////////////////////////////////////////////////
	
	struct DigFileHeader {
		int     Version;				// BitsPerSample field added in version 101, see below
		int     DataOffset;
		double  Freq;
		int     NChannels;
		int     Year;
		int     Month;
		int     Day;
		int     Hour;
		int     Minute;
		int     Second;
		int     Gain;					// as of version 102, this is the *preamp* gain, not NI gain
		char    Comment[128];
		unsigned char BitsPerSample;	// added for ddt version 101
		// LFS 4/10/03 - added for version 102 - actual channel gains, not index
		unsigned char ChannelGain[64]; 
		unsigned char Padding[191];
	};
	"""
