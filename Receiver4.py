import sys
import socket
import math

RECEIVER_IP = '127.0.0.1'


class Receiver:
    def __init__(self, port, file_name, window_size):
        self.port = port
        self.file_name = file_name
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.window_size = window_size

    def connect(self):
        self.socket_.bind((RECEIVER_IP, self.port))

    def break_out(self, expected_ack, last_ack, address):
        for i in range(last_ack-self.window_size, expected_ack):
            for j in range(100):
                self.socket_.sendto(
                    i.to_bytes(2, 'little'), address)

    def receive_file(self):
        file_received = []
        expected_ack = 0
        buffer = [-1] * self.window_size
        last_ack = math.inf
        while True:
            received, address = self.socket_.recvfrom(1027)
            file = bytes(received[3:])
            ack = int.from_bytes(received[:2], 'little')
            if received[2] == 1:
                last_ack = ack
            if ack == expected_ack:
                if self.window_size == 1:
                    self.socket_.sendto(ack.to_bytes(2, 'little'), address)
                    file_received.append(file)
                    expected_ack += 1
                    if expected_ack > last_ack:
                        self.break_out(expected_ack, last_ack, address)
                        break
                    continue
                self.socket_.sendto(ack.to_bytes(2, 'little'), address)
                try:
                    filled = buffer[1:].index(-1)
                except:
                    filled = self.window_size-1
                file_received.append(file)
                file_received.extend(buffer[1:filled+1])
                buffer = buffer[filled+1:] + \
                    ([-1] * (self.window_size-len(buffer[filled+1:])))
                expected_ack = ack + filled + 1
                if expected_ack > last_ack:
                    self.break_out(expected_ack, last_ack, address)
                    break
            else:
                self.socket_.sendto((ack).to_bytes(2, 'little'), address)
                if ack > expected_ack:
                    buffer[ack - expected_ack] = file
        self.socket_.close()
        return file_received

    def write_file(self, file_received):
        with open(self.file_name, 'wb') as f:
            for i in file_received:
                f.write(bytes(i))
        self.socket_.close()


if __name__ == "__main__":
    receiver = Receiver(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    receiver.connect()
    receiver.write_file(receiver.receive_file())
