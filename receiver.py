import socket

from packet import Packet

SEND_ADDR = "127.0.0.1"
SEND_PORT = 24001
BIND_PORT = 24000
ACK_MSG = "Acknowledge UDP!"

class Receiver:
    def __init__(self, send_addr, send_port, bind_port):
        self.send_addr = send_addr
        self.send_port = send_port
        self.bind_port = bind_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __del__(self):
        self.sock.close()

    def run(self):
        self.sock.bind(('', self.bind_port))
        
        # Wait for acknowledgement
        message, _ = self.sock.recvfrom(2048)
        print("Message received: \'{}\'".format(Packet.decode(message)))

        # Send message
        packet = Packet(1, 0, len(ACK_MSG), ACK_MSG)
        self.sock.sendto(packet.encode(), (self.send_addr, self.send_port))
        print("Acknowledgement sent!")

receiver = Receiver(SEND_ADDR, SEND_PORT, BIND_PORT)
receiver.run()
