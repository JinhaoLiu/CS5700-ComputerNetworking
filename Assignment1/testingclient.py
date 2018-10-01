# This example is using Python 3
import socket
import struct

# Connect to server machine and port.
#
# API: connect(address)
#   connect to a remote socket at the given address.
server_ip = '10.138.0.2'
server_port = 8181
bufsize = 16

# send messages to the server.
messages = [
    [2, 6, '16*2-2', 7, '32/4-16'],
    [2, 7, '16*2-23', 6, '23/4-6'],
    [2, 5, '8/4-2', 6, '10*3+4'],
    [2, 9, '101-100/5', 8, '2*57+401'],
    [1, 21, '-11+2*3+5/4+6*7-8/2*9'],
    [2, 9, '3+12*14-3', 20, '1+12/3+4-5+7-6*31+12'],
    [2, 11, "14-22*16+13", 18, "2-13/2+5-8+9+7*3+1"],
    [2, 10, "4+22*16-13", 19, "2+13/2+5-8+9-7*30+1"],
    [2, 14, '(13+12)*(1+41)', 20, '(((-1+6)*5+6)*9+7)/4'],
    [2, 13, '(3+12)/(1+41)', 20, '(((-1+6)*5+6)*9+7)/4']
]


# encode messages to a byte string
def encode_msg(message):
    # Number of expressions
    num = message[0]
    # size of expressions
    size = message[1::2]
    # length of expressions in bytes
    len_in_byte = list(map(str.encode, message[2::2]))
    fmt = '!h'
    args = []
    for i in range(num):
        fmt += ' h {}s'.format(size[i])
        args.append(size[i])
        args.append(len_in_byte[i])

    return struct.pack(fmt, num, *args)


# decode messages
def decode_msg(encoded_msg):
    # Number of expressions
    num = struct.unpack('!h', encoded_msg[:2])[0]
    c = 2
    res_data = [num]
    for _ in range(num):
        exp_len = struct.unpack('!h', encoded_msg[c:c + 2])[0]
        c += 2

        expression_str = struct.unpack('!{}s'.format(exp_len), encoded_msg[c:c + exp_len])[0].decode()
        c += exp_len

        res_data.extend([exp_len, expression_str])
    return res_data


# receive all data
def recv_all(sock, buf_size):
    result = b''
    while True:
        packet = sock.recv(buf_size)
        result += packet
        if len(packet) < buf_size:
            break
    return result


for i in range(len(messages)):
    # Make a TCP socket object.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    print('Connected to server ', server_ip, ':', server_port)
    print('Client sent:', messages[i])
    request = encode_msg(messages[i])
    # send message to server
    s.sendall(request)
    # receive results from server
    res = recv_all(s, bufsize)
    data = decode_msg(res)
    print('Result_received:', data)
    print('\n')

# Close socket to send EOF to server.
s.close()



