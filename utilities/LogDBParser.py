#!/usr/bin/python3
# -*- coding:utf-8 -*-

import sqlite3

# SQLite 保留字（统一大写）。这些词直接拼进 SELECT 语句作字段名时会报语法错误，
# getData()/getDataASC() 会对命中保留字的字段名自动加方括号转义，
# 例如 PARM 表的 Default、AUXF 表的 index。
SQLITE_KEYWORDS = frozenset("""
    ABORT ACTION ADD AFTER ALL ALTER ALWAYS ANALYZE AND AS ASC ATTACH AUTOINCREMENT
    BEFORE BEGIN BETWEEN BY
    CASCADE CASE CAST CHECK COLLATE COLUMN COMMIT CONFLICT CONSTRAINT CREATE CROSS
    CURRENT CURRENT_DATE CURRENT_TIME CURRENT_TIMESTAMP
    DATABASE DEFAULT DEFERRABLE DEFERRED DELETE DESC DETACH DISTINCT DO DROP
    EACH ELSE END ESCAPE EXCEPT EXCLUDE EXCLUSIVE EXISTS EXPLAIN
    FAIL FILTER FIRST FOLLOWING FOR FOREIGN FROM FULL
    GLOB GROUP GROUPS
    HAVING
    IF IGNORE IMMEDIATE IN INDEX INDEXED INITIALLY INNER INSERT INSTEAD INTO IS ISNULL
    JOIN KEY
    LAST LEFT LIKE LIMIT
    MATCH MATERIALIZED
    NATURAL NO NOT NOTHING NOTNULL NULL NULLS
    OF OFFSET ON OR ORDER OTHERS OUTER OVER
    PARTITION PLAN PRAGMA PRECEDING PRIMARY
    QUERY
    RAISE RANGE RECURSIVE REFERENCES REGEXP REINDEX RELEASE RENAME REPLACE RESTRICT
    RETURNING RIGHT ROLLBACK ROW ROWS
    SAVEPOINT SELECT SET
    TABLE TEMP TEMPORARY THEN TIES TO TRANSACTION TRIGGER
    UNBOUNDED UNION UNIQUE UPDATE USING
    VACUUM VALUES VIEW VIRTUAL
    WHEN WHERE WINDOW WITH WITHOUT
""".split())

