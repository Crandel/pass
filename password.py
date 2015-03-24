#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import sys, argparse

table = 'password'


class Password():

    def __init__(self, *args, **kwargs):
        with lite.connect('pass.db') as con:
            self.con = con
            cur = con.cursor()
            query = 'CREATE TABLE IF NOT EXISTS ' + table + '(email text, password text, login text, site text, description text)'
            cur.execute(query)
            con.commit()
            self.cursor = cur

    def __del__(self, *args, **kwargs):
        self.cursor.close()
        self.con.close()

    def search(self, arguments, *args, **kwargs):
        # args validators
        email = str(arguments.e)
        password = str(arguments.p)
        params = 'email="{}"'.format(email)
        cur = self.cursor
        sql = 'SELECT * FROM ' + table + ' WHERE {};'.format(params)
        print(sql)
        cur.execute(sql)
        self.con.commit()
        print('search pass')

    def add(self, arguments, *args, **kwargs):
        # args validators
        email = str(arguments.e)
        password = str(arguments.p)
        login = str(arguments.l)
        site = str(arguments.s)
        description = str(arguments.d)
        cur = self.cursor
        sql = 'INSERT INTO ' + table + ' VALUES ("{0}", "{1}", "{2}", "{3}", "{4}");'.format(email, 
                                                                              password,
                                                                              login,
                                                                              site,
                                                                              description)
        print(sql)
        cur.execute(sql)
        self.con.commit()
        print(dir(cur))
        print('add pass', sql)

    def delete(self, arguments, *args, **kwargs):
        # args validators
        email = str(arguments.e)
        password = str(arguments.p)
        cur = self.cursor
        print(email)
        print('delete pass')


def parse_args():
    password = Password()
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument('-e', help='use to add email or search on it', default='')
    parser.add_argument('-l', help='use to add login or search on it', default='')
    parser.add_argument('-s', help='use to add site or search on it', default='')
    parser.add_argument('-p', help='use to add password', default='')
    parser.add_argument('-d', help='use to add short description or search on it with regexp', default='')
    parser.set_defaults(func=password.search)

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required=False

    parser_add = subparsers.add_parser('a', help='Add new password to database')
    parser_add.set_defaults(func=password.add)
    
    parser_delete = subparsers.add_parser('d', help='Delete password from database')
    parser_delete.set_defaults(func=password.delete)

    parser_search = subparsers.add_parser('s', help='Search password from database')
    parser_search.set_defaults(func=password.search)

    return parser.parse_args()


def main():
    print('start')
    args = parse_args()
    print('-----')
    args.func(args)
    print('stop')


if __name__ == "__main__":
    main()
