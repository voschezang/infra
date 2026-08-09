from cmd import Cmd
import random
import re
import sys
from tabulate import tabulate

PROMPT = '$ '
ENVS = ['dev', 'test', 'acc', 'prod']
COLOR = False

BOLD = '\033[1m'
# ORANGE = '\033[38;5;208m'
RED = '\033[31m'
RESET = '\033[0m'


class ShellError(ValueError):
    pass


class Shell(Cmd):
    intro = 'Welcome to the shell. Type help or ? to list commands.\n'

    def __init__(self):
        self.path = []
        self.prompt = ''

        # go home
        self.do_cd('')

    def do_list(self, arg):
        path = parse_validate_path(arg, self.path)

        match path:
            case []:
                for env in ENVS:
                    print(env)

            case [env]:
                print('users')
                print('vms')

            case [env, 'users']:
                for i in range(3):
                    print(f'user_{i}')

            case _:
                raise ShellError('Invalid arguments')

    def do_cd(self, arg):
        """"Change directory

        cd [PATH, ...], PATH
        """
        if not arg:
            # return home
            self.path = []

        self.path = parse_validate_path(arg, self.path)
        self.prompt = generate_prompt(self.path)

    def do_show(self, arg):
        # TODO add self.path to parse_path instead of custom logic here
        path = parse_validate_path(arg, self.path)

        match path:
            case []:
                show_envs()
            case ['envs']:
                show_envs()
            case [env]:
                print(f'{env}: {env_status(env)}')
            case ['envs', env]:
                print(f'{env}: {env_status(env)}')
            case ['envs', env, 'vms']:
                print(show_cluster(env))

    def cmdloop(self, intro=''):
        try:
            super().cmdloop(intro)

        except KeyboardInterrupt:
            sys.exit('(user exit)')


def generate_prompt(path: list[str]) -> str:
    if not path:
        return PROMPT

    s = '/'.join(path)

    if COLOR:
        return f'( {BOLD}{s}{RESET} )\n{PROMPT}'

    return f'{s}\n{PROMPT}'


def show_envs():
    for env in ENVS:
        print(f'{env:<4}: {env_status(env)}')


def env_status(env: str) -> str:
    env = parse_env(env)

    # mimic a faulty environment
    if env == 'acc':
        if COLOR:
            return f'{RED}x{RESET}'
        else:
            return 'x'

    return 'ok'


def show_cluster(env: str) -> str:
    data = [
        ['core'] + [status() for _ in range(4)],
        ['db'] + [status() for _ in range(2)],
        ['api'] + [status() for _ in range(6)],
    ]

    return tabulate(data,
                    headers=['', '1', '2', '3', '4', '5', '6'],
                    tablefmt="plain")


def status():
    ok = 'ok'
    nok = f'{RED}x{RESET}'

    return random.choice([ok, nok])


def parse_env(env: str):
    """ Parse environment
    """
    env = env.lower()

    if env not in ENVS:
        raise ShellError(f'Invalid environment: {env}')

    return env


def parse_validate_path(arg: str, path: list[str]) -> list[str]:
    path += parse_path(arg)
    validate_path(path)
    return path


def parse_path(arg: str) -> list[str]:
    """Extract words from the `arg` string.
    """
    # fomrat: word [words]
    words = r'[\w\-\.@]+(\s+[\w\-\.@]+)*'

    if not arg:
        return []
    elif re.fullmatch(words, arg):
        return [s.lower() for s in arg.split()]

    raise ShellError('Invalid arguments')


def validate_path(path: list[str]):
    """Validate path
    Path can be
    - [] 
    - [ENV] 
    - [ENV, *]
    where ENV is dev, test, acc or prod 
    """
    match path:
        case []:
            pass
        case [env, *_]:
            verify_env(env)
            validate_env_path(path)
        case _:
            raise ShellError('Invalid path')


def validate_env_path(path):
    """Validate environment path
    Path can be
    - [ENV, users, *]
    - [ENV, vms]
    """
    match path:
        case [env]:
            pass
        case [env, 'users']:
            pass
        case [env, 'users', *_]:
            pass
        case [env, 'vms']:
            pass
        case _:
            raise ShellError('Invalid path')


def verify_env(env):
    if env not in ENVS:
        raise ShellError(f'Invalid environment: {env}')


if __name__ == '__main__':
    shell = Shell()
    COLOR = True
    shell.cmdloop()
