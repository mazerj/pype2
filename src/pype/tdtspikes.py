# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-
# $Id$
#
# Retrieve spike timestamps from tdt datatank using network api (ttank.py)
#

import sys
import Numeric
import pypedata, ttank

from pypedebug import keyboard

class Spikes:
    # get all spikes at once, then sort into trials locally..
    # this is much faster -- seems about 1-2 secs to get all the
    # spikes, even for big datasets. Danger is if there's more than
    # 1e6 spikes...
    
    def __init__(self,
                 rec=None,
                 pypefile=None,
                 server=None, tank=None, block=None,
                 chan=0, unit=0, getwaves=None):
        
        # note: we're just looking at the first pype record in the
        # datafile to get the necessary tank info. That's all we need
        # to find the data..

        if rec or pypefile :
            if pypefile:
                pf = pypedata.PypeFile(pypefile)
                rec = pf.nth(0)
                pf.close()
            self.server = rec.params['tdt_server']
            self.tank = rec.params['tdt_tank']
            self.block = rec.params['tdt_block']
        else:
            self.server = server
            self.tank = tank
            self.block = block

        tt = ttank.TTank(self.server)
        if tt.invoke('OpenTank', self.tank, 'R'):
            tt.invoke('SelectBlock', self.block)
        else:
            sys.stderr.write('Missing tdt tank: %s\n' % self.tank)

        # trl1 is the rising edge of the gating signal
        # this query will get the timestamps for each TRL1 event in SECS
        n = tt.invoke('ReadEventsV', 1e6, 'TRL1', 0, 0, 0.0, 0.0, 'ALL')
        trl1 = tt.invoke('ParseEvInfoV', 0, n, ttank.TIME)

        # trl2 is the falling edge of the gating signal
        n = tt.invoke('ReadEventsV', 1e6, 'TRL2', 0, 0, 0.0, 0.0, 'ALL')
        trl2 = tt.invoke('ParseEvInfoV', 0, n, ttank.TIME)

        if len(trl1) != len(trl2):
            # this probably means a new record came in between requesting
            # trl1 and trl2, so truncate the data to only look at complete
            # trials
            sys.stderr.write('Warning: incomplete trial in tdt tank.\n')
            trl1 = trl1[0:len(trl2)]

        # if requested -- pull down the analog snipet waveform data:
        # still needs to be massaged to adjust timestmps..
        if getwaves:
            nsnip = tt.invoke('ReadEventsV', 1e6, 'Snip', 0, 0, 0.0, 0.0, 'ALL')
            self.waves = tt.invoke('ParseEvV', 0, nsnip)
            self.channel = tt.invoke('ParseEvInfoV', 0, nsnip, ttank.CHANNUM)
            self.sortnum = tt.invoke('ParseEvInfoV', 0, nsnip, ttank.SORTNUM)
            self.ts = tt.invoke('ParseEvInfoV', 0, nsnip, ttank.TIME)

        start, stop = trl1[0], trl2[-1]
        # get number of spike/snip's between start and stop
        #   chan=0 for any channel
        #   unit=0 for any unit (aka sortcode)
        n = tt.invoke('ReadEventsV', 1e6, 'Snip', \
                      chan, unit, start, stop, 'ALL')

        # get timestamps, channel (electrode), sortnum (unit) for spikes
        tall = Numeric.array(tt.invoke('ParseEvInfoV', 0, n,  ttank.TIME))
        call = Numeric.array(tt.invoke('ParseEvInfoV', 0, n,  ttank.CHANNUM))
        sall = Numeric.array(tt.invoke('ParseEvInfoV', 0, n,  ttank.SORTNUM))
        
        self.sdata = []
        for k in range(len(trl1)):
            mask = Numeric.logical_and(Numeric.greater_equal(tall, trl1[k]),
                                       Numeric.less_equal(tall, trl2[k]))
            t = (Numeric.compress(mask, tall) - trl1[k]) * 1000.0
            c = Numeric.compress(mask, call)
            s = Numeric.compress(mask, sall)
            sigs = []
            for j in range(len(s)):
                sigs.append('%03d%c' % (c[j], chr(int(s[j])+ord('a')-1),))
            self.sdata.append((t, c, s, sigs,))
            
        self.ntrials = len(trl1)

    def dump(self, out):
        #out.write('#tnum time chan unit\n')
        for k in range(self.ntrials):
            (t, c, s, sigs) = self.sdata[k]
            for j in range(len(t)):
                out.write('%d\t%.1f\t%.0f\t%.0f\n' % (k, t[j], c[j], s[j],))
                #out.write('%d\t%.1f\t%s\n' % (k, t[j], int(c[j]), sigs[j].))

    def info(self, out):
        out.write('server=%s\n' % self.server)
        out.write('tank=%s\n' % self.tank)
        out.write('block=%s\n' % self.block)
        out.write('channels with spikes:\n')
        units = {}
        for k in range(self.ntrials):
            (t, c, s, sigs) = self.sdata[k]
            for j in range(len(t)):
                if s[j]:
                    units[sigs[j]] = 1
        k = units.keys()
        k.sort()
        for sig in k:
            out.write(' %s\n' % sig)

if __name__ == '__main__':
    sys.stderr.write('%s should never be loaded as main.\n' % __file__)
    sys.exit(1)