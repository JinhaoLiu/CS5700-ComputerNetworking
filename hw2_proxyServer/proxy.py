# This file is using Python 3
import socket
import datetime
import _thread
import re
import logging

# Get host name, IP url, and port number.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
host_port = 8181
print(host_ip, ':', host_port)

# Make a TCP socket object.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Resolve binding socket:" Address already in use"
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to server IP and port number.
s.bind((host_ip, host_port))

# Listen allow 5 pending connects.
s.listen(5)

print('\nServer started. Waiting for connecting...\n')
buf_size = 1024


def recv_all(conn, buf_size):
    res = b''
    while True:
        data = conn.recv(buf_size)
        if not data:
            break
        res += data
    return res


# Receive server's data until reaching '\r\n\r\n'
def recv_req_header(conn, buf_size):
    res = b''
    while True:
        data = conn.recv(buf_size).decode()
        i = data.find('\r\n\r\n')
        if i != -1:
            res += data[:i].encode()
            break
    return res


def construct_req_header(http_method, url, http_version, host):
    return '{} {} {}\r\nHost: {}\r\nConnection: close\r\n\r\n'\
        .format(http_method, url, http_version, host)


def parse_request(raw_request):
    request = raw_request
    parts = request.split('\r\n')
    http_method, url, http_version = parts[0].split(' ')
    host = parts[1][6:]
    port = 80
    if re.match('.*:[0-9]+.*', url):
        port = int(re.search(':([0-9]+)/', url)[1])
        host = re.search('//(.*?):', url)[1]
    return http_method, url, http_version, port, host


def handler(conn):
    req = recv_req_header(conn, buf_size).decode()
    http_method, url, http_version, port, host = parse_request(req)
    logging.info('Request received: {} {}'.format(http_method, url))
    # print(http_method, url, port, host)
    if http_method != "GET":  # TODO: test this
        msg = 'HTTP/1.1 405 Method Not Allowed\r\nDate: {}\r\nConnection: close\r\n\r\n'\
            .format(datetime.datetime.now().strftime("%a, %d %b %Y %T PST"))
        logging.error('Only GET request is supported, got {}'.format(http_method))
        conn.sendall(msg.encode())
        conn.close()
        return

    # Make TCP connection to the "real" Web server;
    new_req = construct_req_header(http_method, url, http_version, host).encode()
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((host, port))
    logging.info('Connected to host: {}, forwarding request...'.format(host))

    s2.sendall(new_req)
    res = recv_all(s2, buf_size)
    logging.info('Response received from remote host')
    s2.close()

    logging.info('Sending response back to client...')
    conn.sendall(res)
    conn.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    while True:
        conn, addr = s.accept()
        logging.info('Server connected by {} at {}'.format(addr, datetime.datetime.now()))
        _thread.start_new(handler, (conn,))
