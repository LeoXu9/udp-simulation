import sys
import socket
import math
import time
import os
from threading import Thread, Lock

base = 0
next = 0
lock = Lock()


def recv_ack(sock):
    global base
    global lock
    global last_ack
    while True:
        data, _ = sock.recvfrom(1024)
        lock.acquire()
        ack = int.from_bytes(data, 'little')
        base = ack + 1
        if ack == last_ack:
            lock.release()
            break
        lock.release()


def istimeout(timeout, start_time):
    return (time.time() - start_time) > (timeout/1000)


def divide(filename):
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


def send(socket_, receiver_ip, port,  retry_timeout, window_size, file_divided):
    global base
    global next
    global lock
    global last_ack
    last_ack = int.from_bytes(file_divided[-1][:2], 'little')
    window = window_size
    recv = Thread(target=recv_ack, args=(socket_,))
    recv.start()
    start_time = time.perf_counter()
    while True:
        lock.acquire()
        if base >= len(file_divided):
            lock.release()
            break
        while next < base + window:
            socket_.sendto(file_divided[next], (receiver_ip, port))
            if base == next:
                start_ = time.time()
            next += 1
        while not istimeout(retry_timeout, start_):
            lock.release()
            time.sleep(0.0001)
            lock.acquire()
        if istimeout(retry_timeout, start_):
            next = base
        window = len(file_divided)-base if len(file_divided) - \
            base < window_size else window_size
        lock.release()
    end_time = time.perf_counter()
    socket_.close()
    total_time = end_time - start_time
    return total_time


if __name__ == "__main__":
    receiver_ip = sys.argv[1]
    port = int(sys.argv[2])
    file_name = sys.argv[3]
    retry_timeout = int(sys.argv[4])
    window_size = int(sys.argv[5])
    file_size = os.path.getsize(file_name)/1024
    socket_ = socket.socket(type=socket.SOCK_DGRAM)
    file_divided = divide(file_name)
    total_time = send(socket_, receiver_ip, port,
                      retry_timeout, window_size, file_divided)
    throughput = round((file_size / total_time), 4)
    print(str(throughput))
