# udp-MIDI
## Protocol to send multiple midi-streams over the internet with UDP.

### Objectives
- Send live MIDI messages from client to host
- Handle multiple udp clients which will be processed on one host machine
- Synchronise all udp clients on hosts
  - The host can account for varying latencies between clients
  - Timestamp notes before sending on client side
  - Sync all machines involved with NTP so that timestamping is accurate
I was able to meet all of the above objectives in this project.
