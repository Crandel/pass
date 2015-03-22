#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import sys, argparse


class Password():

    def connect():
        with lite.connect('pass.db') as con:
            return con

    def search(args):
        # args validators
        email = str(args.e)
        password = str(args.p)
        print(self.connect)
        print(email)
        print('search pass')

    def add(args):
        # args validators
        email = str(args.e)
        password = str(args.p)
        print(email)
        print('add pass')

    def delete(args):
        # args validators
        email = str(args.e)
        password = str(args.p)
        print(email)
        print('delete pass')


def parse_args():
    print('start parse args')
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument('-e', help='use to add email or search on it')
    parser.add_argument('-l', help='use to add login or search on it')
    parser.add_argument('-p', help='use to add password')
    parser.add_argument('-d', help='use to add short description or search on it with regexp')
    parser.set_defaults(func=Password.search)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('add', help='Add new password to database')
    parser_add.set_defaults(func=Password.add)
    
    parser_delete = subparsers.add_parser('delete', help='Delete password from database')
    parser_delete.set_defaults(func=Password.delete)
    
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
