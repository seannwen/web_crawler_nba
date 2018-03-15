#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def send_email(subject, message):
    with open('config.json') as config:
        config_data = json.load(config)
        smtp_host = config_data['smtp_host']
        smtp_port = config_data['smtp_port']
        email = config_data['email']
        password = config_data['password']

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(email, password)

        msg = MIMEMultipart()

        # msg.attach(MIMEText(open(filename, 'rb').read()))

        html_start = '<font face="Courier New, Courier, monospace"><pre>'
        html_end = '</pre></font>'
        msg = MIMEText(html_start + message.replace('\\n', '<br/>') + html_end, _subtype='html', _charset='utf-8')
        msg['Subject'] = Header(subject)

        server.sendmail("programmingemail0930@gmail.com", "luckymanyo@gmail.com", msg.as_string())

        server.quit()
