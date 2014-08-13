#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  network.py
#
#  Copyright 2014 Alexei Krivtsov <kralole@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#
#  Эта программа является свободным программным обеспечением; вы можете
#  распространять и/или изменять в соответствии с условиями GNU General
#  Public License, опубликованной Free Software Foundation; либо
#  версии 2 Лицензии, либо (по вашему выбору) любой более поздней версии.
#
#  Эта программа распространяется в надежде, что она будет полезной,
#  но БЕЗ ВСЯКИХ ГАРАНТИЙ; даже без подразумеваемой гарантии
#  или ПРИГОДНОСТИ ДЛЯ КОНКРЕТНЫХ ЦЕЛЕЙ. Смотрите
#  GNU General Public License для более подробной информации.
#
#
#  Модуль работы с сетью: отправка запроса на выгрузку реестра, загрузка
#  реестра и отправка уведомления на e-mail
#

import suds
import smtplib
from base64 import b64encode
from datetime import datetime
from email.MIMEText import MIMEText

import main

# Настройки SMTP-сервера для уведомления
FROM_EMAIL = 'server@exemple.com'  # с какой почты отправлять уведомление
TO_EMAIL = 'user@exemple.com'  # кому отправлять уведомление
SMTP_SERVER = 'mail.exemple.com'  # кому отправлять уведомление
PORT = 25
#USER_NAME = ' '
#USER_PASS = ' '


class Network:
    def send_request(self,requestFile,signatureFile):
        """
        Отправка запроса в РКН на выгрузку рееста.
        Отправляется файл запроса и файл подписи.
        Возвращается результат запроса: запрос принят - код получен или
        запрос не принят - причины.
        """
        with open(requestFile, "rb") as req_file:
            req_xml = req_file.read()
        with open(signatureFile, "rb") as sign_file:
            data = sign_file.readlines()
        req = b64encode(req_xml)
        if '-----' in data[0]:
            sert = ''.join(data[1:-1])
        else:
            sert = ''.join(data)
        sert = b64encode(sert)
        client = suds.client.Client(main.API_URL)
        result = client.service.sendRequest(req, sert, main.VERSION_NUM)

        return dict(((k, v.encode('utf-8')) \
                                    if isinstance(v, suds.sax.text.Text) \
                                    else (k, v)) for (k, v) in result)


    def get_result(self,code):
        '''
        Загрузка реестра по коду 
        '''
        client = suds.client.Client(main.API_URL)
        result=client.service.getResult(code)
        return dict(((k, v.encode('utf-8')) \
                    if isinstance(v, suds.sax.text.Text) \
                                    else (k, v)) for (k, v) in result)
        
        
    def send_mail(self,message):
        """
        Отправка уведомления по почте о результатах выгрузки реестра.
        """
        Date = datetime.now()
        # текст письма
        text = message
        # заголовок письма
        subj = 'Выгрузка реестра %s' % Date.strftime('%Y%m%d-%H%M')
        msg = MIMEText(text, "", "utf-8")
        msg['Subject'] = subj
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        # отправка
        s = smtplib.SMTP(SMTP_SERVER, PORT)
        s.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        s.quit()
