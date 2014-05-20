#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  parse.py
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
#  Модуль разбора скаченного xml файла реестра запрещенных сайтов
#


from __future__ import with_statement
from xml.dom.minidom import *
import os


#  Папка для сохранения списка ip адресов
BLOCKIP_DIR = "./blockip/"
#  Папка для сохранения реестра
REESTR_DIR = "./reestr/"
#  Папка для сохранения файла с маршрутами для роутера
ROUTEIP_DIR = "./blockrouteip/"


class Parse:
    def ParseAllXML(self):
        '''
        Конвертация разпакованного файл dump.xml
        в файл csv для более легкого анализа в Exel или Calc
        '''
        xml_file = unicode('dump.xml')
        xml = parse(xml_file)
        updateTime = xml.getElementsByTagName('reg:register')[0] \
                                           .getAttribute('updateTime').strip()
        parse_file = REESTR_DIR + 'reestr_' + updateTime[0:10] + '_' + \
                           updateTime[11:13] + '-' + updateTime[14:16] +'.csv'
        out_file = open(parse_file, 'w')
        out_file.truncate()
        out_file.write(updateTime + '\n')
        content = xml.getElementsByTagName('content')
        for node in content:
            row = []
            _id = node.getAttribute('id').strip()
            row.append(_id)
            _date = node.getElementsByTagName('decision')[0] \
                                                 .getAttribute('date').strip()
            row.append(_date)
            _number = node.getElementsByTagName('decision')[0] \
                                               .getAttribute('number').strip()
            row.append(_number)
            _org = node.getElementsByTagName('decision')[0] \
                                                  .getAttribute('org').strip()
            row.append(_org)
            _url = node.getElementsByTagName('url')[0] \
                                                      .firstChild.data.strip()
            row.append(_url)
            #  Проверяем указан домен или нет
            if node.getElementsByTagName('domain'):
                _domain = node.getElementsByTagName('domain')[0] \
                                                      .firstChild.data.strip()
                row.append(_domain)
            else:
                _domain = ' '
                row.append(_domain)
            #  Если указанно несколько IP адресов, то заносится только первый
            _ip = node.getElementsByTagName('ip')[0].firstChild \
                                                            .nodeValue.strip()
            row.append(_ip)
            row.append('\n')
            data = ';'.join(row)
            data = data.encode('cp1251')
            out_file.write(data)
        out_file.close()   
        return parse_file    


    def ParseIpXML(self):
        '''
        Парсинг разпакованного файла dump.xml.
        Выбирает все IP адреса, удаляет дубликаты, сортирует
        и записывает в два текстовых файла:
        blockIP_HHHH-MM-DD_hh-mm.txt - отсортированный список уникальных IP
        blockiproute.txt - список маршрутов блокирования для роутера, ввида:
        ip route 10.0.0.1/32 Null0 254
        '''
        xml_file = unicode('dump.xml')
        xml = parse(xml_file)
        updateTime = xml.getElementsByTagName('reg:register')[0] \
                                           .getAttribute('updateTime').strip()
        parse_file = BLOCKIP_DIR + 'blockIP_' + updateTime[0:10] + '_' + \
                            updateTime[11:13] + '-' + updateTime[14:16]+'.txt'
        out_file = open(parse_file, 'w')
        out_file.truncate()
        ip_file = open(ROUTEIP_DIR + 'blockiproute.txt', 'w')
        ip_file.truncate()
        name = xml.getElementsByTagName('ip')
        list_ip = []
        for node in name:
            _ip = node.childNodes[0].nodeValue
            # удаление дубликатов IP адресов     
            if _ip in list_ip: 
                pass
            else:
                list_ip.append(_ip)
        list_ip.sort()
        # запись списка в файлы
        for i in xrange(len(list_ip)):
            data = list_ip[i] + '\n'
            iproute = "ip route " + list_ip[i] + "/32 Null0 254\n"
            out_file.write(data) 
            ip_file.write(iproute)
        out_file.close()
        ip_file.close()   
        return parse_file
            

 



   
