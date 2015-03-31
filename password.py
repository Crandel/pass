#!/usr/bin/env python3
import sqlite3 as lite
import argparse

table = 'password'
EMAIL = 'email'
PASSWORD = table
LOGIN = 'login'
SITE = 'site'
DESCRIPTION = 'description'


class Password():

    def __init__(self, *args, **kwargs):

        with lite.connect('pass.db') as con:
            self.email = None
            self.password = None
            self.login = None
            self.description = None
            self.site = None
            self.con = con
            cur = con.cursor()
            query = 'CREATE TABLE IF NOT EXISTS {0} ({1} text, {2} text, {3} text, {4} text, {5} text)'.format(
                table, EMAIL, PASSWORD, LOGIN, SITE, DESCRIPTION
            )
            cur.execute(query)
            con.commit()
            self.cursor = cur

    def __del__(self, *args, **kwargs):

        self.cursor.close()
        self.con.close()

    def search(self, arguments, *args, **kwargs):

        self.email = arguments.e
        self.login = arguments.l
        self.site = arguments.s
        self.description = arguments.d
        self.password = arguments.p
        sql_get = 'SELECT * FROM {}'.format(table)

        params = self.params()
        if params:
            params_sql = ' WHERE'
            i = False
            for p in params:
                if i:
                    params_sql += ' OR'
                params_sql += ' {0}=:{1}'.format(p, p)
                i = True
            sql_get += params_sql
        sql_get += ';'
        cur = self.cursor
        print(sql_get, params)
        results = False
        try:
            cur.execute(sql_get, params)
            results = cur.fetchall()
        except lite.Error as e:
            print(e, 'err')
        for r in results:
            print(r)
        print('search pass')
        return results

    def add(self, arguments, *args, **kwargs):

        if not self.search(arguments):

            if not self.password:
                return 'Password is required'
            params = self.params()

            sql_add = 'INSERT INTO ' + table
            if params:
                name = ''
                values = ''
                i = False
                for p in params:
                    if i:
                        name += ', '
                        values += ', '
                    name += p
                    values += ':' + p
                    i = True
                sql_add = sql_add + '(' + name + ') VALUES (' + values + ')'
            sql_add += ';'
            print(sql_add, 'add')
            cur = self.cursor
            try:
                cur.execute(sql_add, params)
                self.con.commit()
            except lite.Error as e:
                print(e, 'error')
            print('add pass')

    def params(self):
        params = {}

        if self.email:
            params[EMAIL] = self.email
        if self.password:
            params[PASSWORD] = self.password
        if self.login:
            params[LOGIN] = self.login
        if self.site:
            params[SITE] = self.site
        if self.description:
            params[DESCRIPTION] = self.description
        print(params, 'def params')
        return params

    def delete(self, arguments, *args, **kwargs):
        rows = self.search(arguments)

        if rows:
            params = self.params()

            if params:
                cur = self.cursor
                if EMAIL in params:
                    i = [0, EMAIL]
                elif LOGIN in params:
                    i = [2, LOGIN]
                elif SITE in params:
                    i = [3, SITE]
                elif DESCRIPTION in params:
                    i = [4, DESCRIPTION]
                print('del start')
                for r in rows:
                    par = {i[1]: r[i[0]]}
                    print(par)
                    sql = 'DELETE FROM {0} WHERE {1}=:{1}'.format(table, i[1])
                    print(sql)
                    try:
                        cur.execute(sql, par)
                    except lite.Error as e:
                        print(e)
                self.con.commit()
        print('delete pass')


def parse_args():
    password = Password()
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument('-e', help='use to add email or search on it', default=None)
    parser.add_argument('-l', help='use to add login or search on it', default=None)
    parser.add_argument('-s', help='use to add site or search on it', default=None)
    parser.add_argument('-p', help='use to add password', default=None)
    parser.add_argument('-d', help='use to add short description or search on it with regexp', default=None)
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
