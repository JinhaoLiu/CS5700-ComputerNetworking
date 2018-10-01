# This example is using Python 3
import socket
import struct
import time
import _thread

# Get host name, IP address, and port number.
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
host_port = 8181

# Make a TCP socket object.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to server IP and port number.
s.bind((host_ip, host_port))

# Listen allow 10 pending connects.
s.listen(10)
print(host_ip, ':', host_port)
print('\nServer started. Waiting for connection...\n')

# the buffer size of server
buf_size = 16


# Current time on the server.
def now():
    return time.ctime(time.time())


def handler(conn):
    data = recv_all(conn, buf_size)
    # Number of expressions
    num = struct.unpack('!h', data[:2])[0]
    i = 2
    res = b''
    res += struct.pack('!h', num)
    for _ in range(num):
        exp_len = struct.unpack('!h', data[i:i+2])[0]
        i += 2
        exp_str = struct.unpack('!{}s'.format(exp_len), data[i:i+exp_len])[0].decode()

        # calculate expression result and pack response data
        result = calculate(exp_str)
        res += struct.pack('!h {}s'.format(len(result)), len(result), result.encode())

        i += exp_len
        print('resp >> len: {}, result: {}'.format(exp_len, exp_str))

    # simulate long running program
    time.sleep(3)
    conn.sendall(res)
    conn.close()


# Calculate expression
def calculate(expression):
    def helper(expression, i):
        pre_val, res = 0, 0
        sign = '+'

        while i < len(expression):
            c = expression[i]
            if c == '(' or c.isdigit():
                if c == '(':
                    val, x = helper(expression, i+1)
                    i = x
                else:
                    val = int(c)
                    while i+1 < len(expression) and expression[i+1].isdigit():
                        val = val * 10 + int(expression[i+1])
                        i += 1
                if sign == '+':
                    res += pre_val
                    pre_val = val
                elif sign == '-':
                    res += pre_val
                    pre_val = -val
                elif sign == '/':
                    pre_val //= val
                elif sign == '*':
                    pre_val *= val
            elif c == ')':
                return res+pre_val, i
            else:
                sign = c
            i += 1

        return res+pre_val, len(expression)-1
    return str(helper(expression, 0)[0])


# receive all data.
def recv_all(sock, buf_size):
    response = b''
    while True:
        packet = sock.recv(buf_size)
        response += packet
        if len(packet) < buf_size:
            break
    return response


while True:
    conn, addr = s.accept()
    print('Server connected by', addr, 'at', now())
    _thread.start_new(handler, (conn,))
