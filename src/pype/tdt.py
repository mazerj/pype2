# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#
# Simple python client/server system to provide remote access
# to TDT COM interface from a linux box (or anyother system
# running python) over the network.
#
# NOTE -- this implments a *simple* server -- only one client
#         at a time!
#
############################################################################
# SERVER SIDE
############################################################################
#
# This module, WHEN RUN AS A PROGRAM ON A WINDOWS MACHINE, implments
# the server. At startup, the program tries to connect to TDevAcc
# (direct access to workbench) and a TTank (data tank) COM
# services. Then it just listens for incomming connections
# on port 10000 (from pype or anything else on the the
# network).
#
# The client then sends commands as pickled strings. For each
# picked string the client sends, the server will eval() the
# string and return a pickled tuple of length 2. Either:
#   (1, result-object)
#   (None, None)
# The first value indicates whether an error occured during
# execution. If it's 1, then execution was a sucess and the
# result is returned.
#
############################################################################
# CLIENT SIDE
############################################################################
#
#
#
############################################################################
# Socket Classes derrived from:
#    Socket utilities class by Amey R Pathak
#    src: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/200946
############################################################################

import sys
import errno
import time
import socket
import pickle

try:
	from pypedebug import keyboard
except ImportError:
	pass
		
try:
	from Numeric import *
except ImportError:
	pass

class TDTError(Exception): pass

# OpenEx run modes
IDLE = 0								# dsp completely idle
STANDBY = 1								# running, no display, no tank..
PREVIEW = 2								# running, not saving to tank
RECORD = 3								# running and saving all data

PORT=10000
DEBUG=1

def log(msg=None):
	import sys, os, time
	if msg is None:
		sys.stderr.write('\n')
	else:
		for ln in msg.split('\n'):
			sys.stderr.write('%02d:%02d:%02d ' % \
							 time.localtime(time.time())[3:6])
			sys.stderr.write('%s: %s\n' % (os.path.basename(sys.argv[0]), ln))

class _Socket:
	def Send(self, data):
		import struct
		self.conn.send(struct.pack('!I', len(data)))
		return self.conn.sendall(data)

	def _recv(self, nbytes):
		while 1:
			try:
				buf = self.conn.recv(nbytes)
				return buf
			except socket.error:
				etype, evalue, traceback = sys.exc_info()
				(errno, err) = evalue
				if evalue == errno.EINTER:
					# unexpected SIGNAL came in before data, just retry..
					# this is likely to be something like a fixwin break
					# during data collection..
					
					# I'm pretty sure this only happens when no data has
					# been read, so there should be no loss..
					sys.stderr.write('warning: tdt recv caught EINTR\n')
				elif evalue == errno.EBUSY:
					# not sure what causes this one..
					sys.stderr.write('warning: tdt recv caught EBUSY\n')
				else:
					# otherwise, god knows what caused it, better raise
					# a proper exception for debuggin..
					raise
	
	def Receive(self, size=1024):
		import struct
		buf = self._recv(struct.calcsize('!I'))
		if not len(buf):
			raise EOFError, '_Socket.Receive()'
		else:
			N = struct.unpack('!I', buf)[0]
			data = ''
			while len(data) < N:
				packet = self._recv(size)
				data = data + packet
			return data

	def Close(self):
		self.sock.close()
		
class _SocketServer(_Socket):
	def __init__(self, host = socket.gethostname(), port = PORT):
		self.host, self.port = host, port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((self.host, self.port))
		self.remoteHost = None
		
	def Listen(self):
		self.sock.listen(1)
		self.conn, self.remoteHost = self.sock.accept()
		self.remoteHost = self.remoteHost[0]
			
	def __str__(self):
		return '<_SocketServer '+\
			   str(self.host)+':'+str(self.port)+'>'

