#!/usr/bin/python3
# -*- coding:utf-8 -*-

def is_number(s):
    """
    判断 s 是否是数字
    是：返回 True
    否：返回 False
    """
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False

from xml.etree import ElementTree

class ParamXMLParser:
    def __init__(self, xml, vehicle):
        """
        xml - 解析用到的 XML 文件
        """
        self.vehicle = vehicle
        self.tree = ElementTree.parse(xml)
        self.root = self.tree.getroot()
        self.root_tag = self.root.tag
        self.root_attrib = self.root.attrib
        self.param_name_dict = {}

    def parse_code_meaning(self):
        vehicle = self.tree.find('vehicles')
        for obs in vehicle:
            if obs.attrib.get('name') == self.vehicle:
                for param in obs:
                    for values in param:
                        if values.tag == 'values':
                            p_name = param.attrib.get('name').split(':')[1]
                            self.param_name_dict[p_name]={}
                        i = 0
                        for value in values:
                            v = value.attrib.get('code')
                            self.param_name_dict[p_name][v]=''
                            i+=1
                        if i != 0:
                            for index in range(len(self.param_name_dict[p_name].keys())):
                                keys = list(self.param_name_dict[p_name].keys())
                                self.param_name_dict[p_name][keys[index]]=values[index].text
        for obs in self.tree.find('libraries'):
            for param in obs:
                for values in param:
                    if values.tag == 'values':
                        p_name = param.attrib.get('name')
                        self.param_name_dict[p_name]={}
                    i = 0
                    for value in values:
                        v = value.attrib.get('code')
                        self.param_name_dict[p_name][v]=''
                        i+=1
                    if i != 0:
                        for index in range(len(self.param_name_dict[p_name].keys())):
                            keys = list(self.param_name_dict[p_name].keys())
                            self.param_name_dict[p_name][keys[index]]=values[index].text
        return self.param_name_dict
