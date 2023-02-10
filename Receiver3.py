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
        expected_ack = 0
        while True:
            received, address = self.socket_.recvfrom(1027)
            file = bytes(received[3:])
            ack = int.from_bytes(received[:2], 'little')
            if ack == expected_ack:
                file_received.extend(file)
                self.socket_.sendto(
                    expected_ack.to_bytes(2, 'little'), address)
                if received[2] == 1:
                    break
                expected_ack += 1
            else:
                if expected_ack == 0:
                    self.socket_.sendto(
                        (expected_ack).to_bytes(2, 'little'), address)
                else:
                    self.socket_.sendto(
                        (expected_ack - 1).to_bytes(2, 'little'), address)
        self.socket_.close()
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
