import re
import os
import pylab as pl
import numpy as np
import sys

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
    cw = [(t, c) for t, c in zip(time, cw)]
    return cw

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
    print(rtt_path)
    rtt_history = []
    with open(rtt_path, 'r') as rtt_file:
        for rtt_line in rtt_file.readlines():
            rtt_line = rtt_line.replace('\n', '').split(' ') 
            time, srtt, tcp_tick = (
                float(rtt_line[0]), 
                int(rtt_line[1]), 
                float(rtt_line[3])
            )
            # calculate rto
            rtt = (srtt >> 3) * tcp_tick
            rtt_history.append((time, rtt))
    return rtt_history


def show_trace():
    trace_path = os.path.join('.', 'reno', 'sor.out')
    transmissions, acks= load_trace(trace_path)
    transmissions = [(time, 'TRASNMISSION', segment) for time, segment in transmissions]
    acks = [(time, 'ACK', segment) for time, segment in acks]
    
    events = acks + transmissions
    events.sort(key=lambda x: x[0])

    for event in events:
        time, event_type, segment = event
        #print(f'{time} : {event_type}-{segment}')
        if time >= 19 and time <=30:
            print(f'{time} : {event_type}-{segment}')


def count_retrasmissions(transmissions):
    segments = []
    n_retrasmissions = 0
    for transmission in transmissions:
        segment = transmission[1]
        if segment in segments:
            n_retrasmissions += 1
        else:
            segments.append(segment)
    return n_retrasmissions

def measure_throughput(cw, rtt):
    throughputs = []
    for time, current_cw in cw:
        valid_rtt = list(filter(lambda x: x[0]<= time, rtt))
        if len(valid_rtt) == 0:
            continue
        current_rtt = valid_rtt[-1][1]
        if current_rtt == 0:
            throughput = 0
        else:
            throughput = current_cw * 1000 * 8 / (current_rtt * 8000)
        throughputs.append((time, throughput))
    return throughputs

                
def extract_trace_info(trace_path_dir):
    trace_path = os.path.join(trace_path_dir, 'sor.out')
    rtt_path = os.path.join(trace_path_dir, 'rtt.out')
    cw_path = os.path.join(trace_path_dir, 'cw.out')
    transmissions, acks = load_trace(trace_path)
    n_retransmissions = count_retrasmissions(transmissions)
    cw = ReadData(cw_path)
    rtt = load_rtt(rtt_path)


    throughput = measure_throughput(cw, rtt)
    return {
        'n_retransmissions': n_retransmissions,
        'throughput': throughput,
        'cw': cw
    }


def plot_cw_cmp(real_cw, estimated_cw, lb1, lb2):
    time_real, real_cw = zip(*real_cw)
    time_e, estimated_cw= zip(*estimated_cw)
    pl.figure(figsize=(15,10), dpi=80, facecolor='white', edgecolor='k')
    pl.plot(time_real, real_cw,linewidth=2,color='red',label=f'cw_{lb1}')
    pl.plot(time_e, estimated_cw,linewidth=2,color='blue',label=f'cw_{lb2}')
    pl.legend()
    pl.xlabel('Time (s)')
    pl.ylabel('CW')
    pl.ylim(0,15)
    pl.xlim(0.15)
    pl.grid()
    pl.show()

def plot_throughput(th_1, th_2, lb1, lb2, title=''):
    time_real, real_cw = zip(*th_1)
    time_e, estimated_cw= zip(*th_2)
    print(f'{lb1}_mean:', np.mean(real_cw))
    print(f'{lb2}_mean:', np.mean(estimated_cw))
    fig = pl.figure(figsize=(15,10), dpi=80, facecolor='white', edgecolor='k')
    pl.title(title)
    pl.plot(time_real, real_cw,linewidth=2,color='red',label=lb1)
    pl.plot(time_e, estimated_cw,linewidth=2,color='blue',label=lb2)
    pl.legend()
    pl.xlabel('Time (s)')
    pl.ylabel('KBytes/s')
    pl.ylim(0,15)
    pl.xlim(0.15)
    pl.grid()
    pl.show()


show_trace()

# plot cw
cw_reno = ReadData('reno/cw.out')
cw_new_reno = ReadData('reno/reno_RED/cw.out')
#plot_cw_cmp(cw_reno, cw_new_reno, 'Reno', 'Reno + RED')



reno_info = extract_trace_info('reno')
new_reno_info = extract_trace_info('new_reno')
reno_red_info = extract_trace_info('reno/reno_RED')
#print(reno_info)
#print(new_reno_info)

throughput_reno = reno_info['throughput']
throughput_new_reno = new_reno_info['throughput']
plot_throughput(throughput_reno, throughput_new_reno, 'reno', 'new_reno')

throughput_reno_red = reno_red_info['throughput']

#plot_throughput(throughput_reno, throughput_reno_red, 'reno', 'reno_red', title='Throughput TCP Reno vs TCP Reno + RED')




