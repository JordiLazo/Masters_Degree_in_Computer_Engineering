import os
import re
import pylab as pl

from abc import ABC, abstractmethod

"""
=======================================================
*         TCP AGENT BASIC STRUCTURE DEFINITION        *
=======================================================
"""
class TCP_AGENT(ABC):
    """
    TCP agent base class
    """
    
    def __init__(self, transmissions=[], acks=[], rtts=[]):
        # store iput data
        self.transmissions = transmissions
        self.acks = acks
        self.rtts = rtts

        # init inner variables
        self.__current_time = 0.0
        self.__timeouts = {}
        self.__cwnd = 1 
        self. __cwnd_history = []
        self.rtt = -1
        self.rto = -1
        self.timeout = -1
        self.__acks = []

    def set_rto(self, rto):
        self.last_rtt = self.rtt
        self.rtt = rto
        self.rto = rto

    def set_cwnd(self, cwnd):
        last_cwnd =  self.__cwnd
        self.__cwnd = cwnd
        # add the new cwnd to the history (and include a interpolation with the last value)
        self.__cwnd_history.append((self.__current_time - 0.001, last_cwnd))
        self.__cwnd_history.append((self.__current_time, cwnd))

    def get_cwnd(self):
        return self.__cwnd

    def set_timeout(self, segment):   
        if self.timeout == -1:
            self.timeout = self.__current_time + self.rto
    
    def remove_timeout(self, segment=None):
        self.timeout = -1

    def check_timeout(self):
        if self.timeout == -1:
            return 
        if self.__current_time >= self.timeout:
            self.on_timeout()
            self.remove_timeout()
    
    def step(self):
        # find the next event
        if len(self.transmissions) == 0 and len(self.acks) != 0:
            next_time, segment = self.acks.pop(0)
            is_ack=True
        elif len(self.transmissions) != 0 and len(self.acks) == 0:
            next_time, segment = self.transmissions.pop(0)
            is_ack=False
        elif self.transmissions[0][0] < self.acks[0][0]:
            next_time, segment = self.transmissions.pop(0)
            is_ack=False
        else:
            next_time, segment = self.acks.pop(0)
            is_ack=True
            
        # update rto
        for time, rto in reversed(self.rtts):
            if time <= next_time:
                self.set_rto(rto)
                break
        # update current time
        self.__current_time = next_time
        self.check_timeout()
        return (is_ack, segment)

    def is_end(self):
        return len(self.transmissions) == 0 and len(self.acks) == 0
    
    def is_duplicated_ack(self, segment):
        return segment in self.__acks
    
    def registry_last_ack(self, segment):
        self.__acks.append(segment)
    
    def run(self):
        while not self.is_end():
            is_ack, segment = self.step()
            # apply action when arrive the ack
            if is_ack and not self.is_duplicated_ack(segment):
                self.registry_last_ack(segment)
                self.on_ack(segment)
            else:
                self.on_transmission(segment)
                self.set_timeout(segment)
        return self.cwd_history
    
    @property
    def cwd_history(self):
        return self.__cwnd_history
    
    @property
    def current_time(self):
        return self.__current_time

    @abstractmethod
    def on_timeout(self):
        pass

    @abstractmethod
    def on_ack(self, segment):
        pass

    @abstractmethod
    def on_transmission(self, segment):
        pass    


