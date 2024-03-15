import logging
import socket
from threading import Lock, Condition, Timer, Thread

from window import Window
from constants import *
from packet import Packet

class Sender:
    def __init__(self, ne_addr, ne_port, bind_port):
        self.ne_addr = ne_addr
        self.ne_port = ne_port
        self.bind_port = bind_port

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_file = open(SEND_FILENAME, 'r')

        self.lock = Lock()
        self.send_cv = Condition()
        self.packet_num = None
        self.expected_packet_num = None

        # Congestion control
        self.cwnd = Window()
        self.timer = None
        self.ssthresh = INIT_SSTHRESH
        self.aimd_count = None
    # end __init__

    def __del__(self):
        self.send_sock.close()
        self.recv_sock.close()
        self.send_file.close()
    # end __del__

    def perform3WayHandshake(self):
        # Send SYN packet
        packet = Packet(INIT_SEND_PACKET_NUM, 0, 0, 1, 0, "")
        self.send_sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
        logging.info("SYN Packet sent")
        self.cwnd.push(packet)
        self.timer = Timer(TIMEOUT, self.onTimeout)
        self.timer.start()

        # Receive SYN ACK packet
        bytes = self.recv_sock.recv(RECV_BUFSIZE)
        packet_num, ack_num, ack_bit, syn_bit, _, _ = Packet.decode(bytes).extract()
        logging.info("SYN ACK Packet received")
        self.timer.cancel()
        self.timer = None
        self.cwnd.pop()
        if ack_bit == 0 or syn_bit == 0:
            logging.warning(f"Packet received with {ack_bit} {syn_bit}!")
        self.packet_num = ack_num
        self.expected_packet_num = packet_num + 1
        
        # Send ACK packet
        packet = Packet(self.packet_num, self.expected_packet_num, 1, 0, 0, "")
        self.send_sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
        logging.info("ACK Packet sent")
        
        logging.info(f"Handshake done {self.packet_num} {self.expected_packet_num}")
    # end perform3WayHandshake

    def sendData(self):
        while True:
            # Get message
            msg = self.send_file.read(MAX_DATA_SIZE)

            # Send message
            fin_bit = 1 if msg == '' else 0
            self.lock.acquire()
            packet = Packet(self.packet_num, self.expected_packet_num, 1, 0, fin_bit, msg)
            self.send_sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
            logging.info(f"Packet {self.packet_num} sent")

            self.cwnd.push(packet)
            logging.info(f"send cwnd = {self.cwnd}")
            if self.timer == None:
                self.timer = Timer(TIMEOUT, self.onTimeout)
                self.timer.start()
            self.packet_num += 1

            if self.cwnd.getSize() == self.cwnd.getCapacity():
                # Wait till acknowledgement received
                with self.send_cv:
                    self.lock.release()
                    self.send_cv.wait()
            else:
                self.lock.release()

            if fin_bit == 1:
                break
    # end sendData

    def recvData(self):
        lastAckPacket = None
        dupCount = 0
        while True:
            # Receive acknowledgement
            bytes = self.recv_sock.recv(RECV_BUFSIZE)
            _, ack_num, ack_bit, _, fin_bit, msg = Packet.decode(bytes).extract()
            assert ack_bit == 1
            logging.info(f"ACK packet {ack_num} received: {msg}")

            # Check for triple duplicate ACK
            if lastAckPacket == ack_num:
                dupCount += 1
                if dupCount == 3:
                    # Fast Recovery
                    logging.info(f"Triple duplicate ACK packet {ack_num}")
                    self.lock.acquire()
                    self.ssthresh = max(self.ssthresh // 2, MIN_CWND_CAPACITY * 2)
                    self.cwnd.setCapacity(self.ssthresh)
                    self.aimd_count = None
                    dupCount = 0
                    self.lock.release()
                continue
            else:
                lastAckPacket = ack_num

            # Check for correct ACK
            self.lock.acquire()
            head_packet_num, _, _, _, _, _ = self.cwnd.head().extract()
            num_ack_packets = ack_num - head_packet_num
            if num_ack_packets < 1:
                self.lock.release()
                continue
            self.timer.cancel()
            self.timer = None
            self.cwnd.pop(num_ack_packets)
            logging.info(f"recv cwnd = {self.cwnd}")
            if self.cwnd.getSize() > 0:
                self.timer = Timer(TIMEOUT, self.onTimeout)
                self.timer.start()

            # Adjust congestion window
            if self.cwnd.getCapacity() < self.ssthresh:
                self.cwnd.setCapacity(self.cwnd.getCapacity() + 1)
            else:
                if self.aimd_count is None:
                    self.aimd_count = self.cwnd.getCapacity()
                self.aimd_count -= 1
                if self.aimd_count <= 0:
                    self.cwnd.setCapacity(self.cwnd.getCapacity() + 1)
                    self.aimd_count = self.cwnd.getCapacity()

            if self.cwnd.getSize() < self.cwnd.getCapacity():
                # Notify to send next message
                with self.send_cv:
                    self.send_cv.notify()

            self.lock.release()
            if fin_bit == 1:
                break
    # end recvData

    def onTimeout(self):
        self.lock.acquire()
        packet = self.cwnd.head()
        packet_num, _, _, _, fin_bit, _ = packet.extract()
        self.send_sock.sendto(packet.encode(), (self.ne_addr, self.ne_port))
        logging.info(f"Timer packet {packet_num} sent")

        if fin_bit == 0:
            self.timer = Timer(TIMEOUT, self.onTimeout)
            self.timer.start()

        # Adjust congestion window
        self.ssthresh = max(self.cwnd.getCapacity() // 2, MIN_CWND_CAPACITY)
        self.cwnd.setCapacity(MIN_CWND_CAPACITY)
        self.aimd_count = None

        self.lock.release()
    # end onTimeout

    def run(self):
        self.recv_sock.bind(('', self.bind_port))
        self.perform3WayHandshake()

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
