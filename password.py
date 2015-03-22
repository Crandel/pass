#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import sys, argparse


class Password():

    def __init__(self, *args, **kwargs):
        with lite.connect('pass.db') as con:
            cur = con.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS password
             (email text, password text, login text, site text, description text)''')
            cur.fetchone()

            self.cursor = cur

    def __del__(self, *args, **kwargs):
        self.cursor.close()

    def search(self, arguments, *args, **kwargs):
        # args validators
        print(arguments, type(arguments), dir(arguments))
        email = str(arguments.e)
        # password = str(arguments.p)
        cur = self.cursor
        print(email, dir(email), type(email))
        print('search pass')

    def add(self, arguments, *args, **kwargs):
        # args validators
        email = str(arguments.e)
        password = str(arguments.p)
        cur = self.cursor
        print(email)
        print('add pass')

    def delete(self, arguments, *args, **kwargs):
        # args validators
        email = str(arguments.e)
        password = str(arguments.p)
        cur = self.cursor
        print(email)
        print('delete pass')


def parse_args():
    print('start parse args')
    password = Password()
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument('-e', help='use to add email or search on it')
    parser.add_argument('-l', help='use to add login or search on it')
    parser.add_argument('-s', help='use to add site or search on it')
    parser.add_argument('-p', help='use to add password')
    parser.add_argument('-d', help='use to add short description or search on it with regexp')
    parser.set_defaults(func=password.search)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('add', help='Add new password to database')
    parser_add.set_defaults(func=password.add)
    
    parser_delete = subparsers.add_parser('delete', help='Delete password from database')
    parser_delete.set_defaults(func=password.delete)
    
    print('end parse')
    return parser.parse_args()


def main():
    print('start')
    args = parse_args()
    print('-----')
    args.func(args)
    print('stop')


if __name__ == "__main__":
    main()
