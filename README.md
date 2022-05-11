# udp-MIDI
## Protocol to send multiple midi-streams over the internet with UDP.

### Objectives
- Send live MIDI messages from client(s) to a host
- Handle multiple udp clients which will be processed on one host machine
- Synchronise all udp clients on hosts
  - The host can account for varying latencies between clients
  - Timestamp notes before sending on client side
  - Sync all machines involved with NTP so that timestamping is accurate
-blah
