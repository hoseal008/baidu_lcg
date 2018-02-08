# coding=utf-8
import base64
import socket
import struct

server_name = '120.77.205.16'
# streaming1_server_name = 'localhost'
server_port = 13897

client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client1.connect((server_name, server_port))

token = "asdf****er"


def online_ocr(img_b64):
    size = len(img_b64)
    fhead = struct.pack('20sI', token + '#', size)
    client1.send(fhead)
    client1.send(img_b64)
    result = client1.recv(10)
    return result


if __name__ == "__main__":

    with open('data/captcha.jpg', 'rb') as f:
        image = f.read()

    img_b64 = base64.b64encode(image)
    print online_ocr(img_b64)