class TCP_AGENT_COMPLEX(ABC):
    """
    TCP agent base class
    """
    
    def __init__(self, transmissions=[], acks=[], rtts=[]):
        # store iput data
        self.transmissions = transmissions
        self.acks = acks
        self.rtts = rtts

        # init inner variables
        self.__current_time = 0.0
        self.__timeouts = {}
        self.__cwnd = 1 
        self. __cwnd_history = []
        self.rtt = -1
        self.rto = -1
        self.timeout = -1
        self.__acks = {}


    def set_rto(self, rto):
        self.last_rtt = self.rtt
        self.rtt = rto
        self.rto = rto

    def set_cwnd(self, cwnd):
        last_cwnd =  self.__cwnd
        self.__cwnd = cwnd
        # add the new cwnd to the history (and include a interpolation with the last value)
        self.__cwnd_history.append((self.__current_time - 0.001, last_cwnd))
        self.__cwnd_history.append((self.__current_time, cwnd))

    def get_cwnd(self):
        return self.__cwnd

    def set_timeout(self, segment):   
        if self.timeout == -1:
            self.timeout = self.__current_time + self.rto
            #print(f'Timeout to {self.timeout} at {self.current_time}')
    
    def remove_timeout(self, segment=None):
        self.timeout = -1

    def check_timeout(self):
        if self.timeout == -1:
            return 
        if self.__current_time >= self.timeout:
            self.on_timeout()
            self.remove_timeout()
    
    def step(self):
        # find the next event
        if len(self.transmissions) == 0 and len(self.acks) != 0:
            next_time, segment = self.acks.pop(0)
            is_ack=True
        elif len(self.transmissions) != 0 and len(self.acks) == 0:
            next_time, segment = self.transmissions.pop(0)
            is_ack=False
        elif self.transmissions[0][0] < self.acks[0][0]:
            next_time, segment = self.transmissions.pop(0)
            is_ack=False
        else:
            next_time, segment = self.acks.pop(0)
            is_ack=True
            
        # update rto
        for time, rto in reversed(self.rtts):
            if time <= next_time:
                self.set_rto(rto)
                break
        # update current time
        self.__current_time = next_time
        self.check_timeout()
        return (is_ack, segment)

    def is_end(self):
        return len(self.transmissions) == 0 and len(self.acks) == 0
    
    def is_duplicated_ack(self, segment):
         if not segment in self.__acks:
             return False
         return self.__acks[segment] >= 1
    
    def registry_last_ack(self, segment):
        #self.__acks.append(segment)
        self.__acks[segment] = self.__acks.setdefault(segment, -1) + 1
    
    def run(self):
        while not self.is_end():
            is_ack, segment = self.step()
            # apply action when arrive the ack
            if is_ack: 
                self.registry_last_ack(segment)
                if self.is_duplicated_ack(segment):
                    self.on_ack_duplicated(segment)
                else:
                    self.on_ack(segment)
            else:
                self.on_transmission(segment)
                self.set_timeout(segment)
        return self.cwd_history
    
    def get_n_ack_duplicated(self, segment):
        return self.__acks[segment]
    
    @property
    def cwd_history(self):
        return self.__cwnd_history
    
    @property
    def current_time(self):
        return self.__current_time

    @abstractmethod
    def on_timeout(self):
        pass

    @abstractmethod
    def on_ack(self, segment):
        pass

    @abstractmethod
    def on_ack_duplicated(self, segment):
        pass    

    @abstractmethod
    def on_transmission(self, segment):
        pass    

"""
=======================================================
*               TCP AGENTS DEFINITIONS                *
=======================================================
"""

class TCP_RFC793(TCP_AGENT):
    """
    Agent TCP_RFC793 classic
    """
    __CWMAX = 10
    __cwini = 1

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.set_cwnd(self.__cwini)
    
    def on_timeout(self):
        self.set_cwnd(self.__cwini)

    def on_transmission(self, segment):
        self.set_timeout(segment)

    def on_ack(self, segment):
        self.set_cwnd(self.__CWMAX)
        self.remove_timeout(segment)


