from logging import INFO

# General

SEND_FILENAME = "inLong.txt"
RECV_FILENAME = "outLong.txt"
ACK_MSG = "All good!"

# Packet

HEADER_SIZE = 2 * 4 + 1 * 3
MAX_DATA_SIZE = 200

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

PROB_DROP = 0.1     # probability packet will be dropped
TIMEOUT = 6         # time till sender will resend packet (in seconds)
MAX_DELAY = 4       # maximum time packet will be delayed (in seconds)
def DELAY(x):       # determine time delay of packet
    assert 0 <= x <= 1
    return MAX_DELAY * (x ** 2)

# Logging

LOGGING_FORMAT = "%(asctime)s %(message)s"
LOGGING_DATEFMT = "%H:%M:%S"
LOGGING_LEVEL = INFO

# Handshake

INIT_SEND_PACKET_NUM = 0
INIT_RECV_PACKET_NUM = 0

# Congestion Control

MIN_CWND_CAPACITY = 1
MAX_CWND_CAPACITY = 15
INIT_SSTHRESH = 8

# Receiver Stash

STASH_CAPACITY = 5
