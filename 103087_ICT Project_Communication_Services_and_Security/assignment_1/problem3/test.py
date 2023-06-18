import re
import os
from plot import plot_cw, ReadData

def load_trace(trace_path):
    with open(trace_path, 'r') as trace_file:
        trace = trace_file.read()
    events = []
    # load acks
    acks_search = re.compile(r'^r \S+ \S+ 1 .*ack.*$', flags=re.MULTILINE)
    for ack in acks_search.findall(trace):
        info = ack.replace('\n', '').split(' ')
        time, segment = float(info[1]), int(info[-2]) 
        events.append((time, 'ACK', segment))
    # load transmissions
    transmissions_search = re.compile(r'^- \S+ 1 (?:(?!ack).)*', flags=re.MULTILINE) 
    for transmission in transmissions_search.findall(trace):
        info = transmission.replace('\n', '').split(' ')
        time, segment = float(info[1]), int(info[-2])
        events.append((time, 'TRANSMISSION',segment))
    # sort events
    events.sort(key=lambda x: x[0])
    return events


def show_trace():
    trace_path = os.path.join('.', 'reno', 'reno_RED', 'sor.out')
    events = load_trace(trace_path)
    for event in events:
        time, event_type, segment = event
        if time >= 20 and time <=40:
            print(f'{time} : {event_type}-{segment}')

def new_reno():
    trace_path = os.path.join('.', 'new_reno', 'cw.out')
    trace_path_reno = os.path.join('.', 'reno', 'cw.out')
    time, cw = ReadData(trace_path)
    cw_new_reno = [(t, c) for t, c in zip(time, cw)]

    time, cw = ReadData(trace_path_reno)
    cw_reno = [(t, c) for t, c in zip(time, cw)]
    plot_cw(cw_new_reno, cw_reno)


def reno_red_cwd():
    trace_path = os.path.join('.', 'reno', 'cw.out')
    trace_path_red = os.path.join('.', 'reno', 'reno_red', 'cw.out')
    time, cw = ReadData(trace_path)
    cw_reno = [(t, c) for t, c in zip(time, cw)]

    time, cw = ReadData(trace_path_red)
    cw_reno_red = [(t, c) for t, c in zip(time, cw)]
    plot_cw(cw_reno, cw_reno_red)    

#new_reno()
#show_trace()
reno_red_cwd()