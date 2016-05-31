#! /usr/bin/python
# encoding: utf-8

import time
import sqlite3 as sq3
import os


def count_reset():
    conn = sq3.connect(os.path.join(os.path.dirname(__file__), 'toilet.db'))
    cur = conn.cursor()
    cur.execute('update toilet set daily=0;')
    conn.commit()
    conn.close()


count_reset()