class LogDBParser:
    """
    SQLite3 数据库形式的日志文件数据读取
    """
    def __init__(self, db):
        """
        db - 需要读取的 SQLite3 数据库文件
        """
        self.conn = sqlite3.connect(db)

    def check_unit(self, table):
        """
        作用：检查日志文件是否带有“单位”和“倍数”
        形参：table - 要检查的表名，例如“ATT”、“SCHE”等。
        返回：
        1. 有单位和倍数则返回 {id, 单位, 倍数} 组成的词典
        2. 无单位和倍数则返回 None
        """
        res = None
        try:
            SQLITE_CMD = "SELECT id,units,multipliers FROM maintable WHERE name=\""
            SQLITE_CMD += table
            SQLITE_CMD += "\""
            with self.conn:
                cur = self.conn.cursor()
                data = cur.execute(SQLITE_CMD)
                rows = cur.fetchall()
                for row in rows:
                    res = {"id":row[0], "units":row[1], "multipliers":row[2]}
                if len(res["units"]) == 0 and len(res["multipliers"]) == 0:
                    res = None
        except TypeError:
            pass
        return res

    def getData(self, table, *args):
        """
        作用：获取表里指定字段的数据，最多可有 20 个字段。
        输入：
        1. table - 表名
        2. *args - 字段名（不定长，最多 20 个，用英文逗号隔开）
                 字段名与 SQLite 保留字相同（如 Default、Limit、index）时会自动转义
        返回：各个字段的值
        示例：
        res = getData("SCHE","TimeUS","name","taken","max")
        res[0] - TimeUS
        res[1] - name
        res[2] - taken
        res[3] - max
        """
        SQLITE_CMD = "SELECT "
        arg_num = 0

        for n in args:
            arg_num += 1
            if n.upper() in SQLITE_KEYWORDS:
                n = '[' + n + ']'
            SQLITE_CMD += n
            SQLITE_CMD += ","
        SQLITE_CMD = SQLITE_CMD[:-1]
        SQLITE_CMD += " FROM "
        SQLITE_CMD += table

        with self.conn:
            cur = self.conn.cursor()
            data = cur.execute(SQLITE_CMD)

        res = [[],[],[],[],[],
               [],[],[],[],[],
               [],[],[],[],[],
               [],[],[],[],[]]
        for row in data:
            if arg_num > 0:
                res[0].append(row[0])
            if arg_num > 1:
                res[1].append(row[1])
            if arg_num > 2:
                res[2].append(row[2])
            if arg_num > 3:
                res[3].append(row[3])
            if arg_num > 4:
                res[4].append(row[4])
            if arg_num > 5:
                res[5].append(row[5])
            if arg_num > 6:
                res[6].append(row[6])
            if arg_num > 7:
                res[7].append(row[7])
            if arg_num > 8:
                res[8].append(row[8])
            if arg_num > 9:
                res[9].append(row[9])
            if arg_num > 10:
                res[10].append(row[10])
            if arg_num > 11:
                res[11].append(row[11])
            if arg_num > 12:
                res[12].append(row[12])
            if arg_num > 13:
                res[13].append(row[13])
            if arg_num > 14:
                res[14].append(row[14])
            if arg_num > 15:
                res[15].append(row[15])
            if arg_num > 16:
                res[16].append(row[16])
            if arg_num > 17:
                res[17].append(row[17])
            if arg_num > 18:
                res[18].append(row[18])
            if arg_num > 19:
                res[19].append(row[19])
        return res

    def getDataASC(self, table, order, *args):
        """
        作用：获取表里指定字段的数据，最多可有 20 个字段。
        输入：
        1. table - 表名
        2. *args - 字段名（不定长，最多 20 个，用英文逗号隔开）
                 字段名与 SQLite 保留字相同（如 Default、Limit、index）时会自动转义
        返回：各个字段的值
        示例：
        res = getData("SCHE","TimeUS","name","taken","max")
        res[0] - TimeUS
        res[1] - name
        res[2] - taken
        res[3] - max
        """
        SQLITE_CMD = "SELECT "
        arg_num = 0

        for n in args:
            arg_num += 1
            if n.upper() in SQLITE_KEYWORDS:
                n = '[' + n + ']'
            SQLITE_CMD += n
            SQLITE_CMD += ","
        SQLITE_CMD = SQLITE_CMD[:-1]
        SQLITE_CMD += " FROM "
        SQLITE_CMD += table
        SQLITE_CMD += " ORDER BY "
        if order.upper() in SQLITE_KEYWORDS:
            order = '[' + order + ']'
        SQLITE_CMD += order

        with self.conn:
            cur = self.conn.cursor()
            data = cur.execute(SQLITE_CMD)

        res = [[],[],[],[],[],
               [],[],[],[],[],
               [],[],[],[],[],
               [],[],[],[],[]]
        for row in data:
            if arg_num > 0:
                res[0].append(row[0])
            if arg_num > 1:
                res[1].append(row[1])
            if arg_num > 2:
                res[2].append(row[2])
            if arg_num > 3:
                res[3].append(row[3])
            if arg_num > 4:
                res[4].append(row[4])
            if arg_num > 5:
                res[5].append(row[5])
            if arg_num > 6:
                res[6].append(row[6])
            if arg_num > 7:
                res[7].append(row[7])
            if arg_num > 8:
                res[8].append(row[8])
            if arg_num > 9:
                res[9].append(row[9])
            if arg_num > 10:
                res[10].append(row[10])
            if arg_num > 11:
                res[11].append(row[11])
            if arg_num > 12:
                res[12].append(row[12])
            if arg_num > 13:
                res[13].append(row[13])
            if arg_num > 14:
                res[14].append(row[14])
            if arg_num > 15:
                res[15].append(row[15])
            if arg_num > 16:
                res[16].append(row[16])
            if arg_num > 17:
                res[17].append(row[17])
            if arg_num > 18:
                res[18].append(row[18])
            if arg_num > 19:
                res[19].append(row[19])
        return res