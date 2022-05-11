# udp-MIDI
### Protocol to send multiple midi-streams over the internet with UDP, written in python
I did this project for a networking course at Houghton College

### Objectives
- Send live MIDI messages from client to host
- Handle multiple udp clients which will be processed on one host machine
- Synchronise all udp clients on hosts
  - The host can account for varying latencies between clients
  - Timestamp notes before sending on client side
  - Sync all machines involved with NTP so that timestamping is accurate

I was able to meet all of the above objectives in this project.

### Networking Principles used in this project
- UDP protocol
- Encoding and decoding
- NTP
- Virtual MIDI ports (I used loopMIDI by Tobias Erichsen)

### How it works

#### Client side
The client reads an inputed midi note using the rtmidi library, then timestamps the note with an added clock correction offset from ntp. Then the note is sent to the host machine with UDP.

```
def send_midi_input(midi_in):
    while 1:
        msg = midi_in.get_message()
        if(msg != None):
            msg_with_timestamp = msg + (time.time()+offset,)
            data = str(msg_with_timestamp).encode( "UTF-8" )
            sock.sendto(data, ( UDP_IP, UDP_PORT ) )
            print(data)
```

#### Host side
The host receives MIDI messages from the internet in one thread, and local MIDI messages from the host machine on another. These messages are added to a queue. In a new thread, the host reads notes from the queue. It compares the timestamp on the note to the current time to find the latency, and adds this information to a latency dictionary. This dictionary maps latency to IP addresses. 

`latency_dictionary.update({ip : (time.time()+offset)-timestamp})`

In a new thread, the note is played at the time specified by the timestamp, plus the required latency delay. To find the latency delay it should add, the host checks to see if this note comes from the slowest IP. If it is from the machine with the largest delay, no delay is added. If it not from the slowest machine, then the delay of the slowest machine minus the latency of the current machine is added.

```
if(ip != slowest_ip):
    latency = latency_dictionary[ip]
    when_to_play = time.time() + (slowest_latency - latency + default_delay)
elif(ip == slowest_ip):
    when_to_play = time.time() + default_delay
s = sched.scheduler(time.time, time.sleep)
s.enterabs(when_to_play, priority=1, action=midi_out.send_message, argument=(note,))
s.run()
```




