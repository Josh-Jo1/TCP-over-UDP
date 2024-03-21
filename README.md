# TCP-over-UDP


inShort.txt: 100 words\
inLong.txt: 700 words

## Usage

Terminal 1
```
python network-emulator.py
```

Terminal 2
```
python receiver.py
```

Terminal 3
```
python sender.py
```

## Development Process

1. Created basic sender and receiver, connected over UDP.
2. Created a Packet class to send header + data as bytes through sockets.
3. Added functionality to transfer files. Discovered no loss or reordering, so will need a network emulator.
4. Created basic network emulator (like a middlebox) and connected sender with receiver.
5. Implemented dropping of packets in network emulator and changed sender to have separate threads for sending and receiving data.
6. Checkpoint: reformat code and comments for easier understanding.
7. Improved Packet structure to match real TCP header more closely and implemented (trivially reliable) connection handshake.
8. Created a Window class and implemented reliable data transfer for data packets (not yet congestion-controlled).
9. Updated Window class to a bounded buffer and added testing.
10. Improved connection handshake to reliable 3-way handshake and moved logic for packet number to send thread.
11. Implemented TCP Reno in sender and cumulative ACKs in receiver. After one packet dropped, congestion window becomes ineffective, so need to create a buffer for receiver.
12. Implemented a Stash class as a bounded buffer, with testing, to temporarily store near-future packets in receiver.
13. Implemented delaying of packets in network emulator.

## Resources

1. https://www.youtube.com/watch?v=kRS4J-m5n04
2. https://www.rfc-editor.org/rfc/rfc9293.html

## Versions

Python 3.10.2

Ubuntu 22.04.3 LTS

WSL2 5.15.133.1
