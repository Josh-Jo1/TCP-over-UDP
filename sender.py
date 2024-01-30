import socket

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

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        
        # Send message
        while True:
            # Get message
            msg = self.send_file.read(PACKET_MAX_DATA_SIZE)
            if msg == '':
                break

            # Send packet
            packet = Packet(1, 0, len(msg), msg)
            self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
            print("Message sent!")

            # Wait for acknowledgement
            bytes = self.recv_sock.recv(RECV_BUFSIZE)
            _, _, _, msg = Packet.decode(bytes).extract()
            print("Acknowledgement received: \'{}\'".format(msg))

        # Send EOF packet
        msg = "EOF"
        packet = Packet(1, 0, len(msg), msg)
        self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
        print("EOF message sent!")

        # Wait for EOF acknowledgement
        bytes = self.recv_sock.recv(RECV_BUFSIZE)
        _, _, _, msg = Packet.decode(bytes).extract()
        print("EOF acknowledgement received: \'{}\'".format(msg))
    # end run
# end Sender

if __name__ == '__main__':
    sender = Sender(NE_ADDR, SEND_PORT, SEND_BIND_PORT)
    sender.run()
