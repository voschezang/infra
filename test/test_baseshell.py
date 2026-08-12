
from pytest import raises

from baseshell import PROMPT, BaseShell, ShellError, parse_path


def test_baseshell():
    BaseShell()


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
