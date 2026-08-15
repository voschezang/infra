
from unittest.mock import patch

from pytest import raises

from base_shell import PROMPT, BaseShell, ShellError, parse_path, parse_args


def test_baseshell():
    shell = BaseShell()

    with raises(ShellError):
        shell.default('')


def test_completedefault():
    shell = BaseShell()
    args = ('', '', 0, 0)
    assert shell.completedefault(*args) == []

    directories = ['hello']
    with patch.object(shell, 'list_dirs', return_value=directories, autospec=True):

        assert shell.completedefault(*args) == ['hello']
        assert shell.completedefault('he', 'bye he', 4, 6) == ['hello']
        assert shell.completedefault('bye', 'bye ', 0, 2) == []
        assert shell.completedefault('hel', 'bye bye hel ', 8, 11) == ['hello']
        assert shell.completedefault('bye', 'bye bye hel ', 8, 11) == []

        assert shell.completedefault('h', 'one/two/h', 8, 8) == ['hello']
        assert shell.completedefault('3', 'one/two/t', 8, 8) == []


def test_do_cd():
    shell = BaseShell()
    assert shell.prompt == PROMPT
    assert shell.path == []

    shell.do_cd('')
    assert shell.prompt == PROMPT
    assert shell.path == []

    with raises(ShellError):
        shell.do_cd('a b')


def test_do_cd_up():
    shell = BaseShell()
    shell.path = ['a']
    shell.do_cd('..')
    assert shell.path == []

    with raises(ShellError):
        shell.do_cd('..')


def test_do_list_after_cd():
    shell = BaseShell()
    shell.path = ['dev']

    shell.do_list('')
    shell.do_list('users')


def test_parse_path():
    assert parse_path('some') == ['some']
    assert parse_path('DEV   ') == ['dev']
    assert parse_path('   my.name') == ['my.name']
    assert parse_path('dev/users/my.name') == ['dev', 'users', 'my.name']
    assert parse_path('   \t') == []

    with raises(ShellError):
        parse_path('  \\t')

    with raises(ShellError):
        parse_path('!*')

    with raises(ShellError):
        parse_path('one two')


def test_parse_args():
    assert parse_args('') == []
    assert parse_args('a b 2') == [['a'], ['b'], ['2']]
    assert parse_args('a/b/c') == [['a', 'b', 'c']]
    assert parse_args('a/b/c def') == [['a', 'b', 'c'], ['def']]