class TCP_RFC793_SLOW_START(TCP_AGENT):
    __CWMAX = 10
    __cwini = 1
    __MSS = 1

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.set_cwnd(self.__cwini)
        self.cwmax = TCP_RFC793_SLOW_START.__CWMAX
    
    def on_timeout(self):
        self.set_cwnd(self.__cwini)
        self.cwmax = max(self.__cwini, self.cwmax // 2) 

    def on_transmission(self, segment):
        self.set_timeout(segment)

    def on_ack(self, segment):
        cwnd = self.get_cwnd()
        if cwnd < self.cwmax:
            self.set_cwnd(cwnd + self.__MSS)
        else:
            self.set_cwnd(cwnd + self.__MSS / cwnd)
            self.cwmax = min(self.__CWMAX, cwnd)
        self.remove_timeout(segment)


class TCP_RENO(TCP_AGENT_COMPLEX):
    __CWMAX = 10
    __cwini = 1
    __MSS = 1

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.set_cwnd(self.__cwini)
        self.cwmax = TCP_RENO.__CWMAX
        self.in_fast_recovery = False
        self.EFS = self.get_cwnd()
        self.last_segment = -1
 
    def on_timeout(self):
        self.set_cwnd(self.__cwini)
        self.cwmax = max(self.__cwini, self.cwmax // 2) 
        self.in_fast_recovery = False

    def on_transmission(self, segment):
        self.set_timeout(segment)
        # store the last segment
        self.last_segment = max(self.last_segment, segment)
       
    def on_ack(self, segment):
        cwnd = self.get_cwnd()         
        if cwnd < self.cwmax:
            self.set_cwnd(cwnd + self.__MSS)
        else:
            self.set_cwnd(cwnd + self.__MSS / cwnd)
            self.cwmax = min(self.__CWMAX, cwnd)
        self.remove_timeout()
        if self.in_fast_recovery:
            self.set_timeout(segment)
            self.in_fast_recovery = False
    
    def on_ack_duplicated(self, segment):
        if self.in_fast_recovery:
            return
        if self.get_n_ack_duplicated(segment) % 3 == 0:
            cwd = min(self.__CWMAX, self.get_cwnd()) / 2
            self.cwmax = max(self.__cwini, self.cwmax // 2) 
            self.set_cwnd(cwd)
            self.in_fast_recovery = True
            self.remove_timeout()

"""
=======================================================
*               LOAD SIMULATON FUNCTIONS              *
=======================================================
"""
def plot_cw(real_cw, estimated_cw, title=''):
    time_real, real_cw = zip(*real_cw)
    time_e, estimated_cw= zip(*estimated_cw)
    pl.figure(figsize=(15,10), dpi=80, facecolor='white', edgecolor='k')
    pl.title = title
    pl.plot(time_real, real_cw,linewidth=2,color='red',label='cw')
    pl.plot(time_e, estimated_cw,linewidth=2,color='blue',label='estimated_cw')
    pl.legend()
    pl.xlabel('Time (s)')
    pl.ylabel('CW')
    pl.ylim(0,15)
    pl.xlim(0.15)
    pl.grid()
    pl.show()


def ReadData(filename):
    time, cw = [], []
    p=re.compile('^#')
    f=open(filename)
    for line in f:
        line=line.rstrip('\n')
        a=line.split()
        if not p.match(line):
            time.append(float(a[0]))
            cw.append(float(a[1]))
    f.close()
    return time, cw

def load_trace(trace_path):
    with open(trace_path, 'r') as trace_file:
        trace = trace_file.read()
    # load transmissions
    transmissions_search = re.compile(r'^- \S+ 1 (?:(?!ack).)*', flags=re.MULTILINE) 
    transmissions = []
    for transmission in transmissions_search.findall(trace):
        info = transmission.replace('\n', '').split(' ')
        time, segment = float(info[1]), int(info[-2])
        transmissions.append((time, segment))
    # load acks
    acks_search = re.compile(r'^r \S+ \S+ 1 .*ack.*$', flags=re.MULTILINE) 
    acks = []
    for ack in acks_search.findall(trace):
        info = ack.replace('\n', '').split(' ')
        time, segment = float(info[1]), int(info[-2]) 
        acks.append((time, segment))
    return transmissions, acks


def load_rtt(rtt_path):
    rtt_history = []
    with open(rtt_path, 'r') as rtt_file:
        for rtt_line in rtt_file.readlines():
            rtt_line = rtt_line.replace('\n', '').split(' ') 
            time, rtt = float(rtt_line[0]), (float(rtt_line[1]))
            rtt_history.append((time, rtt))
    return rtt_history


def load_rto_reno(rtt_path):
    rtt_history = []
    with open(rtt_path, 'r') as rtt_file:
        for rtt_line in rtt_file.readlines():
            rtt_line = rtt_line.replace('\n', '').split(' ') 
            time, srtt, rttvar, tcp_tick = (
                float(rtt_line[0]), 
                int(rtt_line[1]), 
                int(rtt_line[2]), 
                float(rtt_line[3])
            )
            # calculate rto
            rto = ((srtt >>3) + 4 * (rttvar>>2)) * tcp_tick
            rtt_history.append((time, rto))
    return rtt_history


def run_classic():
    trace_path = os.path.join('.', 'original', 'sor.tcporig')
    rtt_path = os.path.join('.', 'original', 'rtt.txt')
    transmissions, acks = load_trace(trace_path)
    rtts = load_rtt(rtt_path)
    tcp_agent = TCP_RFC793(transmissions=transmissions, acks=acks, rtts=rtts)
    tcp_agent.run()
    time, cw = ReadData('./original/cw.tcporig')
    cw = [(t, c) for t, c in zip(time, cw)]
    plot_cw(cw, tcp_agent.cwd_history, title='TCP_RFC793 classic')
    

def run_slow_start():
    trace_path = os.path.join('.', 'slow_start', 'sor.slow')
    rtt_path = os.path.join('.', 'slow_start', 'rtt.slow')
    transmissions, acks = load_trace(trace_path)
    rtts = load_rtt(rtt_path)
    tcp_agent = TCP_RFC793_SLOW_START(transmissions=transmissions, acks=acks, rtts=rtts)
    tcp_agent.run()
    time, cw = ReadData('./slow_start/cw.slow')
    cw = [(t, c) for t, c in zip(time, cw)]
    plot_cw(cw, tcp_agent.cwd_history, title='TCP_RFC793 slow start')


def run_reno():
    trace_path = os.path.join('.', 'reno', 'sor.out')
    rtt_path = os.path.join('.', 'reno', 'rtt.out')
    transmissions, acks = load_trace(trace_path)
    rtts = load_rto_reno(rtt_path)
    tcp_agent = TCP_RENO(transmissions=transmissions, acks=acks, rtts=rtts)
    tcp_agent.run()
    time, cw = ReadData('./reno/cw.out')
    cw = [(t, c) for t, c in zip(time, cw)]
    plot_cw(cw, tcp_agent.cwd_history, title='TCP Reno')

if __name__ == '__main__':
    run_classic()
    run_slow_start()
    run_reno()
