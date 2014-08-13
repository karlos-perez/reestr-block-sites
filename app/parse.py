#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# parse.py
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
#  Версия выгрузки 2.0 (с 01.08.2014)


import os
import main
from xml.dom.minidom import *


#  Папка для сохранения списка ip адресов
BLOCKIP_DIR = main.BASE_DIR + "/blockip/"
#  Папка для сохранения реестра
REESTR_DIR = main.BASE_DIR + "/reestr/"
#  Папка для сохранения файла с маршрутами для роутера
ROUTEIP_DIR = main.BASE_DIR + "/blockrouteip/"



class Parse:
    def parse_dump_file(self):
        with open(main.REESTR_FILE, 'r') as dump_file:
            xml_file = parse(dump_file)
        updateTime = xml_file.getElementsByTagName('reg:register')[0].getAttribute('updateTime').strip()
        self.parse_all_xlm(updateTime, xml_file)
        self.parse_ip_xml(updateTime, xml_file)

    def parse_all_xlm(self, time, file_xml):
        """
        Преобразуем разпакованный файл dump.xml
        в текстовый файл csv
        """
        parse_file_name = 'reestr_' + time[0:10] + '_' + time[11:13] + \
                          '-' + time[14:16] + '.csv'
        parse_file = os.path.join(REESTR_DIR, parse_file_name)
        content = file_xml.getElementsByTagName('content')
        result_list = []
        for node in content:
            node_list = []
            node_list.append(node.getAttribute('id').strip())
            node_list.append(node.getAttribute('includeTime').strip())
            node_list.append(node.getAttribute('entryType').strip())
            node_list.append(node.getElementsByTagName('decision')[0].getAttribute('org').strip())
            node_list.append(node.getElementsByTagName('decision')[0].getAttribute('number').strip())
            node_list.append(node.getElementsByTagName('decision')[0].getAttribute('date').strip())
            if node.getElementsByTagName('domain'):
                _domains = node.getElementsByTagName('domain')
                for _domain in _domains:
                    node_list.append((_domain.firstChild.data.strip()))
            else:
                node_list.append(" ")
            if node.getElementsByTagName('url'):
                _urls = node.getElementsByTagName('url')
                for _url in _urls:
                    node_list.append((_url.firstChild.data.strip()))
            else:
                node_list.append(" ")
            if node.getElementsByTagName('ip'):
                _ips = node.getElementsByTagName('ip')
                for _ip in _ips:
                    node_list.append(str(_ip.childNodes[0].nodeValue.strip()))
            else:
                node_list.append(" ")
            if node.getElementsByTagName('ipSubnet'):
                _ipSubnets = node.getElementsByTagName('ipSubnet')
                for _ipSubnet in _ipSubnets:
                    str(_ipSubnet.firstChild.data.strip())
                    node_list.append(str(_ipSubnet.firstChild.data.strip()))
            else:
                node_list.append(" ")
            result_list.append(';'.join(node_list))
        with open(parse_file, 'w') as result_file:
            result_file.truncate()
            result_file.write(time)
            for nod in result_list:
                nod = nod.encode('cp1251')
                result_file.write(nod + '\n')
        return parse_file

    def parse_ip_xml(self, time, file_xml):
        """
        Парсинг разпакованного файла dump.xml.
        Выбирает все IP адреса, удаляет дубликаты, сортирует
        и записывает в два текстовых файла:
        blockIP_HHHH-MM-DD_hh-mm.txt - отсортированный список уникальных IP
        blockiproute.txt - список маршрутов блокирования для роутера, ввида:
        ip route 10.0.0.1/32 Null0 254
        """
        parse_file = BLOCKIP_DIR + 'blockIP_' + time[0:10] + '_' + \
                     time[11:13] + '-' + time[14:16] + '.txt'
        _ip = file_xml.getElementsByTagName('ip')
        list_ip = []
        for ip in _ip:
            ip_adress = ip.childNodes[0].nodeValue
            if not ip_adress in list_ip:
                list_ip.append(ip_adress)
        list_ip.sort()
        _ipSubnet = file_xml.getElementsByTagName('ipSubnet')
        list_subnet = []
        if _ipSubnet:
            for subnet in _ipSubnet:
                ipSubnet = subnet.childNodes[0].nodeValue
                if not ipSubnet in list_subnet:
                    list_subnet.append(ipSubnet)
            list_subnet.sort()
        with open(parse_file, 'w') as ip_file:
            for ip in list_ip:
                ip_file.write(ip + '\n')
            for subnet in list_subnet:
                ip_file.write(subnet + '\n')
        with open(ROUTEIP_DIR + 'blockiproute.txt', 'w') as route_file:
            route_file.truncate()
            for ip in list_ip:
                route_ip = "ip route " + ip + "/32 Null0 254\n"
                route_file.write(route_ip)
            for subnet in list_subnet:
                route_subnet = "ip route " + subnet + " Null0 254\n"
                route_file.write(route_subnet)
        return parse_file