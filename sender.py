import socket

RECV_ADDR = "127.0.0.1"
RECV_PORT = 24000
BIND_PORT = 24001
TEST_MSG = "Testing UDP!"

class Sender:
    def __init__(self, recv_addr, recv_port, bind_port):
        self.recv_addr = recv_addr
        self.recv_port = recv_port
        self.bind_port = bind_port

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __del__(self):
        self.send_sock.close()
        self.recv_sock.close()

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        
        # Send message
        self.send_sock.sendto(TEST_MSG.encode(), (self.recv_addr, self.recv_port))
        print("Message sent!")

        # Wait for acknowledgement
        message, _ = self.recv_sock.recvfrom(2048)
        print("Acknowledgement received: \'{}\'".format(message.decode()))

sender = Sender(RECV_ADDR, RECV_PORT, BIND_PORT)
sender.run()
