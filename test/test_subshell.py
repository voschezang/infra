from subshell import Shell


def test_shell():
    Shell()


def test_do_list():
    Shell().do_list('')
    Shell().do_list('something')


def test_do_cd():
    Shell().do_cd('')
    Shell().do_cd('there')
