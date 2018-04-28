import os
import socket
import ssl
import base64

def send_message(conf, msg):
    message = f'Content-Type: text/plain; charset=utf-8\n\n{msg}'

    head = '\n'.join((f'From: {conf["From"][0]}(Hackerman)',
                      f'To: {",".join(conf["To"])}',
                      f'Subject: {conf["Subject"][0]}'))

    messages = ['EHLO hackerman.ru', 
                'AUTH LOGIN',
                b64encode(conf["From"][0]),
                b64encode('fortest'),
                f'MAIL FROM: {conf["From"][0]}',
                *[f'RCPT TO: {to}' for to in conf['To']],
                'DATA',
                get_attachments(conf, head, message),
                'QUIT'
                ]

    sock = ssl.SSLSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    sock.connect(('smtp.yandex.ru', 465))
    data = sock.recv(1024)
    print(data.decode())
    for i in messages:
        sock.send(i.encode() + b'\r\n')
        data = sock.recv(1024)
        print(data.decode())
    sock.close()


def get_attachments(conf, head, msg):
    if 'Attachments' not in conf:
        return '\n'.join((head, msg, '.'))
    boundary = get_bound(msg)
    cont = ['\n'.join((
                    f'--{boundary}',
                    f'Content-Disposition: attachment; filename={a}',
                    'Content-Transfer-Encoding: base64',
                    f'Content-Type: {typeof(a.split(".")[1])}; name={a}\n',
                    get_file(a))) for a in conf["Attachments"]]

    return '\n'.join(( head,
                    f'Content-Type: multipart/mixed; boundary={boundary}\n',
                    f'--{boundary}',
                    msg,
                    *cont,
                    f'--{boundary}--', '.'))


def get_bound(msg):
    b = '~'
    i = 0
    while b in msg:
        i += 1
        b += str(i)
    return b


def get_file(file):
    with open(file, 'br') as f:
        return base64.b64encode(f.read()).decode()


def typeof(_type):
    return 'image/jpeg' if _type in ('jpeg', 'jpg') else 'image/png' if _type == 'png' else 'application/pdf'


def b64encode(obj):
    return base64.b64encode(obj.encode()).decode()


def main():
    config = {}
    with open("letter.txt") as f:
        text = f.read().encode('cp1251').decode().replace('\n.', '\n. ')
    with open("configure.txt") as f:
        for line in f.readlines():
            s = line.encode("cp1251").decode().split(':')
            config[s[0]] = [i.strip() for i in s[1].split(',')]
    print(config)
    print(text)
    send_message(config, text)

if __name__ == '__main__':
    main()
