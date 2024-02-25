import logging
import socket
from threading import Lock, Condition, Timer, Thread

from window import Window
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

        self.lock = Lock()
        self.send_cv = Condition()
        self.cwnd = Window()
        self.timer = None
        self.packet_num = 0
        self.expected_ack_num = 0
    # end __init__

    def __del__(self):
        self.send_sock.close()
        self.recv_sock.close()
        self.send_file.close()
    # end __del__

    def sendData(self):
        # Handshake
        packet = Packet(INIT_SEND_PACKET_NUM, 0, 0, 1, 0, "")
        self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
        logging.info(f"Packet {INIT_SEND_PACKET_NUM} {0} sent")

        self.lock.acquire()

        self.cwnd.push(packet)
        self.timer = Timer(TIMEOUT, self.onTimeout)
        self.timer.start()

        self.lock.release()

        self.send_cv.acquire()
        self.send_cv.wait()

        logging.info(f"Handshake done")


        while True:
            # Get message
            msg = self.send_file.read(MAX_DATA_SIZE)

            # Send message
            fin_bit = 1 if msg == '' else 0
            packet = Packet(self.packet_num, self.expected_ack_num, 0, 0, fin_bit, msg)
            self.send_sock.sendto(packet.encode(), (self.ne_host, self.ne_port))
            logging.info(f"Packet {self.packet_num} sent")

            self.lock.acquire()

            self.cwnd.push(packet)
            self.timer = Timer(TIMEOUT, self.onTimeout)
            self.timer.start()
            
            self.lock.release()

            self.send_cv.acquire()
            self.send_cv.wait()

            if fin_bit == 1:
                break
    # end sendData

    def recvData(self):
        bytes, _ = self.recv_sock.recvfrom(RECV_BUFSIZE)
        packet_num, ack_num, ack_bit, syn_bit, _, _ = Packet.decode(bytes).extract()
        logging.info(f"Received {packet_num}, {ack_num}, {ack_bit}, {syn_bit}")
        
        self.lock.acquire()

        self.timer.cancel()
        self.cwnd.pop()

        self.packet_num = ack_num
        self.expected_ack_num = packet_num + 1
        logging.info(f"packet_num: {self.packet_num} expected_packet_num: {self.expected_ack_num}")

        self.lock.release()

        self.send_cv.acquire()
        self.send_cv.notify()
        self.send_cv.release()


        while True:
            # Receive acknowledgement
            bytes = self.recv_sock.recv(RECV_BUFSIZE)
            packet_num, ack_num, _, _, fin_bit, msg = Packet.decode(bytes).extract()
            logging.info(f"Packet {packet_num} received: {msg}")

            self.lock.acquire()

            self.timer.cancel()
            self.cwnd.pop()

            self.packet_num = ack_num
            self.expected_ack_num = packet_num + 1
            logging.info(f"packet_num: {self.packet_num} expected_packet_num: {self.expected_ack_num}")

            self.lock.release()

            self.send_cv.acquire()
            self.send_cv.notify()
            self.send_cv.release()

            if (fin_bit == 1):
                break
    # end recvData

    def onTimeout(self):
        self.lock.acquire()
        self.send_sock.sendto(self.cwnd.head().encode(), (self.ne_host, self.ne_port))
        logging.info(f"Timer packet sent")
        self.timer = Timer(TIMEOUT, self.onTimeout)
        self.timer.start()
        self.lock.release()
    # end onTimeout

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        
        recvThread = Thread(target=self.recvData)
        sendThread = Thread(target=self.sendData)
        recvThread.start()
        sendThread.start()
        recvThread.join()
        sendThread.join()
    # end run
# end Sender

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, datefmt=LOGGING_DATEFMT, level=LOGGING_LEVEL)
    sender = Sender(NE_ADDR, SEND_PORT, SEND_BIND_PORT)
    sender.run()
