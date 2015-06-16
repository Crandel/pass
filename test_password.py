#!/usr/bin/env python
import unittest
import password
import argparse

query = (
    'test_id',
    'test_email',
    'test_password',
    'test_login',
    'test_site',
    'test_description'
)
arguments = argparse.Namespace(
    e='arguments_email',
    p='arguments_password',
    l='arguments_login',
    s='arguments_site',
    d='arguments_desc'
)


class TestCreateFromQuery(unittest.TestCase):

    def test_create_from_query(self):
        test_pass = password.Password()
        test_pass.create_pass(query)
        # self.assertEqual(expected, create_from_query(self, list))
        assert test_pass.email == 'test_email'
        assert test_pass.password == 'test_password'
        assert test_pass.login == 'test_login'
        assert test_pass.site == 'test_site'
        assert test_pass.description == 'test_description'

    def test_create_from_args(self):
        test_pass = password.Password()
        test_pass.create_pass(arguments)
        # self.assertEqual(expected, create_from_query(self, list))
        assert test_pass.email == 'arguments_email'
        assert test_pass.password == 'arguments_password'
        assert test_pass.login == 'arguments_login'
        assert test_pass.site == 'arguments_site'
        assert test_pass.description == 'arguments_desc'


# class TestClipboard(unittest.TestCase):
#    def test_clipboard(self):
#        # self.assertEqual(expected, clipboard(self, text))
#        assert False # TODO: implement your test here
#
# class TestParseResults(unittest.TestCase):
#    def test_parse_results(self):
#        # self.assertEqual(expected, parse_results(self, results))
#        assert False # TODO: implement your test here
#
# class TestSearch(unittest.TestCase):
#    def test_search(self):
#        # self.assertEqual(expected, search(self, arguments, *args, **kwargs))
#        assert False # TODO: implement your test here
#
# class TestAdd(unittest.TestCase):
#    def test_add(self):
#        # self.assertEqual(expected, add(self, arguments, *args, **kwargs))
#        assert False # TODO: implement your test here
#
# class TestParams(unittest.TestCase):
#    def test_params(self):
#        # self.assertEqual(expected, params(self, password))
#        assert False # TODO: implement your test here
#
# class TestDelete(unittest.TestCase):
#    def test_delete(self):
#        # self.assertEqual(expected, delete(self, arguments, *args, **kwargs))
#        assert False # TODO: implement your test here
#
# class TestEdit(unittest.TestCase):
#    def test_edit(self):
#        # self.assertEqual(expected, edit(self, arguments, *args, **kwargs))
#        assert False # TODO: implement your test here
#
# class TestParseArgs(unittest.TestCase):
#    def test_parse_args(self):
#        # self.assertEqual(expected, parse_args())
#        assert False # TODO: implement your test here
#
# class TestMain(unittest.TestCase):
#    def test_main(self):
#        # self.assertEqual(expected, main())
#        assert False # TODO: implement your test here

if __name__ == '__main__':
    unittest.main()
