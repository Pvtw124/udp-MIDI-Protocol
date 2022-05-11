import socket
import threading
import rtmidi
import time
import ntplib

c = ntplib.NTPClient()
response = c.request('us.pool.ntp.org')
offset = response.offset
print(offset)

UDP_IP = '10.63.1.171'
UDP_PORT = 5004

print( "UDP target IP:", UDP_IP )
print( "UDP target port:", UDP_PORT )

midi_out = rtmidi.MidiOut()
midi_in = rtmidi.MidiIn()
print("input ports:", midi_in.get_ports())
print("output ports:", midi_out.get_ports())



# AKM320
midi_in.open_port(0)

# set up UDP socket
sock = socket.socket( socket.AF_INET,     # Internet
                      socket.SOCK_DGRAM ) # UDP

# gets midi input from AKM320, and adds local timestamp, then sends to other host
def send_midi_input(midi_in):
    while 1:
        msg = midi_in.get_message()
        if(msg != None):
            msg_with_timestamp = msg + (time.time()+offset,)
            data = str(msg_with_timestamp).encode( "UTF-8" )
            sock.sendto(data, ( UDP_IP, UDP_PORT ) )
            print(data)

t1 = threading.Thread(target=send_midi_input, args=(midi_in,))
t1.start()

