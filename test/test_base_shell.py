
from unittest.mock import patch

from pytest import raises

from base_shell import PROMPT, BaseShell, ShellError, parse_path


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


def test_do_cd():
    shell = BaseShell()
    assert shell.prompt == PROMPT
    assert shell.path == []

    shell.do_cd('')
    assert shell.prompt == PROMPT
    assert shell.path == []


def test_do_list_after_cd():
    shell = BaseShell()
    shell.path = ['dev']

    shell.do_list('')
    shell.do_list('users')


def test_parse_path():
    assert parse_path('some') == ['some']
    assert parse_path('DEV   ') == ['dev']
    assert parse_path('   my.name') == ['my.name']
    assert parse_path('dev users my.name') == ['dev', 'users', 'my.name']
    assert parse_path('   \t') == []

    with raises(ShellError):
        parse_path('  \\t')

    with raises(ShellError):
        parse_path('!*')
