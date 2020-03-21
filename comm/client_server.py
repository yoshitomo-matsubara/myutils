import pickle
import socket
import time


def serialize(*args):
    return pickle.dumps(tuple(args))


def deserialize(pickle_dump):
    x = pickle.loads(pickle_dump)
    return x[0] if len(x) == 1 else x


class SocketClient(object):
    def __init__(self, server_address, port=8080, timeout_sec=30, buffer_size=4096):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout_sec if isinstance(timeout_sec, int) else float(timeout_sec))
        client.connect((server_address, port))
        self.client = client
        self.server_address = server_address
        self.port = port
        self.buffer_size = buffer_size
        self.requires_preprocess = False

    def preprocess(self, *args, **kwargs):
        raise NotImplementedError

    def send_and_receive(self, data, close_at_end=True):
        client_start_time = time.time()
        preprocessed_data = self.preprocess(data) if self.requires_preprocess else data
        data_id = hash(preprocessed_data)
        data_from_server = data_id
        processed_data = data_id
        server_start_time = None
        server_end_time = None
        try:
            if self.client.fileno() == -1:
                print('Reconnecting to {} ...'.format(self.server_address))
                self.client.connect((self.server_address, self.port))

            self.client.sendall(preprocessed_data)
            while True:
                data_from_server = self.client.recv(self.buffer_size)
                if data_from_server:
                    break
        except socket.timeout:
            print('Timeout')

        if close_at_end:
            self.client.close()

        if data_from_server != data_id:
            processed_data, server_start_time, server_end_time = deserialize(data_from_server)

        client_end_time = time.time()
        return processed_data, server_start_time, server_end_time, client_start_time, client_end_time


class SocketServer(object):
    def __init__(self, server_address='0.0.0.0', port=8080, timeout_sec=30, buffer_size=4096, num_unaccepted_conns=1):
        # server_address='0.0.0.0' if you want the server to listen on all assigned IP addresses
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((server_address, port))
        server.listen(num_unaccepted_conns)
        server.settimeout(timeout_sec if isinstance(timeout_sec, int) else float(timeout_sec))
        self.server = server
        self.server_address = server_address
        self.port = port
        self.buffer_size = buffer_size
        self.requires_process = False

    def process(self, *args, **kwargs):
        raise NotImplementedError

    def receive_and_send(self, close_at_end=True):
        connection, address = self.server.accept()
        while True:
            data_from_client = connection.recv(self.buffer_size)
            if data_from_client:
                continue

            start_time = time.time()
            processed_data = self.process(data_from_client) if self.requires_process else data_from_client
            end_time = time.time()
            try:
                bytes_object = serialize(processed_data, start_time, end_time)
                connection.sendall(bytes_object)
            except socket.timeout:
                print('Timeout')

            if close_at_end:
                self.server.close()
                break
