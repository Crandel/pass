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

    def create_from_query(self, list):
        self.email = list[1]
        self.password = list[2]
        self.login = list[3]
        self.site = list[4]
        self.description = list[5]

    def create_from_args(self, arguments):
        self.email = arguments.e
        self.password = arguments.p
        self.login = arguments.l
        self.site = arguments.s
        self.description = arguments.d


class PasswordManager():

    def __init__(self, *args, **kwargs):

        with lite.connect('pass.db') as con:

            self.con = con
            cur = con.cursor()
            query = 'CREATE TABLE IF NOT EXISTS {0} (id INTEGER PRIMARY KEY ASC, {1} text, {2} text, {3} text, {4} text, {5} text)'.format(
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
        if xclipExists:
            p = Popen(['xclip', '-selection', 'c', '-i'], stdin=PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        elif xselExists:
            p = Popen(['xsel', '-b', '-i'], stdin=PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        else:
            raise Exception('Program requires the xclip or xsel application')

    def parse_results(self, results):

        res_list = {}
        i = 1
        for res in results:
            res_list[i] = res
            passw = Password()
            passw.create_from_query(res)
            print('{0}. email:{1}, login:{2}, site:{3}, description:{4}'.format(
                    i, passw.email, passw.login, passw.site, passw.description
                )
            )
            i += 1
        return res_list

    def search(self, arguments, *args, **kwargs):

        password = Password()
        password.create_from_args(arguments)

        try:
            input_type = arguments.input_type
        except AttributeError:
            input_type = False
        sql_get = 'SELECT * FROM {}'.format(TABLE)

        params = self.params(password)
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
        if results and input_type:
            res_list = self.parse_results(results)
            queny = input('Please enter a number of record ')
            try:
                queny = int(queny)
            except ValueError:
                queny = input('Please enter the number of record ')
                queny = int(queny)
            if queny in res_list.keys():
                # password to clipboard
                self.clipboard(res_list[queny][2])
            else:
                print('Sorry, this record does not exist')
        else:
            print('Sorry, this record does not exist')
        print('search results')
        return results

    def add(self, arguments, *args, **kwargs):
        password = Password()
        password.create_from_args(arguments)
        if not password.password:
            return 'Password is required'
        params = self.params(password)

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
        print('Record was added')

    def params(self, password):
        params = {}

        if password.email:
            params[EMAIL] = password.email
        if password.password:
            params[PASSWORD] = password.password
        if password.login:
            params[LOGIN] = password.login
        if password.site:
            params[SITE] = password.site
        if password.description:
            params[DESCRIPTION] = password.description
        return params

    def delete(self, arguments, *args, **kwargs):
        password = Password()
        password.create_from_args(arguments)
        rows = self.search(arguments)

        if rows:
            params = self.params(password)

            if params:
                cur = self.cursor
                if EMAIL in params:
                    i = [1, EMAIL]
                elif LOGIN in params:
                    i = [3, LOGIN]
                elif SITE in params:
                    i = [4, SITE]
                elif DESCRIPTION in params:
                    i = [5, DESCRIPTION]
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
                    i = [1, EMAIL]
                elif LOGIN in params:
                    i = [3, LOGIN]
                elif SITE in params:
                    i = [4, SITE]
                elif DESCRIPTION in params:
                    i = [5, DESCRIPTION]
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
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
