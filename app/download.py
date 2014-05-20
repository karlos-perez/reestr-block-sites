#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  download.py
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
#  Загрузка и обработка реестра запрещенных сайтов
#
#


import os
import shutil
import time
import zipfile
from base64 import b64decode
from datetime import datetime,timedelta
from network import Network
from parse import Parse

#  Файл запроса
REQ_FILE_NAME = "req.xml"
#  Файл подписи запроса
P7S_FILE_NAME = "req.xml.sig"
#  Папка файлов архива скачанного реестра
date = datetime.now()
ARCHIVE = './archive/'+ date.strftime('%Y%m%d-%H%M') + '/'



class Download:
    '''
    Загрузка и обработка реестра запрещенных файлов и уведомление
    о результатах по почте
    '''
    def __init__(self): 
        self.reestr()


    def reestr(self):
        sender = Network()
        #  Отправляем запрос на выгрузку
        request = sender.send_request(REQ_FILE_NAME,P7S_FILE_NAME)
        msg =  10*'*' + '%s' % date + 10*'*' + '\n'
        msg = msg + 'Отправлен запрос на загрузку реестра.\n'
        #  Проверяем, принят ли запрос к обработке
        if request['result']:  #  Запрос принят, получен код
            code=request['code']
            msg = msg + 'Получили код: %s\n' % (code)
            while 1:
                #  Пытаемся получить архив по коду
                msg = msg + 'Пытаемся получить архив по коду...'
                request = sender.get_result(code)
                if request['result']:
                    #Архив получен, скачиваем его и распаковываем
                    msg = msg + 'Реестр скачен.\n'
                    result_file = open('result.zip', "wb")
                    result_file.write(b64decode(request['registerZipArchive']))
                    result_file.close()
                    zip_f = zipfile.ZipFile('result.zip', 'r')
                    zip_file = zip_f.read('dump.xml')
                    dump_xml = open('dump.xml', 'w')
                    dump_xml.write(zip_file)
                    dump_xml.close()
                    zip_f.close()
                    msg = msg + "Разархивированно..\n"
                    #Создаем папку для архива
                    try:
                        os.makedirs(ARCHIVE)
                        msg = msg + 'Новые папки созданы!\n'
                    except OSError:
                        msg = msg + "Ошибка создания папки архива\n"
                    #  Парсим полученный реестр (файл dump.xml)
                    processing = Parse()
                    reestr = processing.ParseAllXML()
                    msg = msg + "Парсинг XML-файла реестра... OK!\n"
                    reestr_ip = processing.ParseIpXML()
                    msg = msg + "Парсинг IP-адресов... OK!\n"
                    # Переносим dump.xml и result.zip в архив
                    shutil.move('dump.xml', ARCHIVE)
                    shutil.move('result.zip', ARCHIVE)
                    msg = msg + "Перемещение в архив... OK!\n"
                    msg = msg + 'Реестр загружен и обработан\n'
                    break
                else:
                    #Архив не получен, проверяем причину.
                    if request['resultComment']=='запрос обрабатывается':
                        #  Если это сообщение об обработке запроса,
                        #  то просто ждем минутку
                        msg = msg + 'Реестр еще не подготовлен\n'
                        time.sleep(120)
                    else:
                        #  Если это любая другая ошибка,
                        #  выводим ее и прекращаем работу
                        msg = msg + 'Ошибка: %s\n' % request['resultComment']
                        break
        else:
            #Запрос не принят, возвращаем ошибку
            msg = msg + 'Ошибка: %s\n' % request['resultComment']
        msg = msg + 45*'*' + '\n'
        #  Отправляем уведомление о результатах
        send = Network()
        send.send_mail(msg)
