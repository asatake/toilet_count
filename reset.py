#! /usr/bin/python
# encoding: utf-8

import time
import sqlite3 as sq3


def count_reset():
    conn = sq3.connect(os.path.join(os.path.dirname(__file__), 'toilet.db'))
    cur = conn.cursor()
    cur.execute('update toilet set daily=0;')
    conn.commit()
    conn.close()


while True:
    now = time.gmtime()
    if (now.tm_hour is 15) and (now.tm_min is 0) and (now.tm_sec is 0):
        count_reset()
    time.sleep(1.0)
