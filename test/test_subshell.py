
from pytest import raises

from subshell import Shell, PROMPT, ShellError, env_status, parse_env, show_cluster


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


def test_do_show():
    shell = Shell()
    shell.do_show('')


def test_parse_env():
    assert parse_env('dev') == 'dev'
    assert parse_env('DEV') == 'dev'

    with raises(ShellError):
        parse_env('def')


def test_env_status():
    assert env_status('dev') == 'ok'
    assert env_status('acc') == 'x'


def test_show_vms():
    lines = show_cluster('dev').splitlines()

    assert len(lines) == 4
    assert lines[0].split() == ['1', '2', '3', '4', '5', '6']
    assert 'core' in lines[1]
    assert 'db' in lines[2]
    assert 'api' in lines[3]
