"""
PROBLEM 2

    DESCRIPTION
        The goal of this script is the implementation of Weighted Fair Quering. One point worth noting about this implementation,
        is the simulation of queues. Instead of filling the queues as the segments arrive, these queues are filled once the simulation
        is loaded. Later during execution, those segments whose arrival time is greater than the current time are ignored.
    
    DATA REPRESENTATION
        -Packet:
            - a_i : arrival time
            - s_i : packet length
            - flow : flow indentifier
            - f_i : estimated finalization time
            
    HOW TO RUN
        To execute the script, the following arguments must be passed:
          - queues_weights: weights of the queues
          - filename: path of with the segements to be scheduled
    
"""
import argparse
import sys
from itertools import count
from dataclasses import dataclass, field

@dataclass
class Packet:
    a_i : float
    s_i : int 
    flow : int 
    f_i : int = -1
    id : int = field(default_factory=count().__next__)

    def __getitem__(self, ind): 
        return [self.a_i, self.s_i, self.flow, self.f_i][ind]
    

def input_validations(a_i, s_i, q_i, n_queues):
    if a_i < 0.0 or s_i < 0.0:
        print('Error a_i and s_i must be >= 0.0')
        sys.exit()
    if q_i < 1:
        print('Error q_i must be >= 1')
        sys.exit() 
    if q_i > n_queues:
        print('Error n_queue must be equals queues_weights size')
        sys.exit() 

def parse_file(path, n_queues):
    lines = []
    with open(path) as input_file:
        for line in input_file.readlines():
            # read line
            a_i, s_i, q_i = line.replace('\n', '').split(' ') 
            # cast input line
            a_i, s_i, q_i = float(a_i), float(s_i), int(q_i)
            # values validations
            input_validations(a_i, s_i, q_i, n_queues)
            lines.append((a_i, s_i, q_i))
    return lines       

def load_transmissions(path, n_queues):
    transmissions = parse_file(path, n_queues)
    # sort the packets by arrival time
    transmissions.sort(key=lambda p: p[0])
    return transmissions

def setup_scheduled(transmissions, return_packets=False):
    # fill the queue
    packets = []
    queues = {}
    next_time = float('inf')
    for r_packet in transmissions:
        a_i, s_i, flow = r_packet
        packet = Packet(a_i, s_i, flow)
        # calculate current next_time
        next_time = min(next_time, a_i)
        queues.setdefault(flow, []).append(packet)
        packets.append(packet)
    if return_packets:
        return next_time, queues, packets
    return next_time, queues

def run_scheduled(start_time, n_packets, queues, queues_weights, packets=[]):
    # start algorithm
    current_time = start_time
    global_f_i = float("-inf")
    while n_packets != 0:
        current_best_f_i, best_queue_idx = (float('inf'), list(queues.keys())[0])
        current_next_time = float('inf')
        for queue_idx, queue in queues.items():
            if len(queue) == 0:
                continue
            # check if the queue has a new avaliable packet 
            if queue[0].a_i < current_time and queue[0].f_i == -1:
                # check if the package arrives the next time
                current_next_time = min(current_next_time, queue[0].a_i)
                continue
            packet = queue[0]
            # get the packet estimated end time
            if packet.f_i == -1: # Indicates that the packet has just arrived
                f_i = max(global_f_i, packet.a_i) + packet.s_i / queues_weights[queue_idx - 1]
                packet.f_i = f_i
            else:
                f_i = packet.f_i     
            # check if the packet can be the next
            if f_i < current_best_f_i:
                current_best_f_i = f_i
                best_queue_idx = queue_idx
            # update the next_time if it is necesary
            if len(queue) > 1:
                current_next_time = min(current_next_time, queue[1].a_i)
        # pop the next element
        current_time = current_next_time
        packet = queues[best_queue_idx].pop(0)
        global_f_i = packet.f_i
        print('next -> %d' % (packet.id + 1))
        n_packets -= 1

def parse_args():
    parser = argparse.ArgumentParser(
        prog="WFQ",
        description="A program that simulates a Weighted Fair Queuing",
    )
    parser.add_argument('queues_weights')
    parser.add_argument('filename') 
    # parse arguments
    args = parser.parse_args()

    # cast queues_weights to float
    queues_weights = args.queues_weights.split(',')
    args.queues_weights = [float(weight) for weight in queues_weights]
    return args

def main():
    # Parse input program arguments
    args = parse_args()
    queues_weights = args.queues_weights
    input_file_path = args.filename
    n_queues =  len(queues_weights)
    # run transmissions scheduler
    transmissions_to_schedule = load_transmissions(input_file_path, n_queues)
    start_time, queues, packets = setup_scheduled(transmissions_to_schedule, return_packets=True)
    n_transmissions = len(transmissions_to_schedule)
    run_scheduled(start_time, n_transmissions, queues, queues_weights=queues_weights)

if __name__ == '__main__':
    main()
    
