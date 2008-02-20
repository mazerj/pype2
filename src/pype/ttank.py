# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
#
# TTank.X ONLY interface  -- see tdt.py for complete docs..
#

import sys, time
import socket
import pickle

class TDTError(Exception): pass

# event-type codes from TDT docs
WSIZE=1
ETYPE=2
ECODE=3
CHANNUM=4
SORTNUM=5
TIME=6
DATAFMT=8
RATE=9

TTank=None
DEBUG=1

class _Socket:
	def Send(self, data):
		import struct
		self.conn.send(struct.pack('!I', len(data)))
		return self.conn.sendall(data)
	
	def Receive(self, size=8192):
		import struct
		buf = self.conn.recv(struct.calcsize('!I'))
		if not len(buf):
			raise EOFError, '_Socket.Receive()'
		else:
			N = struct.unpack('!I', buf)[0]
			data = ''
			while len(data) < N:
				packet = self.conn.recv(size)
				data = data + packet
			return data

	def Close(self):
		self.sock.close()
		
class _SocketServer(_Socket):
	def __init__(self, host = socket.gethostname(), port = 10001):
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

	def Connect(self, remoteHost = socket.gethostname(), remotePort = 10001):
		self.remoteHost, self.remotePort = remoteHost, remotePort
		# set to non-blocking..
		self.conn.settimeout(None)
		# generates exception on failure-to-connect
		self.conn.connect((self.remoteHost, self.remotePort))
		
	def __str__(self):
		return '<_SocketClient '+\
			   str(self.remoteHost)+':'+str(self.remotePort)+'>'

class TTankServer:
	def __init__(self, Server='Local', tk=None):
		# this throws ImportError under linxu; should be caught
		import win32com.client

		# only need global decl to Modify TTank!
		global TTank
		self.Server = Server
		
		TTank = win32com.client.Dispatch('TTank.X')

	def log(self, msg=None):
		import sys, os, time
		if msg is None:
			sys.stderr.write('\n')
		else:
			for ln in msg.split('\n'):
				sys.stderr.write('%02d:%02d:%02d ' % \
								 time.localtime(time.time())[3:6])
				sys.stderr.write('%s: %s\n' % \
								 (os.path.basename(sys.argv[0]), ln))

	def connect(self):
		"""
		Set up connections to the TDT COM server
		"""
		if TTank.ConnectServer(self.Server, 'Me'):
			self.log('Connected to %s:TTank.X' % self.Server)
			return 1
		else:
			self.log('No connection %s:TTank.X' % self.Server)
			return 0

	def disconnect(self):
		TTank.CloseTank()
		TTank.ReleaseServer()

	def listen(self):
		import traceback
		
		server = _SocketServer()
		while 1:
			self.log('Waiting for client connection')
			server.Listen()
			self.log('Received connection from %s' % server.remoteHost)

			if not self.connect():
				raise TDTError, 'TTank.X ActiveX control not installed'

			
			self.log('Recieving commands')
			while 1:
				try:
					x = pickle.loads(server.Receive())
				except EOFError:
					# client closed connection
					break

				et = time.time()
				try:
					ok = 1
					(obj, method, args) = x
					fn = eval('%s.%s' % (obj, method))
					result = apply(fn, args)
				except:
					# send error info back to client for debugging..
					ok = None
					result = sys.exc_info()
					traceback.print_tb(tb)
				et = time.time() - et
				server.Send(pickle.dumps((ok, result)))
				if DEBUG:
					#self.log('(%s,"%s") <- %s' % (ok, result, x))
					self.log('(%s,??) <- ..%s..' % (ok, x[1]))
					self.log('[%.3fs elapsed]' % (et, ))
					
				if ok is None:
					self.log(sys.exc_value)
					
			self.log('Client closed connection.')
			self.disconnect()
		server.Close()

	
class TTank:
	def __init__(self, server):
		self.server = server
		self.client = _SocketClient()
		try:
			self.client.Connect(self.server)
		except socket.error:
			raise TDTError, 'TTank server @ %s not available' % self.server
		
	def __repr__(self):
		return '<TTank server=%s>' % (self.server,)

	def close_conn(self):
		"""
		Shut down connection.
		"""
		self.client.Close()
		self.client = None

	def _send(self, cmdtuple):
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

	def invoke(self, method, *args):
		import types

		(ok, result) = self._send(('TTank', method, args,))
		if ok:
			return result
		else:
			raise TDTError, 'TTank Error; cmd=<%s>; err=<%s>' % (method, result)

def loopforever():
	try:
		import win32com
		# we're running on windows, start up the read-eval-print loop
	except ImportError:
		# we're running on linux, return now!
		return 0
	
	while 1:
		s = TTankServer()
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
