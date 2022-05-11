import socket
import rtmidi
import time
import threading
import sched
from queue import Queue
import ntplib

c = ntplib.NTPClient()
response = c.request('us.pool.ntp.org')
offset = response.offset

# gets midi input from local machine
def get_local_midi(midi_in, latency, local_ip, q):
    
    def local_delay(msg_with_timestamp, delay):
        time.sleep(delay)
        q.put(msg_with_timestamp)

    while 1:
        msg = midi_in.get_message()
        if(msg != None):
            timestamp = time.time()+offset
            msg_with_timestamp = (local_ip,) + msg + (timestamp,)
            t4 = threading.Thread(target=local_delay, args=(msg_with_timestamp, latency))
            t4.start()

# gets midi from other hosts over internet
def get_online_midi(sock, q):
    while 1:
        data, addr = sock.recvfrom(1024) # 1024 byte buffer
        ip = addr[0]
        msg = data.decode("UTF-8").replace('(', '').replace(')', '').replace('[', '').replace(']', '').split(',')
        note, delta_time, timestamp = [float(elem) for elem in msg[:-2]], float(msg[-2]), float(msg[-1])
        msg_with_timestamp = (ip, note, delta_time, timestamp)
        q.put(msg_with_timestamp)

# play midi on synth
def play_midi(midi_out, q):

    def play_with_delay(note, ip, latency_dictionary):
        print(latency_dictionary)
        default_delay = 0.4
        slowest_latency = max(latency_dictionary.values())
        slowest_ip = max(latency_dictionary, key=latency_dictionary.get)

        if(ip != slowest_ip):
            #print(ip, 'not slowest')
            #print(max(latency_dictionary), 'slowest ip')
            latency = latency_dictionary[ip]
            when_to_play = time.time() + (slowest_latency - latency + default_delay)
            #print(f'ip: {ip} timestamp: {timestamp}')
        elif(ip == slowest_ip):
            #print(ip, 'slowest')
            when_to_play = time.time() + default_delay
            #print(f'ip: {ip} timestamp: {timestamp}')
    
        s = sched.scheduler(time.time, time.sleep)
        s.enterabs(when_to_play, priority=1, action=midi_out.send_message, argument=(note,))
        s.run()

    latency_dictionary = {}
    while 1:
        data = q.get() # waits here until it gets something
        ip, note, delta_time, timestamp = data[0], data[1], data[2], data[3]
        latency_dictionary.update({ip : (time.time()+offset)-timestamp})
        t5 = threading.Thread(target=play_with_delay, args=(note, ip, latency_dictionary))
        t5.start()

IP_ADDR = '10.63.1.171' 
UDP_PORT = 5004

# opens a port to listen for UDP messages
sock = socket.socket( socket.AF_INET,    # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((IP_ADDR, UDP_PORT))

midi_out = rtmidi.MidiOut()
midi_in = rtmidi.MidiIn()
available_ports = midi_in.get_ports()
#print(available_ports)
# port 0 is microsoft GS wavetable synth
midi_out.open_port(0)
# port 0 is virtual loopMIDI
midi_in.open_port(0)

q = Queue()
t1 = threading.Thread(target=get_online_midi, args=(sock, q))
t2 = threading.Thread(target=get_local_midi, args=(midi_in, 2, IP_ADDR, q))
t3 = threading.Thread(target=play_midi, args=(midi_out, q))
t1.start()
t2.start()
t3.start()
