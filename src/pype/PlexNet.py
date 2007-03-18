#! /usr/bin/env python
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

import sys
import struct
import socket
import threading
import time, random

from PlexHeaders import *

class PlexNet:
	def __init__(self, host, port=6000, waveforms=0):
		self.__status = 'No Connection'

		self.host = host
		self.port = port
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__sock.connect((self.host, self.port))
		self.__status = 'connected'
		
		self.__last_NumMMFDropped = 0
		self.__mmf_drops = 0
		self.__tank = []
		self.__neurons = {}
		
		packet = [0] * 6
		packet[0] = Plex.PLEXNET_CMD_SET_TRANSFER_MODE
		packet[1] = 1					# want timestamps?
		packet[2] = waveforms			# want waveforms?
		packet[3] = 0					# want analog data?
		packet[4] = 1					# chanel from
		packet[5] = 16					# chanel to

		self.__put('6i', packet)
		data = self.__get()

		# these values are precomputed to speed things up:
		self.__db_header = 'iiii'
		self.__db_header_size = struct.calcsize(self.__db_header)
		self.__db_size = struct.calcsize(Plex.fPL_DataBlockHeader)

		self.__lock = threading.Lock()
		sys.stderr.write('starting plexnet thread\n')
		threading.Thread(target=self.run).start()

	def __del__(self):
		try:
			self.__put('h', [Plex.PLEXNET_CMD_DISCONNECT,])
		except:
			pass
		self.__sock.close()

	def __put(self, format, packet):
		# pack data into binary format for transfer
		bin = apply(struct.pack, [format,] + packet)

		# pad packet to full length with zeros
		bin = bin + "\0" * (Plex.PACKETSIZE-len(bin))
		self.__sock.send(bin)

	def __get(self):
		nbytes = 0
		while nbytes < Plex.PACKETSIZE:
			data = self.__sock.recv(Plex.PACKETSIZE)
			nbytes = nbytes + len(data)
		return data

	def start_data(self):
		self.__put('i', [Plex.PLEXNET_CMD_START_DATA_PUMP,])

	def stop_data(self):
		self.__put('i', [Plex.PLEXNET_CMD_STOP_DATA_PUMP,])

	def pump(self):
		data = self.__get()

		(unknown1, unknown2, NumServerDropped, NumMMFDropped) = \
				   struct.unpack(self.__db_header, data[:self.__db_header_size])

		#print unknown1, unknown2, NumServerDropped, NumMMFDropped

		if (NumMMFDropped - self.__last_NumMMFDropped) > 0:
			self.__last_NumMMFDropped = NumMMFDropped
			sys.stderr.write("PlexNet: Warning, MMF dropout!!\n")
			sys.stderr.write("PlexNet: Consider power cycling MAP box...\n")
			self.__mmf_drops = self.__mmf_drops + 1

		if NumServerDropped > 0:
			sys.stderr.write("PlexNet: NumServerDropped=%d\n" %
							 NumServerDropped)
			sys.stderr.write("PlexNet: This shouldn't happen; tell Jamie\n")

		pos = 16
		events = []
		while (pos + self.__db_size) <= Plex.PACKETSIZE:
			db = struct.unpack(Plex.fPL_DataBlockHeader,
							   data[pos:pos+self.__db_size])

			if db[0] == 0:			# db[1] Type // empty block
				print "?empty?"
				break

			if db[0] == -1:
				# end of packet
				break
			pos = pos + self.__db_size

			(Type, UpperTS, TimeStamp, Channel, \
			 Unit, nWaveforms, nWordsInWaveform) = db

			# compute 5 byte timestamp as L type (long int)
			ts = (1L<<24)+TimeStamp
			
			if nWaveforms > 0:
				# waveform samples/words are 2-bytes each
				wavesize = nWaveforms * nWordsInWaveform
				waveform = data[pos:pos+(wavesize*2)]
				waveform = struct.unpack('h' * (len(waveform)/2), waveform)
				pos = pos + (wavesize * 2)
			else:
				waveform = None
				
			# note: if type==4, then this is a non-waveform event, like
			# the trigger pulse. Channel contains the event id. I think
			# it's 258 for start and 259 for stop trial/recording.
			events.append((Type, Channel, Unit, ts, waveform))
			
		return events

	def run(self):
		self.start_data()
		while 1:
			# query the socket for a new set of plexon evens
			eventlist = self.pump()

			# Now crunch through the events. The appended None dummy event
			# will force a check on the tank status w/o requiring an
			# additional acquire/release cylce on the lock. This allows
			# the thread to correctly terminate and allow pype to cleanly
			# exit when no spike data is coming in.
			for e in eventlist + [None]:
				try:
					self.__lock.acquire()
					if self.__tank is None:
						# this is the termination signal from the main thread
						return
					if e is not None:
						self.__tank.append(e)
						self.__neurons[(e[1],e[2])] = 1
				finally:
					if self.__tank is not None:
						self.__status = "[%05d]" % len(self.__tank)
					self.__lock.release()
		self.stop_data()

	def drain(self, terminate=0):
		self.__lock.acquire()
		t, self.__tank, ndrops = self.__tank, [], self.__mmf_drops
		self.__mmf_drops = 0
		if terminate:
			# signal collection thread to terminate next possible chance
			self.__tank = None
		self.__lock.release()
		return t, ndrops

	def neuronlist(self, clear=0):
		"""Get list of recently seen neurons"""
		self.__lock.acquire()
		n = self.__neurons.keys()
		if clear:
			self.__neurons = {}
		self.__lock.release()
		return n

	def status(self):
		self.__lock.acquire()
		s = self.__status
		self.__lock.release()
		return s

if __name__ == '__main__':
	p = PlexNet("192.168.1.111", 6000)
	for i in range(3):
		time.sleep(1)
		events, ndrops = p.drain()
		print "%d events (%d)" % (len(events), ndrops)
	p.drain(terminate=1)
	print "drained."
