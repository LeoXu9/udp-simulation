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
        while True:
            received = self.socket_.recv(1027)
            file_received.extend(received[3:])
            if (received[2] == 1):
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
