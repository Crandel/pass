#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

with lite.connect('pass.db') as con:
    cur = con.cursor()    
    try:
        con.execute('SELECT * FROM pass')
    except lite.Error as e:
        # con.execute('''CREATE TABLE pass (email, name, password, description)''')
        print(e)
    
    
    #con.close()
