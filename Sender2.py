import socket
import math
import sys
import time


class Sender:
    def __init__(self, receiver_ip, port, file_name, retry_timeout):
        self.receiver_ip = receiver_ip
        self.port = port
        self.file_name = file_name
        self.retry_timeout = retry_timeout/1000
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_to_send = []
        self.file_bytes_num = 0

    def divide(self):
        with open(self.file_name, 'rb') as f:
            f2 = f.read()
            f_bytes = bytearray(f2)
        f.close()
        self.file_bytes_num = len(f_bytes)
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
        datagram = bytearray(sequence_number.to_bytes(2, 'little'))
        datagram.append(end_of_file)
        datagram.extend(f_bytes)
        self.file_to_send.append(datagram)

    def send_file(self):
        num = len(self.file_to_send)
        retransmissions = 0
        start_time = time.perf_counter()
        for i in range(num):
            self.socket_.sendto(
                self.file_to_send[i], (self.receiver_ip, self.port))
            while True:
                try:
                    self.socket_.settimeout(self.retry_timeout)
                    received_ack = int.from_bytes(
                        self.socket_.recv(2), 'little')
                    if received_ack == num-1:
                        received_ack = int.from_bytes(
                        self.socket_.recv(2), 'little')
                        received_ack = int.from_bytes(
                        self.socket_.recv(2), 'little')
                        break
                    if received_ack != i:
                        # print(i)
                        # print(received_ack)
                        self.socket_.sendto(
                            self.file_to_send[i], (self.receiver_ip, self.port))
                        retransmissions += 1
                        # print('stuck')
                    else:
                        break
                except:
                    self.socket_.sendto(
                        self.file_to_send[i], (self.receiver_ip, self.port))
                    # retransmissions += 1
        # print()
        end_time = time.perf_counter()
        total_time = end_time - start_time
        throughput = round((self.file_bytes_num/1024)/total_time, 4)
        print(str(retransmissions)+' '+str(throughput))
        self.socket_.close()


if __name__ == "__main__":
    sender = Sender((sys.argv[1]), int(sys.argv[2]),
                    sys.argv[3], int(sys.argv[4]))
    sender.divide()
    sender.send_file()
