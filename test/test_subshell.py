
from pytest import raises

from subshell import Shell, PROMPT, ShellError


def test_shell():
    Shell()


def test_do_list():
    Shell().do_list('')
    Shell().do_list('something')


def test_do_cd():
    shell = Shell()
    assert shell.prompt == PROMPT
    assert shell.path == []

    shell.do_cd('')
    assert shell.prompt == PROMPT
    assert shell.path == []


def test_do_cd_single_arg():
    shell = Shell()
    shell.do_cd('there')
    assert shell.prompt == f'there\n{PROMPT}'
    assert shell.path == ['there']

    # return home
    shell.do_cd('')
    assert shell.prompt == PROMPT
    assert shell.path == []


def test_do_cd_multi_arg():
    shell = Shell()
    shell.do_cd('first    second')
    assert shell.prompt == f'first/second\n{PROMPT}'
    assert shell.path == ['first', 'second']


def test_do_cd_unhappy():
    shell = Shell()
    with raises(ShellError):
        shell.do_cd('.a')

    with raises(ShellError):
        shell.do_cd('go.here')
