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
        # param 下除 <values> 外还有 <field>/<bitmask> 等子元素，只处理 <values>
        vehicles = self.tree.find('vehicles')
        if vehicles is not None:
            for obs in vehicles:
                if obs.attrib.get('name') == self.vehicle:
                    for param in obs:
                        for values in param:
                            if values.tag != 'values':
                                continue
                            p_name = param.attrib.get('name').split(':')[1]
                            self.param_name_dict[p_name]={}
                            for value in values:
                                v = value.attrib.get('code')
                                self.param_name_dict[p_name][v]=value.text
        for obs in self.tree.find('libraries'):
            for param in obs:
                for values in param:
                    if values.tag != 'values':
                        continue
                    p_name = param.attrib.get('name')
                    self.param_name_dict[p_name]={}
                    for value in values:
                        v = value.attrib.get('code')
                        self.param_name_dict[p_name][v]=value.text
        return self.param_name_dict
