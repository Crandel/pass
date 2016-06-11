#!/usr/bin/env python
import sqlite3
import argparse
import os

from subprocess import Popen, PIPE, call

TABLE = 'password'
EMAIL = 'email'
PASSWORD = TABLE
LOGIN = 'login'
SITE = 'site'
DESCRIPTION = 'description'
DB = '{}/.pass.db'.format(os.environ['HOME'])



class Password(object):

    email = None
    password = None
    login = None
    description = None
    site = None

    def __init__(self, arguments=None):

        if isinstance(arguments, tuple):
            self.email = arguments[1]
            self.password = arguments[2]
            self.login = arguments[3]
            self.site = arguments[4]
            self.description = arguments[5]
        elif isinstance(arguments, argparse.Namespace):
            self.email = arguments.e
            self.password = arguments.p
            self.login = arguments.l
            self.site = arguments.s
            self.description = arguments.d


class Db(object):

    default_params  = {i: '' for i in dir(Password()) if not i.startswith('_')}
    sql_add         = '''INSERT INTO password(password, site, login, description)
                         VALUES (:password, :site, :login, :description);'''
    sql_select      = '''SELECT * FROM password WHERE
                         password=:password OR
                         site=:site OR
                         login=:login OR
                         description=:description;'''
    sql_delete      = 'DELETE FROM password WHERE %(condition)s;'
    sql_update      = '''UPDATE password
                         SET %(values)s
                         WHERE %(condition)s;'''
    create_table    = '''CREATE TABLE IF NOT EXISTS %s
                      (
                       id INTEGER PRIMARY KEY ASC,
                       %s text,
                       %s text,
                       %s text,
                       %s text,
                       %s text)''' % (TABLE,
                                      EMAIL,
                                      PASSWORD,
                                      LOGIN,
                                      SITE,
                                      DESCRIPTION)

    def __init__(self, *args, **kwargs):

        with sqlite3.connect(DB) as con:

            self.con = con
            cur = con.cursor()
            try:
                cur.execute('SELECT * FROM %s' % TABLE)
            except sqlite3.OperationalError:
                cur.execute(self.create_table)
            con.commit()
            self.cursor = cur

    def __del__(self, *args, **kwargs):

        self.cursor.close()
        self.con.close()

    def _get_params(params):
        parameters = self.default_params
        if params:
            parameters.update(params)
        return parameters

    def search(self, *args, **kwargs):
        cur = self.cursor
        results = False
        params = self._get_params(kwargs['params'])
        try:
            cur.execute(self.sql_select, params)
            results = cur.fetchall()
        except sqlite3.Error as e:
            print(e, 'err')

        return results

    def add(self, *args, **kwargs):
        params = self._get_params(kwargs['params'])
        cur = self.cursor

        try:
            cur.execute(self.sql_add, params)
            self.con.commit()
        except sqlite3.Error as e:
            print(e, 'error')
        print('Record was added')

    def delete(self, *args, **kwargs):
        cur = self.cursor
        params = kwargs['params']
        rows = kwargs['rows']

        for r in rows:
            sql, par = self.delete_query(params, r)
            try:
                cur.execute(sql, par)
            except sqlite3.Error as e:
                print(e)
            self.con.commit()
        print('delete pass')

    def delete_query(self, params, r):

        if EMAIL in params:
            i = [1, EMAIL]
        elif LOGIN in params:
            i = [3, LOGIN]
        elif SITE in params:
            i = [4, SITE]
        elif DESCRIPTION in params:
            i = [5, DESCRIPTION]
        par = {i[1]: r[i[0]]}
        sql = 'DELETE FROM {0} WHERE {1}=:{1}'.format(TABLE, i[1])
        return sql, par

    def edit(self, *args, **kwargs):
        pass


class PasswordManager(object):

    def __init__(self, *args, **kwargs):
        self.db = Db()

    def clipboard(self, text):

        xclipExists = call(['which', 'xclip'], stdout=PIPE, stderr=PIPE) == 0

        xselExists = call(['which', 'xsel'], stdout=PIPE, stderr=PIPE) == 0
        if xclipExists:
            p = Popen(['xclip',
                       '-selection',
                       'c',
                       '-i'],
                      stdin=PIPE,
                      close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        elif xselExists:
            p = Popen(['xsel', '-b', '-i'], stdin=PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        else:
            raise Exception('Program requires the xclip or xsel application')

    def search(self, arguments, *args, **kwargs):
        print(arguments)
        try:
            no_input = arguments.no_input
        except AttributeError:
            no_input = False

        params = self.params(Password()(arguments))
        results = self.db.search(params=params)
        print(results)
        if results and not no_input:
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
        elif not results:
            print('Sorry, this record does not exist')

        print('search results')
        return results

    def add(self, arguments, *args, **kwargs):

        params = self.params(Password()(arguments))
        if not params.get('password', False):
            print('Password is required')
            return
        self.db.add(params=params)

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

    def parse_results(self, results):

        res_list = {}
        i = 1
        for res in results:
            res_list[i] = res
            passw = Password()(res)
            print(
                '{0}. email:{1}, login:{2}, site:{3}, description:{4}'.format(
                    i, passw.email, passw.login, passw.site, passw.description
                )
            )
            i += 1
        return res_list

    def delete(self, arguments, *args, **kwargs):

        rows = self.search(arguments)

        if rows:
            params = self.params(Password()(arguments))
            if params:
                self.db.delete(params=params, rows=rows)

    def edit(self, arguments, *args, **kwargs):
        rows = self.search(arguments)

        if rows:
            params = self.params()

            if params:
                i = []
                # cur = self.cursor
                if EMAIL in params:
                    i = [1, EMAIL]
                elif LOGIN in params:
                    i = [3, LOGIN]
                elif SITE in params:
                    i = [4, SITE]
                elif DESCRIPTION in params:
                    i = [5, DESCRIPTION]

                print(i)
        print('edit pass')


def parse_args():
    password = PasswordManager()
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument(
        '-e',
        help='use to add email or search on it',
        default=None)
    parser.add_argument(
        '-l',
        help='use to add login or search on it',
        default=None)
    parser.add_argument(
        '-s',
        help='use to add site or search on it',
        default=None)
    parser.add_argument('-p', help='use to add password', default=None)
    parser.add_argument(
        '-d',
        help='use to add short description or search on it with regexp',
        default=None)
    parser.set_defaults(func=password.search)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser(
        'add',
        help='Add new password to database')
    parser_add.set_defaults(func=password.add)

    parser_edit = subparsers.add_parser('edit', help='Edit record from database')
    parser_edit.set_defaults(func=password.edit)

    parser_delete = subparsers.add_parser(
        'del',
        help='Delete password from database')
    parser_delete.set_defaults(func=password.delete, no_input=True)

    parser_search = subparsers.add_parser(
        'srch',
        help='Search password from database')
    parser_search.set_defaults(func=password.search)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
