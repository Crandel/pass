#!/usr/bin/env python
import sqlite3 as lite
import argparse
from subprocess import Popen, PIPE, call

TABLE = 'password'
EMAIL = 'email'
PASSWORD = TABLE
LOGIN = 'login'
SITE = 'site'
DESCRIPTION = 'description'


class Password():

    email = None
    password = None
    login = None
    description = None
    site = None

    def create(self, list):
        self.email = list[0]
        self.password = list[1]
        self.login = list[2]
        self.site = list[3]
        self.description = list[4]


class PasswordManager(Password):

    def __init__(self, *args, **kwargs):

        with lite.connect('pass.db') as con:

            self.con = con
            cur = con.cursor()
            query = 'CREATE TABLE IF NOT EXISTS {0} ({1} text, {2} text, {3} text, {4} text, {5} text)'.format(
                TABLE, EMAIL, PASSWORD, LOGIN, SITE, DESCRIPTION
            )
            cur.execute(query)
            con.commit()
            self.cursor = cur

    def __del__(self, *args, **kwargs):

        self.cursor.close()
        self.con.close()

    def clipboard(self, text):

        xclipExists = call(['which', 'xclip'], stdout=PIPE, stderr=PIPE) == 0

        xselExists = call(['which', 'xsel'], stdout=PIPE, stderr=PIPE) == 0
        print(xclipExists, xselExists)
        if xclipExists:
            p = Popen(['xclip', '-selection', 'c', '-i'], stdin=PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        elif xselExists:
            p = Popen(['xsel', '-b', '-i'], stdin=PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        else:
            raise Exception('Program requires the xclip or xsel application')

    def search(self, arguments, *args, **kwargs):

        self.email = arguments.e
        self.login = arguments.l
        self.site = arguments.s
        self.description = arguments.d
        try:
            input_type = arguments.input_type
        except AttributeError:
            input_type = False
        self.password = arguments.p
        sql_get = 'SELECT * FROM {}'.format(TABLE)

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
        results = False
        try:
            cur.execute(sql_get, params)
            results = cur.fetchall()
        except lite.Error as e:
            print(e, 'err')
        if input_type:
            res_list = {}
            if len(results) > 1:
                print(results, type(results))
                i = 0
                for res in results:
                    res_list[i] = res
                    passw = Password()
                    passw.create(res)
                    print('{0}. email:{1}, login:{2}, site:{3}, description:{4}'.format(
                            i, passw.email, passw.login, passw.site, passw.description
                        )
                    )
                    i += 1
            elif len(results) == 1:
                res_list = {0: results[0]}
                print('1. email={0}, login={1}, site={2}, description={3}'.format(
                    results[0][0], results[0][2], results[0][3], results[0][4]
                    )
                )

            queny = input('Please enter a number of record ')
            try:
                queny = int(queny)
            except ValueError:
                queny = input('Please enter the number of record ')
                queny = int(queny)
            if queny in res_list.keys():
                # password to clipboard
                self.clipboard(res_list[queny][1])
            else:
                print('Sorry, this record does not exist')
        print('search pass')
        return results

    def add(self, arguments, *args, **kwargs):

        if not self.search(arguments):

            if not self.password:
                return 'Password is required'
            params = self.params()

            sql_add = 'INSERT INTO ' + TABLE
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
                for r in rows:
                    par = {i[1]: r[i[0]]}
                    sql = 'DELETE FROM {0} WHERE {1}=:{1}'.format(TABLE, i[1])
                    try:
                        cur.execute(sql, par)
                    except lite.Error as e:
                        print(e)
                self.con.commit()
        print('delete pass')

    def edit(self, arguments, *args, **kwargs):
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
        print('edit pass')


def parse_args():
    password = PasswordManager()
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument('-e', help='use to add email or search on it', default=None)
    parser.add_argument('-l', help='use to add login or search on it', default=None)
    parser.add_argument('-s', help='use to add site or search on it', default=None)
    parser.add_argument('-p', help='use to add password', default=None)
    parser.add_argument('-d', help='use to add short description or search on it with regexp', default=None)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('a', help='Add new password to database')
    parser_add.set_defaults(func=password.add)

    parser_add = subparsers.add_parser('e', help='Edit record from database')
    parser_add.set_defaults(func=password.edit)

    parser_delete = subparsers.add_parser('d', help='Delete password from database')
    parser_delete.set_defaults(func=password.delete)

    parser_search = subparsers.add_parser('s', help='Search password from database')
    parser_search.set_defaults(func=password.search, input_type=True)

    return parser.parse_args()


def main():
    print('start')
    args = parse_args()
    args.func(args)
    print('stop')


if __name__ == "__main__":
    main()
