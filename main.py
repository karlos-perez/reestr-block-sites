#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
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


import os
import app.download

#  Settings:
REQ_FILE_NAME = "req.xml" #  Файл запроса
P7S_FILE_NAME = "req.xml.sig" #  Файл подписи запроса
API_URL = "http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl" #  Ссылка выгрузки реестра запрещенных сайтов
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_NUM = 2.0  # Версия выгрузки (2.0 - действует с 01.08.2014г.)
REESTR_FILE = BASE_DIR + '/dump.xml' # Распакованный файл с реестром
REESTR_ZIP = BASE_DIR + '/result.zip'

def main():
    app.download.Download()
    return 0


if __name__ == '__main__':
    main()
