import socket
import time


class ClientError(Exception):
    pass


class Client:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        # not using the context manager due to the task
        self.sock = socket.create_connection((self.host, self.port))
        if timeout is not None:
            self.sock.settimeout(timeout)

    @staticmethod
    def output_validator(parsed_string):
        if parsed_string[0] != 'ok' or parsed_string[len(parsed_string) - 1] != '' or \
                parsed_string[len(parsed_string) - 2] != '':
            raise ClientError
        else:
            pass

    def get(self, key):
        self.sock.sendall("{} {}\n".format('get', key).encode("utf8"))
        while True:
            try:
                data = self.sock.recv(1024)
            except socket.timeout:
                print('connection closed by timeout')
                break
            if not data:
                break

            parsed_string = data.decode("utf8").split("\n")
            try:
                Client.output_validator(parsed_string)
                # positive answer 'ok\n\n'
                if len(parsed_string) == 3:
                    return dict()
                # positive answer with useful data
                position = 1
                get_dict = dict()
                while position <= len(parsed_string) - 3:
                    new_key = parsed_string[position].split(' ')[0]
                    new_metric_value = parsed_string[position].split(' ')[1]
                    new_timestamp = parsed_string[position].split(' ')[2]

                    try:

                        new_metric_value = float(new_metric_value)
                        new_timestamp = int(new_timestamp)

                        if new_key not in get_dict.keys():
                            get_dict[new_key] = [(new_timestamp, new_metric_value)]
                        else:
                            get_dict[new_key].append((new_timestamp, new_metric_value))
                    except ValueError:
                        raise ClientError

                    position += 1

            except (ClientError, IndexError):
                raise ClientError

            for k in get_dict:
                get_dict[k] = sorted(get_dict[k], key=lambda tup: tup[0])

            return get_dict

    def put(self, key, value, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())

        self.sock.sendall("{} {} {} {}\n".format('put', key, value, timestamp).encode("utf8"))
        while True:
            try:
                data = self.sock.recv(1024)
            except socket.timeout:
                print('connection closed by timeout')
                break
            if not data:
                break

            parsed_string = data.decode("utf8").split("\n")
            try:
                Client.output_validator(parsed_string)
                # positive answer 'ok\n\n'
                if len(parsed_string) == 3:
                    return
            except ClientError:
                raise