class _SocketClient(_Socket):
	def __init__(self):
		self.host, self.port = None, None
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def Connect(self, remoteHost = socket.gethostname(), remotePort = PORT):
		self.remoteHost, self.remotePort = remoteHost, remotePort
		# non blocking..
		self.conn.settimeout(None)
		# generates exception on failure-to-connect
		self.conn.connect((self.remoteHost, self.remotePort))
		
	def __str__(self):
		return '<_SocketClient '+\
			   str(self.remoteHost)+':'+str(self.remotePort)+'>'

class TDTServer:
	"""
	Wrapper object for the server. To setup a server, you simply
	do something like this:
	
	  s = Server()
	  s.listen()

	The server doesn't connect to the TDT subsystem until a client
	get's connected. If it can't make the connection, it reports
	an error by pushing a '0' instead of a '1' back to the client
	upon connection.

	This means you can leave the python server running all the time
	and it will connect to the TDT stuff at will...

	** This should be instantiated on a Windows system ONLY **
	"""
	def __init__(self, Server='Local', tk=None):
		# importing win32com stuff will fail on a unix box, so be
		# ready to print an error message and die..
		import win32com.client
		global TDevAcc, TTank

		self.Server = Server
		TDevAcc = win32com.client.Dispatch('TDevAcc.X')
		TTank = win32com.client.Dispatch('TTank.X')

	def connect(self):
		"""
		Set up connections to the TDT COM server
		"""
		global TDevAcc, TTank
			
		log('Connecting to TDT servers...')

		connections = 0
		
		if TDevAcc.ConnectServer(self.Server):
			log('..connect to %s:TDevAcc' % self.Server)
			connections = connections + 1
		else:
			log('..no connection to %s:TDevAcc' % self.Server)
			
		if TTank.ConnectServer(self.Server, 'Me'):
			log('..connect to %s:TTank.X' % self.Server)
			connections = connections + 2
		else:
			log('..no connection %s:TTank.X' % self.Server)
			
		return connections

	def listen(self):
		global TDevAcc, TTank
		import traceback

		while 1:
			server = _SocketServer()
			log('Waiting for client..')
			server.Listen()
			log('Received connection from %s' % server.remoteHost)

			connections = self.connect()
			server.Send(pickle.dumps(connections))
			log('Recieving commands')
			while 1:
				try:
					x = pickle.loads(server.Receive())
				except EOFError:
					# client closed connection
					break

				et = time.time()
				try:
					# new original string-based mode..
					ok = 1
					(obj, method, args) = x
					fn = eval('%s.%s' % (obj, method))
					result = apply(fn, args)
					time.sleep(10)
				except:
					# send error info back to client for debugging..
					ok = None
					result = sys.exc_info()
					traceback.print_tb(result[2])
					result = result[0:1]
				et = time.time() - et
				server.Send(pickle.dumps((ok, result)))
				if DEBUG:
					log('(%s,"%s") <- %s' % (ok, result, x))
					log('[%.3fs elapsed]' % (et, ))
					
				if ok is None:
					log('%s' % sys.exc_value)
					
			log("client closed connection.")
			if TTank:
				log('TTank.X closing tank')
				TTank.CloseTank()
				log('TTank.X releasing server')
				TTank.ReleaseServer()
			if TDevAcc:
				if TDevAcc.CheckServerConnection():
					log('TDevAcc closing connection')
					TDevAcc.CloseConnection()

			server.Close()
			log()
			
