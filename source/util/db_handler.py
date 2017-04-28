# -*- coding: utf-8 -*-
from __future__ import division
import os, sys
import sqlite3
import datetime


class DBHandler():
    def __init__(self):
        self.conn = sqlite3.connect('build_manager.db', check_same_thread=False);
        self.createTable()

    # cursor.execute("pragma journal_mode = MEMORY;")
    # cursor.execute("pragma journal_mode = WAL;")

    def createTable(self):
        sql = "Create Table if not exists build(id INTEGER PRIMARY KEY AUTOINCREMENT, build_id varchar(200), job_index varchar(200), result_job varchar(200), start_date datetime default current_timestamp, end_date datetime default current_timestamp)"
        self.conn.execute(sql)
        self.conn.commit();

    def beginTrans(self):
        pass

    def endTrans(self):
        try:
            self.conn.commit()
        except:
            print("Fatal Error in commit !!!")
            self.conn.rollback()

    def openSql(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

            return cursor
        except:
            print("Unexpected error in ExecSQL:", sys.args[0])
            raise

    def execSql(self, sql, db_commit=True):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if db_commit:
                self.conn.commit()
            return cursor

        except Exception as error:
            print(">>> Unexpected error in ExecSQL: ", error)
            print("--- %s ---" % (sql))

    def select_all(self, table_name):
        sql = "select * from %s" % (table_name)
        return self.openSql(sql).fetchall()

    def insert_register_build(self, build_id, result_job, index):
        sql = "insert into build(build_id, job_index, result_job, start_date, end_date) "
        sql += "values("
        sql += "'%s'" % (build_id)
        sql += "," + "'%s'" % (index)
        sql += "," + "'%s'" % (result_job)
        sql += "," + "'not yet'"
        sql += "," + "'not yet'"
        sql += ")"
        print(sql)
        self.execSql(sql)
        return sql

    def update_build_time(self, type, build_id, slave_index): # type = start_date or end_date
        sql = "update build set %s='%s' where build_id = '%s' and job_index = '%s'" % (
            type, datetime.datetime.now(), build_id, slave_index)
        print(sql)
        self.execSql(sql)
        return sql

    def remaining_build_number(self, build_id):
        sql = "select count(*) from build where build_id = '%s' and end_date = 'not yet'" % (build_id)
        print(sql)
        num = self.openSql(sql).fetchall()
        return num[0][0]

    def get_result_job_name(self, build_id):
        sql = "select result_job from build where build_id = '%s'" % (build_id)
        print(sql)
        job_name = self.openSql(sql).fetchall()
        return job_name[0][0]

    def delete_with_buildID(self, build_id):
        sql = "delete from build where build_id='%s'" % (build_id)
        print(sql)
        self.execSql(sql)
