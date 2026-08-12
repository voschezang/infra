
from pytest import raises

from subshell import ENVS, PROMPT, Shell, ShellError, env_status, parse_env, parse_path, show_cluster


def test_shell():
    Shell()


def test_do_cd():
    shell = Shell()
    assert shell.prompt == PROMPT
    assert shell.path == []

    shell.do_cd('')
    assert shell.prompt == PROMPT
    assert shell.path == []


def test_do_cd_single_arg():
    shell = Shell()
    shell.do_cd('dev')
    assert shell.prompt == f'dev\n{PROMPT}'
    assert shell.path == ['dev']

    # return home
    shell.do_cd('')
    assert shell.prompt == PROMPT
    assert shell.path == []

    shell.path = ['dev']
    shell.do_cd('users')
    assert shell.path == ['dev', 'users']


def test_do_cd_multi_arg():
    shell = Shell()
    shell.do_cd('dev    users')
    assert shell.prompt == f'dev/users\n{PROMPT}'
    assert shell.path == ['dev', 'users']

    shell.do_cd('')
    shell.do_cd('dev users my.name')
    assert shell.prompt == f'dev/users/my.name\n{PROMPT}'
    assert shell.path == ['dev', 'users', 'my.name']


def test_do_cd_unhappy():
    shell = Shell()
    with raises(ShellError):
        shell.do_cd('abc')

    with raises(ShellError):
        shell.do_cd('dev users my.name!')


def test_do_list_from_root():
    Shell().do_list('')
    Shell().do_list('dev users')

    with raises(ShellError):
        Shell().do_list('abc')


def test_do_list_after_cd():
    shell = Shell()
    shell.path = ['dev']

    shell.do_list('')
    shell.do_list('users')


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


def test_list_dirs():
    shell = Shell()
    assert shell.list_dirs([]) == ENVS
    assert shell.list_dirs(['dev']) == ['users', 'vms']
    assert shell.list_dirs(['test', 'users']) == ['alice', 'bob']


def test_list_vms():
    shell = Shell()
    assert len(shell.list_vms()) == 12


def test_list_vm():
    assert Shell().list_vm('vm001') == []

    with raises(ShellError):
        Shell().list_vm('vm9')


def test_list_components():
    shell = Shell()
    assert len(shell.list_components('dev', 'api')) == 6
    assert len(shell.list_components('dev', 'core')) == 4
    assert len(shell.list_components('dev', 'db')) == 2


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
