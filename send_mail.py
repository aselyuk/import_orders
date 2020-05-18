# coding: utf-8

import mimetypes
import os
import smtplib
from email import encoders
from email.header import Header
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def attach_file_walker(msg, files):
    for f in files:
        if os.path.isfile(f) and os.path.exists(f):
            attach_file(msg, f)
        elif os.path.exists(f):
            dirs = os.listdir(f)
            for file_ in dirs:
                attach_file(msg, f+"/"+file_)


def read_file(file_path, mode=None):
    if mode is None or mode is "":
        f = open(file_path)
    else:
        f = open(file_path, mode)
    data = f.read()
    f.close()
    return data


def attach_file(msg, filepath):
    filename = os.path.basename(filepath)
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        attach = MIMEText(read_file(filepath), _subtype=subtype)
    elif maintype == 'image':
        attach = MIMEImage(read_file(filepath, 'rb'), _subtype=subtype)
    elif maintype == 'audio':
        attach = MIMEAudio(read_file(filepath, 'rb'), _subtype=subtype)
    else:
        attach = MIMEBase(maintype, subtype)
        attach.set_payload(read_file(filepath, 'rb'))
        encoders.encode_base64(attach)
    attach.add_header('Content-Disposition', 'attachment', filename=filename.encode('utf-8'))
    msg.attach(attach)


def send(email_config, addr_to, msg_subj, msg_text, files=None):
    if files is None:
        files = []
    if addr_to is None:
        addr_to = []
    if len(addr_to) is 0:
        print "recipients list is empty!!!"
        return

    addr_from = email_config["from"]
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = ','.join(addr_to)
    msg['Subject'] = Header(msg_subj, 'utf-8')

    body = msg_text
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    attach_file_walker(msg, files)

    host = email_config["host"]
    port = email_config["port"]
    server = None
    try:
        server = smtplib.SMTP(host, port)
        server.sendmail(addr_from, addr_to, msg.as_string())
    except Exception as ex:
        print ex
    finally:
        if server is not None:
            server.quit()
