import sys
import socket

RECEIVER_IP = '127.0.0.1'


class Receiver:
    def __init__(self, port, file_name):
        self.port = port
        self.file_name = file_name
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def connect(self):
        self.socket_.bind((RECEIVER_IP, self.port))

    def receive_file(self):
        file_received = bytearray()
        curr_seq_num = 0
        prev_seq_num = -1
        while True:
            received, address = self.socket_.recvfrom(1027)
            if received is None:
                continue
            curr_seq_num = int.from_bytes(received[:2], 'little')
            if curr_seq_num == (prev_seq_num + 1):
                prev_seq_num = curr_seq_num
                file_received.extend(received[3:])
                self.socket_.sendto(curr_seq_num.to_bytes(
                    2, byteorder='little'), address)
            else:
                self.socket_.sendto(curr_seq_num.to_bytes(
                    2, byteorder='little'), address)
            if (received[2] == 1):
                for i in range(10):
                    self.socket_.sendto(curr_seq_num.to_bytes(
                    2, byteorder='little'), address)
                break
        return file_received

    def write_file(self, file_received):
        with open(self.file_name, 'wb') as f:
            f.write(file_received)
        f.close()
        self.socket_.close()


if __name__ == "__main__":
    receiver = Receiver(int(sys.argv[1]), sys.argv[2])
    receiver.connect()
    receiver.write_file(receiver.receive_file())
