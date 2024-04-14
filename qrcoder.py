import os

import qrcode
import base64


def get_qrcode(url):
    qr = qrcode.make(data=url)
    qr.save(stream='qr.jpg')

    with open('qr.jpg', mode='rb') as f:
        data = f.read()

    bytes_qr = base64.b64encode(data).decode("ascii")

    return bytes_qr
