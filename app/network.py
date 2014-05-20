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


#  Ссылка выгрузки реестра запрещенных сайтов
API_URL = "http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl"
#  отправитель
FROM = 'server@exemple.com'
#  получатель
TO = 'user@exemple.com'


class Network:
    def send_request(self,requestFile,signatureFile):
        '''
        Отправка запроса в РКН на выгрузку рееста.
        Отправляется файл запроса и файл подписи.
        Возвращается результат запроса: запрос принят - код получен или 
        запрос не принят - причины. 
        '''
        req_file = open(requestFile, "rb")
        data = req_file.read()
        req_file.close()
        xml = b64encode(data)
        sign_file = open(signatureFile, "rb")
        data = sign_file.readlines()
        sign_file.close()
        if '-----' in data[0]:
            sert = ''.join(data[1:-1])
        else:
            sert = b64encode(sert)
        client = suds.client.Client(API_URL)
        result=client.service.sendRequest(xml,sert)
        return dict(((k, v.encode('utf-8')) \
                                    if isinstance(v, suds.sax.text.Text) \
                                    else (k, v)) for (k, v) in result)


    def get_result(self,code):
        '''
        Загрузка реестра по коду 
        '''
        client = suds.client.Client(API_URL)
        result=client.service.getResult(code)
        return dict(((k, v.encode('utf-8')) \
                                    if isinstance(v, suds.sax.text.Text) \
                                    else (k, v)) for (k, v) in result)
        
        
    def send_mail(self,message):
        '''
        Отправка уведомления по почте о результатах выгрузки реестра.
        '''
        Date = datetime.now()
        # текст письма
        text = message
        # заголовок письма
        subj = 'Peecтр загружен %s' % Date.strftime('%Y%m%d-%H%M')
        # SMTP-сервер
        server = "mail.exemple.com"
        port = 25
        user_name = "server.exemple.com"
        user_passwd = "password"
        # формирование сообщения
        msg = MIMEText(text, "", "utf-8")
        msg['Subject'] = subj
        msg['From'] = FROM
        msg['To'] = TO
        # отправка
        s = smtplib.SMTP(server, port)
        s.sendmail(FROM, TO, msg.as_string())
        s.quit()
