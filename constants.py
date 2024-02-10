from logging import INFO

# General

SEND_FILENAME = "inLong.txt"
RECV_FILENAME = "outLong.txt"
ACK_MSG = "All good!"

# Packet

HEADER_SIZE = 12
MAX_DATA_SIZE = 200

DATA = 0
ACK = 1
EOF = 2

# Sockets

NE_ADDR = "127.0.0.1"
RECV_ADDR = "127.0.0.1"
SEND_ADDR = "127.0.0.1"

SEND_PORT = 24000
RECV_BIND_PORT = 24001
RECV_PORT = 24002
SEND_BIND_PORT = 24003

RECV_BUFSIZE = HEADER_SIZE + MAX_DATA_SIZE

# Network Emulator

PROB_DROP = 0.4     # probability packet will be dropped

# Logging

LOGGING_FORMAT = "%(asctime)s %(message)s"
LOGGING_DATEFMT = "%H:%M:%S"
LOGGING_LEVEL = INFO
