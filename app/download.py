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
#  Формат выгрузки 2.0 (действует с 01.08.2014)



import os
import shutil
import time
import zipfile
from base64 import b64decode
from datetime import datetime,timedelta

import main
import parse
from network import Network





#  Папка файлов архива скачанного реестра
date = datetime.now()
ARCHIVE = main.BASE_DIR + '/archive/'+ date.strftime('%Y%m%d-%H%M') + '/'



class Download:
    """
    Загрузка и обработка реестра запрещенных файлов и уведомление
    о результатах по почте
    """
    def __init__(self): 
        self.reestr()

    def reestr(self):
        sender = Network()
        #  Отправляем запрос на выгрузку
        request = sender.send_request(main.REQ_FILE_NAME, main.P7S_FILE_NAME)
        msg =  10*'*' + '%s' % date + 10*'*' + '\n'
        msg = msg + 'Отправлен запрос на загрузку реестра.\n'
        #  Проверяем, принят ли запрос к обработке
        if request['result']:  #  Запрос принят, получен код
            code=request['code']
            msg = msg + 'Код выгрузки: %s\n' % (code)
            while 1:
                #  Пытаемся получить архив по коду
                #msg = msg + 'Пытаемся получить архив по коду...'
                request = sender.get_result(code)
                if request['result']:
                    #Архив получен, скачиваем его и распаковываем
                    #msg = msg + 'Реестр скачен.\n'
                    with open(main.REESTR_ZIP, "wb") as result_file:
                        result_file.write(b64decode(request['registerZipArchive']))
                    with open(main.REESTR_FILE, 'w') as dump_xml:
                        try:
                            zip_f = zipfile.ZipFile(main.REESTR_ZIP, 'r')
                            dump_xml.write(zip_f.read('dump.xml'))
                            zip_f.close()
                        except:
                            msg = msg + 'Ошибка разархивирования!\n'
                    #Создаем папку для архива
                    try:
                        os.makedirs(ARCHIVE)
                    except OSError:
                        msg = msg + "Ошибка создания папки архива\n"
                    #  Парсим полученный реестр (файл dump.xml)
                    processing = parse.Parse()
                    try:
                        processing.parse_dump_file()
                    except:
                        msg = msg + "Ошибка парсинг XML-файла реестра!\n"
                    try: # Перенос dump.xml и result.zip в архив
                        shutil.move(main.REESTR_FILE, ARCHIVE)
                        shutil.move(main.REESTR_ZIP, ARCHIVE)
                    except:
                        msg = msg + "Ошибка перемещения файлов в архив... OK!\n"
                    break
                else:
                    #Архив не получен, проверяем причину.
                    if request['resultComment']=='запрос обрабатывается':
                        #  Если это сообщение об обработке запроса,
                        #  то просто ждем минутку
                        #msg = msg + 'Реестр еще не подготовлен\n'
                        time.sleep(120)
                    else:
                        #  Если это любая другая ошибка,
                        #  выводим ее и прекращаем работу
                        msg = msg + "Ошибка: %s\n" % request['resultComment']
                        break
        else:
            #Запрос не принят, возвращаем ошибку
            msg = msg + "Ошибка: %s\n" % request['resultComment']
        msg = msg + 45*'*' + '\n'
        #  Отправляем уведомление о результатах
        send = Network()
        send.send_mail(msg)