class TDTClient:
	def __init__(self, server):
		self.server = server
		self.client = None
		self.open_conn()
		
	def __repr__(self):
		return '<TDTClient server=%s TDevAcc=%d TTank=%d>' % \
			   (self.server, self.gotTDevAcc, self.gotTTank)

	def open_conn(self):
		"""
		Connect to the remote server sepcified during initialization
		and exchange sync information.

		The default timeout (set above) is 1s, so if this throws and
		exception or error, it's likely the server's not running on
		the TDT size.
		"""
		if self.client is None:
			self.client = _SocketClient()
			self.client.Connect(self.server)
		c = pickle.loads(self.client.Receive())
		self.gotTDevAcc = (1 & c) > 0
		self.gotTTank = (2 & c) > 0
		
	def close_conn(self):
		"""
		Shut down connection.
		"""
		self.client.Close()
		self.client = None

	def _sendtuple(self, cmdtuple):
		"""
		Send a command string for remove evaluation to the server.
		Command string (cmd) should be a valid python expression
		that can be eval'ed in the remote envrionment. Access to
		the Tucker-Davis API is via:
		  TDevAcc (for the direct DSP interface), or,
		  TTank (for access to the data tank)

		The return value is a pair: (statusFlag, resultValue), where
		statusFlag is 1 for normal evaluation and 0 for an error and
		resultValue is the actual value returned by the function
		call (the value is pickled on the Server side and returns, so
		data typing should be correctly preserved and propagated.
		"""
		try:
			self.client.Send(pickle.dumps(cmdtuple))
			p = self.client.Receive()
			(ok, result) = pickle.loads(p)
		finally:
			pass
		return (ok, result)

	def tdev_invoke(self, method, *args):
		import types

		(ok, result) = self._sendtuple(('TDevAcc', method, args,))
		if ok:
			return result
		else:
			raise TDTError, 'TDev Error; cmd=<%s>; err=<%s>' % (method, result)

	def ttank_invoke(self, method, *args):
		import types

		(ok, result) = self._sendtuple(('TTank', method, args,))
		if ok:
			return result
		else:
			raise TDTError, 'TTank Error; cmd=<%s>; err=<%s>' % (method, result)

	def tdev_mode(self, mode=None, name=None, wait=None):
		"""
		Query current run mode for the TDT device.

		Run modes are defined by TDT as follows (and also declared
		as global constants/vars in this file):
		  IDLE = 0		# dsp completely idle
		  STANDBY = 1	# running, no display, no tank..
		  PREVIEW = 2	# running, not saving to tank
		  RECORD = 3	# running and saving all data
		"""
		if not mode is None:
			self.tdev_invoke('SetSysMode', mode)
			while wait:
				if self.tdev_invoke('GetSysMode') == mode:
					break
		else:
			r = self.tdev_invoke('GetSysMode')
			if name:
				modes = { IDLE:'IDLE', STANDBY:'STANDBY',
						  PREVIEW:'PREVIEW', RECORD:'RECORD'}
				r = modes[r]
		r = self.tdev_invoke('GetSysMode')
		return r

	def tdev_tnum(self, reset=None):
		"""
		Read trial count, or if reset==1 reset the counter to zero. This
		should really be done when OpenEx is in standby mode..
		"""
		if reset:
			self.tdev_invoke('SetTargetVal', 'Amp1.TNumRst', 1.0)
			while 1:
				if self.tdev_invoke('GetTargetVal', 'Amp1.TNum') == 0:
					break
		return self.tdev_invoke('GetTargetVal', 'Amp1.TNum')

	def tdev_chaninfo(self):
		"""
		Figure out number of analog channels and length of spike snippet.
		The actual length of the snippet is hoopsize/3 points, since
		cSnip refers to the hoops, not the waveform.
		"""
		n = 1
		while 1:
			s = self.tdev_invoke('GetTargetSize',
								 'Amp1.cSnip~%d' % n)
			if s < 0:
				self.tdev_invoke('SetSysMode', PREVIEW)
				s = self.tdev_invoke('GetTargetSize',
									 'Amp1.cSnip~%d' % n)
			if s == 0:
				break
			if n == 1:
				hoopsize = s
			n = n + 1
		return (n-1, hoopsize/3)

	def getblock(self):
		"""
		Query current block info -- this is enough info to find the current
		data record later (assuming tank doesn't get deleted...)
		"""
		return (self.server,
				self.tdev_invoke('GetTankName'),
				self.ttank_invoke('GetHotBlock'),
				self.tdev_invoke('GetTargetVal', 'Amp1.TNum'))

	def tdev_newblock(self, record=1):
		"""
		Start a new block in the current tank. Each block corresponds
		to a single run. If record==1, then a new block is started for
		recording. Otherwise, the current block is terminated and the
		system is left in standby mode.

		Basically, you should call newblock(record=1) at the start
		of a run and then neweblock(record=0) at the end.

		NOTE: In IDLE and STANDBY mode, GetHotBlock() returns an empty
		string, in PREVIEW mode 'TempBlock' and in RECORD mode a true
		block name (typically 'Block-NNN')

		RETURNS: (servername, tankname, blockname); this should be enough
		info to track down the location of the record no matter what..
		"""
		# set OpenEx to STANDBY and wait for this to register in the
		# tank as a change in the block name to '' (or if it was already
		# in STANDBY mode, we're good to go..

		self.tdev_mode(PREVIEW)

		tank = self.tdev_invoke('GetTankName')
		err = self.ttank_invoke('OpenTank', tank, 'R')

		while 1:
			oldblock = self.ttank_invoke('GetHotBlock')
			if str(oldblock) == 'TempBlk' or len(oldblock) == 0:
				break

		# actually, I do not think this is necessary, as long as the
		# tnum's are unique, so just let it count up continuously..
		# reset the trial counter
		# self.tdev_tnum(reset=1)

		# switch back to record mode and wait for this to get into the
		# tank, so we can store the block name for easy access later..
		if record:
			self.tdev_mode(RECORD)
			while 1:
				newblock = self.ttank_invoke('GetHotBlock')
				if not (newblock == oldblock) and len(newblock) > 0:
					break
		else:
			self.tdev_mode(PREVIEW)
			newblock = self.ttank_invoke('GetHotBlock')
			
		# and return the tank & block name --> this is enough info to
		# find the record later..
		tank = self.tdev_invoke('GetTankName')
		return (self.server, str(tank), str(newblock))


	def tdev_sortparams(self, params=None):
		"""
		Get or set current sort parameters (aka hoop settings). If called
		with no arguments, current settings are returned. Otherwise, the
		params arg specifies a new set of settings to setup
		"""

		# just assume 16 channels to be safe...
		nchans = 16
		sniplen = -1
		while sniplen < 0:
			sniplen = self.tdev_invoke('GetTargetSize',
									   'Amp1.cSnip~%d' % 1)
			if sniplen < 0:
				# sniplen means circuit hasn't been started up yet, so
				# start it going and try again..
				self.tdev_invoke('SetSysMode', PREVIEW)

		if params is None:
			params = {}
			for n in range(1, nchans+1):
				try:
					params[n, 'thresh'] = self.tdev_invoke('GetTargetVal',
														   'Amp1.aSnip~%d' % n)
				except ValueError:
					# not sure what this is --> comes back as -1.#IND..
					params[n, 'thresh'] = 1.0
				params[n, 'hoops'] = self.tdev_invoke('ReadTargetV',
													  'Amp1.cSnip~%d' % n,
													  0, sniplen)
			return params
		else:
			for n in range(1, nchans+1):
				t = params[n, 'thresh']
				h = params[n, 'hoops']
				self.tdev_invoke('SetTargetVal', 'Amp1.aSnip~%d' % n, t)
				self.tdev_invoke('WriteTargetVEX',
								 'Amp1.cSnip~%d' % n, 0, 'F32', h)
			
def loopforever():
	while 1:
		try:
			s = TDTServer()
		except ImportError:
			return 0
		try:
			s.listen()
		except:
			log('-----------------------------')
			log('Server-side near fatal error in loopforever:')
			log(sys.exc_value)
			log('-----------------------------')
			del s

if __name__ == '__main__':
	loopforever()
	sys.stderr.write("Don't run me under linux!\n")
	sys.exit(0)
