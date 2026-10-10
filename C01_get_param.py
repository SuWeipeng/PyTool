#!/usr/bin/python3
# -*- coding:utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
import sys
import os
from utilities.LogDBParser import LogDBParser
from utilities.ParamCare import care_params
import platform
import matplotlib

# Check if running on Linux
if platform.system() == 'Linux':
    try:
        matplotlib.use('TkAgg')
    except ImportError:
        print("sudo apt-get install python3-tk")
        # Fallback to default backend
        pass

# Handle command line arguments
if len(sys.argv) > 1:
    db_name = sys.argv[1]
else:
    db_name = "D:/Log/00000002.db"
# Cross-platform path handling
db_path = os.path.join('..', db_name)

# Check if file exists
if not os.path.exists(db_path):
    print(f"Error: Database file not found: {db_path}")
    sys.exit(1)

log = LogDBParser(db_path)

# 到 utilities 目录下的 ParamCare.py 中填写
# 需要醒目标出的参数，不推荐在此手动填写
#care_params = ['servo1_function', 'RC8_DZ']
ratio = 0.999

data          = log.getData("PARM","Name","Value")

name  = data[0]
value = data[1]
parms = {}

from utilities.ParamXMLParser import ParamXMLParser
xml = ParamXMLParser('utilities/apm.pdef.xml', 'ArduCopter')
meaning_dict = xml.parse_code_meaning()
meaning_param = list(meaning_dict.keys())

for i in range(len(name)):
    parms[name[i]]=value[i]

os.makedirs("params", exist_ok=True)
parm_file_name = "params/"+os.path.basename(db_name).split('.')[0]+".html"
if len(care_params) > 0:
    care_file_name = "params/"+os.path.basename(db_name).split('.')[0]+"_care.html"
    care_file = open(care_file_name,'w',encoding='utf-8')

with open(parm_file_name,'w',encoding='utf-8') as file:
    if len(care_params) > 0:
        care_file.write('<table>\n')
        care_file.write('''    <tr align="left">
        <th bgcolor="#F6F6F6">seq</th>
        <th bgcolor="#F6F6F6">NAME</th>
        <th bgcolor="#F6F6F6">VALUE</th>
        <th bgcolor="#F6F6F6">MEANING</th>
    </tr>''')
    file.write('<table>\n')
    file.write('''    <tr align="left">
        <th bgcolor="#F6F6F6">seq</th>
        <th bgcolor="#F6F6F6">NAME</th>
        <th bgcolor="#F6F6F6">VALUE</th>
        <th bgcolor="#F6F6F6">MEANING</th>
    </tr>''')
    index = 0
    care_index = 0
    for i in sorted(parms):
        import difflib
        care = False
        for j in range(len(care_params)):
            compare = difflib.SequenceMatcher(None, i, care_params[j].upper()).quick_ratio()
            if compare > ratio:
                care = True
                break
        if i in meaning_param:
            try:
                meaning = meaning_dict[i][str(parms[i]).split('.')[0]]
            except:
                meaning = '&#32;'
        else:
            meaning = '&#32;'
        if care:
            if len(care_params) > 0:
                if care_index % 2 == 0:
                    care_file.write('''
    <tr >
        <td bgcolor="#FDFDFD">%s</td>
        <td bgcolor="#FDFDFD">%s</td>
        <td bgcolor="#FDFDFD">%s</td>
        <td bgcolor="#FDFDFD">%s</td>
    </tr>'''%(care_index+1,i,str(parms[i]), meaning))
                else:
                    care_file.write('''
    <tr >
        <td bgcolor="#F6F6F6">%s</td>
        <td bgcolor="#F6F6F6">%s</td>
        <td bgcolor="#F6F6F6">%s</td>
        <td bgcolor="#F6F6F6">%s</td>
    </tr>'''%(care_index+1,i,str(parms[i]), meaning))
                care_index += 1
            file.write('''
    <tr >
        <td bgcolor="#62F7EF"> <font color="##FF0000"> <strong>%s</strong></td>
        <td bgcolor="#62F7EF"> <font color="##FF0000"> <strong>%s</strong></td>
        <td bgcolor="#62F7EF"> <font color="##FF0000"> <strong>%s</strong></td>
        <td bgcolor="#62F7EF"> <font color="##FF0000"> <strong>%s</strong></td>
    </tr>'''%(index+1,i,str(parms[i]), meaning))
        elif index % 2 == 0:

            file.write('''
    <tr >
        <td bgcolor="#FDFDFD">%s</td>
        <td bgcolor="#FDFDFD">%s</td>
        <td bgcolor="#FDFDFD">%s</td>
        <td bgcolor="#FDFDFD">%s</td>
    </tr>'''%(index+1,i,str(parms[i]), meaning))
        else:
            file.write('''
    <tr >
        <td bgcolor="#F6F6F6">%s</td>
        <td bgcolor="#F6F6F6">%s</td>
        <td bgcolor="#F6F6F6">%s</td>
        <td bgcolor="#F6F6F6">%s</td>
    </tr>'''%(index+1,i,str(parms[i]), meaning))
        index += 1
    file.write('\n</table>\n')
if len(care_params) > 0:
    care_file.write('\n</table>\n')
    care_file.close()