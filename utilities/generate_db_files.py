suffix     = ".ehbin"
LogFiles   = []

def get_str_index(str1,str2):
    res = None
    try:
        res = str1.index(str2)
    except:
        res = None
    return res

def _checkName(in1):
    import re
    res = None
    res = re.match("^[A-Z0-9]{1,4}$",in1)
    return res

def _checkFormat(in1):
    import re
    res = None
    res = re.match("^[A-Za-z]{1,16}$",in1)
    return res

def _checkLabels(in1):
    import re
    res = None
    res = re.match("^[A-Za-z0-9, _]{1,64}$",in1)
    return res

def _checkMessage(name_in, format_in, labels_in):
    res = False
    res1 = _checkName(name_in) is not None
    res2 = _checkFormat(format_in) is not None
    res3 = _checkLabels(labels_in) is not None
    if not res1:
        print("Name check failed: %s"%(name_in))
    if not res2:
        print("%s Format check failed: %s"%(name_in, format_in))
    if not res3:
        print("%s Labels check failed: %s"%(name_in, labels_in))
    res = res1 and res2 and res3
    return res

def _decodeData(id_dict, id1, stream, size1):
    from struct import unpack
    import traceback
    fmt = id_dict[id1][1]
    res = ""
    fmt_list = list(fmt)
    print_flag_01 = False
    for c in fmt_list:
        if stream.tell() == size1:
            break
        if c == 'a':
            r = stream.read(64)
            v = 0
            try:
                v = unpack('<32h',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int16_t[32]: %s"%(res))
        elif c == 'b':
            r = stream.read(1)
            v = 0
            try:
                v = unpack('<b',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int8_t")
        elif c == 'B':
            r = stream.read(1)
            v = 0
            try:
                v = unpack('<B',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint8_t: %s"%(res))
        elif c == 'h':
            r = stream.read(2)
            v = 0
            try:
                v = unpack('<h',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int16_t")
        elif c == 'H':
            r = stream.read(2)
            v = 0
            try:
                v = unpack('<H',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint16_t")
        elif c == 'i':
            r = stream.read(4)
            v = 0
            try:
                v = unpack('<i',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int32_t")
        elif c == 'I':
            r = stream.read(4)
            v = 0
            try:
                v = unpack('<I',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint32_t")
        elif c == 'f':
            r = stream.read(4)
            v = 0
            try:
                v = unpack('<f',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            import math
            if math.isnan(v):
                #print("table:%s,f:%f"%(id_dict[id1][0],v),r)
                #print_flag_01 = True
                v = 0
            res = "%s%f,"%(res,v)
            #print("float")
        elif c == 'd':
            r = stream.read(8)
            v = 0
            try:
                v = unpack('<d',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%f,"%(res,v)
            #print("double")
        elif c == 'n':
            r = stream.read(4)
            v = 0
            try:
                v = r.decode('utf-8','strict').strip(b'\x00'.decode())
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s'%s',"%(res,v)
            #print("char[4]: %s"%(res))
        elif c == 'N':
            r = stream.read(16)
            v = 0
            try:
                v = r.decode('utf-8','strict').strip(b'\x00'.decode())
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s'%s',"%(res,v)
            #print("char[16]: %s"%(res))
        elif c == 'Z':
            r = stream.read(64)
            v = 0
            try:
                v = r.decode('utf-8','strict').strip(b'\x00'.decode())
            except Exception as e:
                #print(r)
                #print_flag_01 = True
                if id_dict[id1][0] != 'FILE':
                    traceback.print_exc()
            res = "%s'%s',"%(res,v)
            #print("char[64]")
        elif c == 'c':
            r = stream.read(2)
            v = 0
            try:
                v = unpack('<h',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int16_t * 100")
        elif c == 'C':
            r = stream.read(2)
            v = 0
            try:
                v = unpack('<H',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint16_t * 100")
        elif c == 'e':
            r = stream.read(4)
            v = 0
            try:
                v = unpack('<i',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int32_t * 100")
        elif c == 'E':
            r = stream.read(4)
            v = 0
            try:
                v = unpack('<I',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint32_t * 100")
        elif c == 'L':
            r = stream.read(4)
            v = 0
            try:
                v = unpack('<i',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int32_t latitude/longitude")
        elif c == 'M':
            r = stream.read(1)
            v = 0
            try:
                v = unpack('<b',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint8_t flight mode")
        elif c == 'q':
            r = stream.read(8)
            v = 0
            try:
                v = unpack('<q',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("int64_t")
        elif c == 'Q':
            r = stream.read(8)
            v = 0
            try:
                v = unpack('<Q',r)[0]
            except Exception as e:
                print(r)
                traceback.print_exc()
            res = "%s%d,"%(res,v)
            #print("uint64_t")
    res = res[0:len(res)-1]
    if print_flag_01:
        print(res)
    return res

import sqlite3
class LVDB:
    def __init__(self,db):
        self.Number = 0
        if os.path.exists(db):
            os.remove(db)
        self.maintable_ids  = {}
        self.conn = sqlite3.connect(db)
        sql = "CREATE TABLE maintable(id INT8 PRIMARY KEY, len INT8, name VARCHAR, format VARCHAR, labels VARCHAR, units VARCHAR, multipliers VARCHAR)"
        cursor = self.conn.cursor()
        cursor.execute(sql)

    def close(self):
        self.conn.close()

    def checkMainTable(self,id1):
        res = False
        if id1 in self.maintable_ids.keys():
            res = True
        return res

    def get_id_dict(self):
        return self.maintable_ids

    def addToMainTable(self,type1,len1,name1,format1,labels1,uints1,multipliers1):
        if type1 not in self.maintable_ids.keys():
            self.maintable_ids[type1] = [name1, format1]

        sql = "INSERT INTO maintable VALUES(%d,%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"%(type1,len1,name1,format1,labels1,uints1,multipliers1)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()

        table_field = self.createTableField(format1,labels1)
        table_field = "%s,%s"%("LineNo INTEGER PRIMARY KEY", table_field)
        sql = "CREATE TABLE IF NOT EXISTS %s(%s)"%(name1, table_field)

        import traceback
        try:
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            traceback.print_exc()
            print(name1, sql)

    def addToSubTable(self,name1, values):
        self.Number += 1
        v = "%s,%s"%(str(self.Number),values);
        sql = "INSERT INTO %s VALUES(%s)"%(name1,v)
        import traceback
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except Exception as e:
            traceback.print_exc()
            print(sql)

    def commit(self):
        self.conn.commit()

    def createTableField(self,formats,fields):
        res = ""
        fmt_list = list(formats)
        for i in range(len(fmt_list)):
            if fmt_list[i] == 'a': # int16_t[32]
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'b': # int8_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'B': # uint8_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'h': # int16_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'H': # uint16_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'i': # int32_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'I': # uint32_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'f': # float
                res = "%s %s %s,"%(res, fields.split(',')[i], "DOUBLE")
            elif fmt_list[i] == 'd': # double
                res = "%s %s %s,"%(res, fields.split(',')[i], "DOUBLE")
            elif fmt_list[i] == 'n': # char[4]
                res = "%s %s %s,"%(res, fields.split(',')[i], "VARCHAR")
            elif fmt_list[i] == 'N': # char[16]
                res = "%s %s %s,"%(res, fields.split(',')[i], "VARCHAR")
            elif fmt_list[i] == 'Z': # char[64]
                res = "%s %s %s,"%(res, fields.split(',')[i], "VARCHAR")
            elif fmt_list[i] == 'c': # int16_t * 100
                res = "%s %s %s,"%(res, fields.split(',')[i], "DOUBLE")
            elif fmt_list[i] == 'C': # uint16_t * 100
                res = "%s %s %s,"%(res, fields.split(',')[i], "DOUBLE")
            elif fmt_list[i] == 'e': # int32_t * 100
                res = "%s %s %s,"%(res, fields.split(',')[i], "DOUBLE")
            elif fmt_list[i] == 'E': # uint32_t * 100
                res = "%s %s %s,"%(res, fields.split(',')[i], "DOUBLE")
            elif fmt_list[i] == 'L': # int32_t latitude/longitude
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'M': # uint8_t flight mode
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'q': # int64_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
            elif fmt_list[i] == 'Q': # uint64_t
                res = "%s %s %s,"%(res, fields.split(',')[i], "INTEGER")
        res = res[0:len(res)-1]
        return res

class LFMT:
    def __init__(self):
        self.id     = []
        self.name   = []
        self.format = []
        self.valid  = {}

FMT = LFMT()

# 获取当前目录下的 Log 文件名
import os
filePath = os.getcwd()
for i,j,k in os.walk(filePath):
    for filename in k:
        if filename.lower().endswith(suffix) and filename not in LogFiles:
            LogFiles.append(filename)

cnt   = 0
total = len(LogFiles)
for logfile in LogFiles:
    print("\n\n\n%s in processing...\n\n\n"%(logfile))
    ptr_pos    = 0
    head_check = []
    log_size = os.path.getsize(logfile)

    # sqlite3: 创建同名数据库文件
    # db = LVDB("db/"+logfile.split(".")[0]+".db")
    db = LVDB("".join(logfile.split(".")[0:-1])+".db")

    with open(logfile,"rb") as log:
        while log.tell() < log_size:
            currentByte = log.read(1)

            if ptr_pos <= 3:
                ptr_pos += 1

            if ptr_pos > 3:
                head_check[0] = head_check[1]
                head_check[1] = head_check[2]
                head_check[2] = currentByte
            else:
                if ptr_pos == 1:
                    head_check.append(currentByte)
                    continue
                elif ptr_pos == 2:
                    head_check.append(currentByte)
                    continue
                elif ptr_pos == 3:
                    head_check.append(currentByte)

            if head_check[0] == b'\xa3' and head_check[1] == b'\x95':
                if head_check[2] == b'\x80':
                    from struct import unpack
                    type1        = unpack('>B',log.read(1))[0]
                    type_flag    = str(type1)
                    len1         = unpack('>B',log.read(1))[0]
                    length       = str(len1)
                    table_name   = log.read(4).decode('utf-8','strict').strip(b'\x00'.decode())
                    formats      = log.read(16).decode('utf-8','strict').strip(b'\x00'.decode())
                    labels       = log.read(64).decode('utf-8','strict').strip(b'\x00'.decode())
                    uints1       = ""
                    multipliers1 = ""

                    if _checkMessage(table_name, formats, labels):
                        index_of_Primary = get_str_index(labels, 'Primary')
                        if index_of_Primary is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_Primary+7, '`')
                            str_list.insert(index_of_Primary, '`')
                            labels = "".join(str_list)

                        index_of_Default = get_str_index(labels, 'Default')
                        if index_of_Default is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_Default+7, '`')
                            str_list.insert(index_of_Default, '`')
                            labels = "".join(str_list)

                        index_of_Limit = get_str_index(labels, 'Limit')
                        if index_of_Limit is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_Limit+5, '`')
                            str_list.insert(index_of_Limit, '`')
                            labels = "".join(str_list)

                        index_of_IS = get_str_index(labels, 'IS')
                        if index_of_IS is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_IS+2, '`')
                            str_list.insert(index_of_IS, '`')
                            labels = "".join(str_list)

                        index_of_As = get_str_index(labels, 'As')
                        if index_of_As is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_As+2, '`')
                            str_list.insert(index_of_As, '`')
                            labels = "".join(str_list)

                        index_of_AS = get_str_index(labels, 'AS')
                        if index_of_AS is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_AS+2, '`')
                            str_list.insert(index_of_AS, '`')
                            labels = "".join(str_list)

                        index_of_index = get_str_index(labels, 'index')
                        if index_of_index is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_index+5, '`')
                            str_list.insert(index_of_index, '`')
                            labels = "".join(str_list)

                        index_of_m0v = get_str_index(labels, 'm0v')
                        if index_of_m0v is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_m0v+3, '0')
                            labels = "".join(str_list)

                        index_of_m0c = get_str_index(labels, 'm0c')
                        if index_of_m0c is not None:
                            str_list = list(labels)
                            str_list.insert(index_of_m0c+3, '0')
                            labels = "".join(str_list)

                        if table_name == "FROM":
                            table_name = "`FROM`"
                        if table_name == "TO":
                            table_name = "`TO`"

                        db.addToMainTable(type1, len1, table_name, formats, labels, uints1, multipliers1)
                else:
                    log_id = unpack('>B',head_check[2])[0]
                    if db.checkMainTable(log_id):
                        v = _decodeData(db.get_id_dict(), log_id, log, log_size)
                        table_name1 = db.get_id_dict()[log_id][0]
                        if table_name1 != 'FILE':
                            db.addToSubTable(table_name1, v)
        db.commit()
        cnt += 1
        print("\n\n\n%s finished (%d/%d)\n\n\n"%(logfile,cnt,total))