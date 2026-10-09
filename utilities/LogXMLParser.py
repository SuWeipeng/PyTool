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

class LogXMLParser:
    """
    解析 XML 获取日志文件的：
    1. 编码格式
    2. 数值单位
    3. 换算成数值单位需乘的倍数
    """
    def __init__(self, xml):
        """
        xml - 解析用到的 XML 文件
        """
        self.fmt_dict  = {}
        self.unit_dict = {}
        self.mul_dict  = {}
        self.tree = ElementTree.parse(xml)
        self.root = self.tree.getroot()

        for child in self.root:
            if child.tag == "format":
                for fmt in child:
                    self.fmt_dict[fmt.attrib["marker"]]   = fmt.attrib["type"]
            elif child.tag == "logUnits":
                for unit in child:
                    self.unit_dict[unit.attrib["marker"]] = unit.attrib["unit"]
            elif child.tag == "logMultipliers":
                for mul in child:
                    v = mul.attrib["multiplier"]
                    if is_number(v):
                        v = float(v)
                    self.mul_dict[mul.attrib["marker"]]   = v
    def print(self):
        """
        输出解析结果
        """
        print(self.fmt_dict)
        print(self.unit_dict)
        print(self.mul_dict)
    def get_unit(self, marker):
        """
        marker - 对应单位的字符标识
        返回：marker 对应单位的字符串
        """
        return self.unit_dict.get(marker)
    def get_mul(self, marker):
        """
        marker - 对应倍数的字符标识
        返回：marker 对应的倍数
        """
        return self.mul_dict.get(marker)