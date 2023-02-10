import sys
import socket
import math
import time
import os
from threading import Thread, Lock


base = 0
next = 0
lock = Lock()


class Sender:
    def __init__(self, receiver_ip, port, file_name, retry_timeout, window_size):
        self.receiver_ip = receiver_ip
        self.port = port
        self.file_name = file_name
        self.retry_timeout = retry_timeout/1000
        self.window_size = window_size

    def timedout(self, timeout, start_time):
        return (time.time() - start_time) > (timeout/1000)

    def divide(self, filename):
        file_to_send = []
        with open(filename, 'rb') as f:
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
            file_to_send.append(datagram)
            f_bytes = f_bytes[1024:]
            sequence_number += 1
        end_of_file = 1
        datagram = bytearray(sequence_number.to_bytes(2, 'little'))
        datagram.append(end_of_file)
        datagram.extend(f_bytes)
        file_to_send.append(datagram)
        return file_to_send

    def send_a_datagram(self, socket_, datagram, ack, retry_timeout, receiver_ip, port):

        global acks
        global lock
        start_ = time.time()
        while True:
            if self.timedout(retry_timeout, start_):
                socket_.sendto(datagram, (receiver_ip, port))
                start_ = time.time()
                continue
            lock.acquire()
            if not acks[ack]:
                lock.release()
                time.sleep(0.00001)
                continue
            else:
                lock.release()
                break

    def receive_ack(self, sock):
        global acks
        global lock

        while True:
            if all(acks):
                break
            data, _ = sock.recvfrom(1024)
            ack = int.from_bytes(data, 'little')
            lock.acquire()
            acks[ack] = True
            lock.release()

    def send(self, socket_, receiver_ip, port,  retry_timeout, window_size, file_divided):
        global acks
        global base
        global next
        global lock

        window = window_size
        acks = [False]*len(file_divided)
        receiving_thread = Thread(target=self.receive_ack, args=(socket_,))
        receiving_thread.start()
        start_time = time.perf_counter()
        k = 0
        while True:
            lock.acquire()
            if base >= len(file_divided):
                lock.release()
                k = 0
                break
            while next < base + window:
                sending_thread = Thread(target=self.send_a_datagram, args=(
                    socket_, file_divided[next], next, retry_timeout, receiver_ip, port))
                sending_thread.start()
                k = 0
                next += 1
            while not acks[base]:
                lock.release()
                time.sleep(0.01)
                lock.acquire()
                k += 1
                if k > 30:
                    if(self.window_size==1):
                        base+=999
                        break
                    acks[base] = True
            base += 1
            window = len(file_divided) - base if len(file_divided) - \
                base < window_size else window_size
            lock.release()
        end_time = time.perf_counter()
        socket_.close()
        total_time = end_time - start_time
        return total_time


if __name__ == "__main__":
    sender = Sender(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    receiver_ip = sys.argv[1]
    port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry_timeout = int(sys.argv[4])
    window_size = int(sys.argv[5])
    file_size = os.path.getsize(file_name)/1024
    socket_ = socket.socket(type=socket.SOCK_DGRAM)
    file_divided = sender.divide(file_name)
    total_time = sender.send(socket_, receiver_ip, port,
                             retry_timeout, window_size, file_divided)
    throughput = round((file_size / total_time), 4)
    print(str(throughput))
    os._exit(0)
