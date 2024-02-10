import logging
import socket
import threading

from constants import *
from packet import Packet

class Sender:
    def __init__(self, ne_host, ne_port, bind_port):
        self.ne_host = ne_host
        self.ne_port = ne_port
        self.bind_port = bind_port

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_file = open(SEND_FILENAME, 'r')
    # end __init__

    def __del__(self):
        self.send_sock.close()
        self.recv_sock.close()
        self.send_file.close()
    # end __del__

    def sendData(self):
        packet_num = 0
        while True:
            # Get message
            msg = self.send_file.read(MAX_DATA_SIZE)

            # Send message
            type = EOF if msg == '' else DATA
            packet = Packet(type, packet_num, len(msg), msg)
            self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
            logging.info(f"Packet {packet_num} sent")

            if type == EOF:
                break
            packet_num += 1
    # end sendData

    def recvData(self):
        while True:
            # Receive acknowledgement
            bytes = self.recv_sock.recv(RECV_BUFSIZE)
            type, packet_num, _, msg = Packet.decode(bytes).extract()
            logging.info(f"Packet {packet_num} received: {msg}")

            if (type == EOF):
                break

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        
        sendThread = threading.Thread(target=self.sendData)
        recvThread = threading.Thread(target=self.recvData)
        sendThread.start()
        recvThread.start()
        sendThread.join()
        recvThread.join()
    # end run
# end Sender

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    sender = Sender(NE_ADDR, SEND_PORT, SEND_BIND_PORT)
    sender.run()
