#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import sys, argparse

def create_new_pass(args):
    # args validators
    email = str(args.e)
    password = str(args.p)
    print(email)
    print(password)

    # Password.add(email=email, password=password)

def parse_args():
    parser = argparse.ArgumentParser(description='Password database utility')
    subparsers = parser.add_subparsers()
    parser_create = subparsers.add_parser('create', help='Create a new password to database')
    parser_create.add_argument('e', help='use to add email or search on it')
    parser_create.add_argument('l', help='use to add login or search on it')
    parser_create.add_argument('p', help='use to add password')
    parser_create.add_argument('d', help='use to add short description or search on it with regexp')
    parser_create.set_defaults(func=create_new_pass)

    return parser.parse_args()

def main():
    args = parse_args()
    args.func(args)
