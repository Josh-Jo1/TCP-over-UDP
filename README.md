# TCP-over-UDP


inShort.txt: 100 words\
inLong.txt: 700 words

## Usage

Terminal 1
```
python receiver.py
```

Terminal 2
```
python sender.py
```

## Development Process

1. Created basic sender and receiver, connected over UDP.
2. Created a Packet class to send header + data as bytes through sockets.
3. Added functionality to transfer files. Discovered no loss or reordering, so will need a network emulator.


## Versions

Python 3.10.2

Ubuntu 22.04.3 LTS

WSL2 5.15.133.1
