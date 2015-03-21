#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import sys, argparse


def add_new_pass(args):
    # args validators
    email = str(args.e)
    password = str(args.p)
    print(email)
    print(password, 'add_new_pass')

    # Password.add(email=email, password=password)


def delete_pass(args):
    # args validators
    email = str(args.e)
    password = str(args.p)
    print(email)
    print(password, 'delete_pass')

    # Password.delete(email=email, password=password)


def search_pass(args):
    # args validators
    email = str(args.e)
    password = str(args.p)
    print(email)
    print(password, 'search_pass')

    # Password.search(email=email, password=password)


def parse_args():
    print('start parse args')
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument('-e', help='use to add email or search on it')
    parser.add_argument('-l', help='use to add login or search on it')
    parser.add_argument('-p', help='use to add password')
    parser.add_argument('-d', help='use to add short description or search on it with regexp')
    subparsers = parser.add_subparsers()
    parser_add = subparsers.add_parser('add', help='Add new password to database')
    parser_delete = subparsers.add_parser('delete', help='Delete password from database')
    parser_add.set_defaults(func=add_new_pass)
    parser_delete.set_defaults(func=delete_pass)
    parser.set_defaults(func=search_pass)
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
