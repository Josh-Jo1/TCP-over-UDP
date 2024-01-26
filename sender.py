import socket

from packet import Packet

RECV_ADDR = "127.0.0.1"
RECV_PORT = 24000
BIND_PORT = 24001

FILE_TO_SEND = "inLong.txt"
MAX_DATA_LENGTH = 200

class Sender:
    def __init__(self, recv_addr, recv_port, bind_port):
        self.recv_addr = recv_addr
        self.recv_port = recv_port
        self.bind_port = bind_port

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.send_file = open(FILE_TO_SEND, 'r')

    def __del__(self):
        self.send_sock.close()
        self.recv_sock.close()

        self.send_file.close()

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        
        # Send message
        while True:
            # Get message
            msg = self.send_file.read(MAX_DATA_LENGTH)
            if msg == '':
                break

            # Send packet
            packet = Packet(1, 0, len(msg), msg)
            self.send_sock.sendto(packet.encode(), (self.recv_addr, self.recv_port))
            print("Message sent!")

            # Wait for acknowledgement
            packet, _ = self.recv_sock.recvfrom(2048)
            _, _, _, msg = Packet.decode(packet)
            print("Acknowledgement received: \'{}\'".format(msg))

        # Send EOF packet
        msg = "EOF"
        packet = Packet(1, 0, len(msg), msg)
        self.send_sock.sendto(packet.encode(), (self.recv_addr, self.recv_port))
        print("EOF message sent!")

        # Wait for EOF acknowledgement
        packet, _ = self.recv_sock.recvfrom(2048)
        _, _, _, msg = Packet.decode(packet)
        print("EOF acknowledgement received: \'{}\'".format(msg))

sender = Sender(RECV_ADDR, RECV_PORT, BIND_PORT)
sender.run()
