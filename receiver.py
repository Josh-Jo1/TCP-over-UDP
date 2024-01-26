import socket

from packet import Packet

SEND_ADDR = "127.0.0.1"
SEND_PORT = 24001
BIND_PORT = 24000
ACK_MSG = "All good!"

FILE_TO_RECV = "outLong.txt"

class Receiver:
    def __init__(self, send_addr, send_port, bind_port):
        self.send_addr = send_addr
        self.send_port = send_port
        self.bind_port = bind_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.recv_file = open(FILE_TO_RECV, 'w')

    def __del__(self):
        self.sock.close()

        self.recv_file.close()

    def run(self):
        self.sock.bind(('', self.bind_port))
        
        while True:
            # Wait for acknowledgement
            packet, _ = self.sock.recvfrom(2048)
            _, _, _, msg = Packet.decode(packet)
            print("Message received!")
            if msg != "EOF":
                self.recv_file.write(msg)

            # Send message
            packet = Packet(1, 0, len(ACK_MSG), ACK_MSG)
            self.sock.sendto(packet.encode(), (self.send_addr, self.send_port))
            print("Acknowledgement sent!")

            if msg == "EOF":
                break

receiver = Receiver(SEND_ADDR, SEND_PORT, BIND_PORT)
receiver.run()
