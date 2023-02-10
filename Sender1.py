import socket
import math
import sys


class Sender:
    def __init__(self, receiver_ip, port, file_name):
        self.receiver_ip = receiver_ip
        self.port = port
        self.file_name = file_name
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_to_send = []

    def divide(self):
        with open(self.file_name, 'rb') as f:
            f2 = f.read()
            f_bytes = bytearray(f2)
        f.close()
        num = math.floor(len(f_bytes)/1024)
        sequence_number = 0
        end_of_file = 0
        if len(f_bytes) % 1024 == 0:
            num -= 1
        for i in range(num):
            datagram = bytearray(sequence_number.to_bytes(2, 'little'))
            datagram.append(end_of_file)
            datagram.extend(f_bytes[:1024])
            self.file_to_send.append(datagram)
            f_bytes = f_bytes[1024:]
            sequence_number += 1
        end_of_file = 1
        datagram = bytearray(sequence_number.to_bytes(2, 'big'))
        datagram.append(end_of_file)
        datagram.extend(f_bytes)
        self.file_to_send.append(datagram)

    def send_file(self):
        num = len(self.file_to_send)
        for i in range(num):
            self.socket_.sendto(
                self.file_to_send[i], (self.receiver_ip, self.port))
        self.socket_.close()


if __name__ == "__main__":
    sender = Sender((sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    sender.divide()
    sender.send_file()
