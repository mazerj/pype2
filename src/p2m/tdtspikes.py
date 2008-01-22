#!/bin/env pypenv
#
# Retrieve spike timestamps from tdt datatank using network api
#


import Numeric
import pypedata, ttank
#import time

class tdtspikes:
    # get all spikes at once, then sort into trials locally..
    # this is much faster -- seems about 1-2 secs to get all the
    # spikes, even for big datasets. Danger is if there's more than
    # 1e6 spikes...
    
    def __init__(self, pypefile, chan=0, unit=0):
        
        # note: we're just looking at the first pype record in the
        # datafile to get the necessary tank info. That's all we need
        # to find the data..
        
        pf = pypedata.PypeFile(pypefile)
        rec = pf.nth(0)
        pf.close()

        self.server = rec.params['tdt_server']
        self.tank = rec.params['tdt_tank']
        self.block = rec.params['tdt_block']

        tt = ttank.TTank(self.server)
        tt.invoke('OpenTank', self.tank, 'R')
        tt.invoke('SelectBlock', self.block)

        # trl1 is the rising edge of the gating signal
        # this query will get the timestamps for each TRL1 event in SECS
        n = tt.invoke('ReadEventsV', 1e6, 'TRL1', 0, 0, 0.0, 0.0, 'ALL')
        trl1 = tt.invoke('ParseEvInfoV', 0, n, ttank.TIME)

        # trl2 is the falling edge of the gating signal
        n = tt.invoke('ReadEventsV', 1e6, 'TRL2', 0, 0, 0.0, 0.0, 'ALL')
        trl2 = tt.invoke('ParseEvInfoV', 0, n, ttank.TIME)


        #tstart = time.time()
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
            self.sdata.append((t, c, s,))
            
        #print '%.1fms' % ((time.time() - tstart) * 1000.0)

        self.ntrials = len(trl1)

    def dump(self, out):
        out.write('#tnum time chan unit\n')
        for k in range(self.ntrials):
            (t, c, s) = self.sdata[k]
            for j in range(len(t)):
                out.write('%d\t%.1f\t%.0f\t%.0f\n' % (k, t[j], c[j], s[j],))
                #out.write('%d\t%.1f\tsig%03d%s\n' % (k, t[j],
                #                                     int(c[j]),
                #                                     chr(s[j]+ord('a')-1),))

if __name__ == '__main__':
    tdtspikes(sys.argv[1]).dump(sys.stdout)
