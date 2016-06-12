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
    sql_add         = '''INSERT INTO password (password, site, login, description)
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

    def _get_params(self, params):
        parameters = self.default_params
        if params:
            parameters.update(params)
            if params.get('password'):
                params['password'] = self.get_hash(params['password'])
        return parameters

    def get_hash(self, password):
        try:
            hash = __import__('hash_func')
            return hash.hash_password(password)
        except ImportError:
            return password

    def search(self, *args, **kwargs):
        cur = self.cursor
        results = []
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
            print('Record was added')
        except sqlite3.Error as e:
            print(e, 'error')

    def delete(self, id, **kwargs):
        cur = self.cursor
        id = int(id)
        condition = 'id=%d' % id
        sql = self.sql_delete % {'condition': condition}
        try:
            cur.execute(sql)
            self.con.commit()
            print('Record №%d was deleted' % id)
        except sqlite3.Error as e:
            print(e)

    def edit(self, id, **kwargs):
        cur = self.cursor
        id = int(id)
        condition = 'id=%d' % id
        values_dict = {}
        values_dict['password'] = input('Please enter a new password\n')
        values_dict['email'] = input('Please enter a new email\n')
        values_dict['login'] = input('Please enter a new login\n')
        values_dict['site'] = input('Please enter a new site\n')
        values_dict['description'] = input('Please enter a new description\n')
        values = ''
        m = False
        for key, value in values_dict.items():
            if value:
                if key == 'password':
                    value = self.get_hash(value)
                if m:
                    values += ', '
                values += "%(key)s = '%(value)s'" % {'key': key, 'value': value}
                m = True
        sql = self.sql_update % {'condition': condition, 'values': values}
        try:
            cur.execute(sql)
            self.con.commit()
            print('Record №%d was updated' % id)
        except sqlite3.Error as e:
            print(e)


class PasswordManager(object):

    def __init__(self, *args, **kwargs):
        self.db = Db()

    def clipboard(self, text):

        xclip_exists = call(['which', 'xclip'], stdout=PIPE, stderr=PIPE) == 0

        xsel_exists = call(['which', 'xsel'], stdout=PIPE, stderr=PIPE) == 0
        if xclip_exists:
            p = Popen(['xclip',
                       '-selection',
                       'c',
                       '-i'],
                      stdin=PIPE,
                      close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        elif xsel_exists:
            p = Popen(['xsel', '-b', '-i'], stdin=PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
        else:
            raise Exception('Program requires the xclip or xsel application')

    def user_input(self, results, **kwargs):
        res_list = self.parse_results(results)
        queny = input('Please enter a number of record ')
        try:
            queny = int(queny)
        except ValueError:
            queny = input('Please enter the number of record ')
            queny = int(queny)
        if queny in res_list.keys():
            if kwargs.get('copy'):
                # password to clipboard
                self.clipboard(res_list[queny][2])
                print('Password was copied to clipboard')
            if kwargs.get('edit'):
                return queny
        else:
            print('Sorry, this record does not exist')

    def search(self, arguments, *args, **kwargs):
        try:
            no_input = arguments.no_input
        except AttributeError:
            no_input = False

        params = self.params(Password(arguments))
        results = self.db.search(params=params)
        if results and not no_input:
            self.user_input(results=results, copy=True)
        elif not results:
            print('Sorry, this record does not exist')

        return results

    def add(self, arguments, *args, **kwargs):

        params = self.params(Password(arguments))
        if not params.get('password', False):
            print('Password is required')
            return
        self.db.add(params=params)

    def params(self, password):
        ret = {
            key: password.__dict__[key] for key in password.__dict__
            if not key.startswith('_') and password.__dict__[key]}
        return ret

    def parse_results(self, results):

        res_list = {}
        for res in results:
            i = res[0]
            res_list[i] = res
            passw = Password(res)
            print(
                '{0}. email:{1}, login:{2}, site:{3}, description:{4}'.format(
                    i, passw.email, passw.login, passw.site, passw.description
                )
            )
        return res_list

    def delete(self, arguments, *args, **kwargs):

        rows = self.search(arguments)
        if rows:
            id = self.user_input(results=rows, edit=True)
            self.db.delete(id)

    def edit(self, arguments, *args, **kwargs):
        rows = self.search(arguments)

        if rows:
            id = self.user_input(results=rows, edit=True)
            self.db.edit(id)


def parse_args():
    password = PasswordManager()
    parser = argparse.ArgumentParser(description='Password database utility')
    parser.add_argument(
        '-e', metavar='email',
        help='use to add email or search on it',
        default=None)
    parser.add_argument(
        '-l', metavar='login',
        help='use to add login or search on it',
        default=None)
    parser.add_argument(
        '-s', metavar='site',
        help='use to add site or search on it',
        default=None)
    parser.add_argument(
        '-p', metavar='password',
        help='use to add password', default=None)
    parser.add_argument(
        '-d', metavar='description',
        help='use to add short description or search on it with regexp',
        default=None)
    parser.set_defaults(func=password.search)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser(
        'add',
        help='Add new password to database')
    parser_add.set_defaults(func=password.add)

    parser_edit = subparsers.add_parser(
        'edit',
        help='Edit record from database')
    parser_edit.set_defaults(func=password.edit, no_input=True)

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
