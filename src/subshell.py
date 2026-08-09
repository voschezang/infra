from cmd import Cmd
import random
import re
import sys
from tabulate import tabulate

PROMPT = '$ '
ENVS = ['dev', 'test', 'acc', 'prod']

# enable colored output
COLOR = False

# ignore ShellError exceptions
STRICT = False

BOLD = '\033[1m'
ORANGE = '\033[38;5;208m'
RED = '\033[31m'
RESET = '\033[0m'


class ShellError(ValueError):
    pass


class Shell(Cmd):
    intro = 'Welcome to the shell. Type help or ? to list commands.\n'

    def __init__(self):
        self.path = []
        self.prompt = ''
        self.tree = {env: {'users': {},
                           'vms': {}
                           } for env in ENVS}

        super().__init__()

        # go home
        self.do_cd('')

    def do_list(self, arg):
        """List directories

        list [PATH ...]
        """
        path = self.path + parse_path(arg)
        dirs = self.list_dirs(path)

        for directory in dirs:
            print(directory)

    def do_cd(self, arg):
        """Change directory
        Return home when PATH is not provided.

        cd [PATH ...]
        """
        if not arg:
            # return home
            self.path = []

        path = self.path + parse_path(arg)
        self.validate_path(path)
        self.path = path
        self.prompt = generate_prompt(self.path)

    def do_show(self, arg):
        path = self.path + parse_path(arg)
        self.validate_path(path)

        match path:
            case []:
                show_envs()
            case [env]:
                print(f'{env}: {env_status(env)}')
            case [env, 'vms']:
                print(show_cluster(env))
            case _:
                self.do_list(arg)

    def list_dirs(self, path: list[str]) -> list[str]:
        """List directories
        Path can be
        - [] 
        - [ENV] 
        - [ENV, *]
        where ENV is dev, test, acc or prod 
        """
        match path:
            case []:
                return ENVS
            case [env, *_]:
                verify_env(env)
                return self.list_environment_dirs(path)
            case _:
                raise ShellError('Invalid path')

    def list_environment_dirs(self, path: list[str]) -> list[str]:
        """List environment directories
        Path can be
        - [ENV]
        - [ENV, users]
        - [ENV, users, *]
        - [ENV, vms]
        - [ENV, vms, *]
        """
        match path:
            case [env]:
                return ['users', 'vms']
            case [env, 'users']:
                return ['alice', 'bob']
            case [env, 'users', *_]:
                return []
            case [env, 'vms']:
                return ['vm0001', 'vm0002']
            case [env, 'vms', *_]:
                return []
            case _:
                raise ShellError('Invalid path')

    def validate_path(self, path):
        self.list_dirs(path)

    def cmdloop(self, intro=''):
        try:
            super().cmdloop(intro)

        except KeyboardInterrupt:
            sys.exit('(user exit)')
        except ShellError as e:
            if COLOR:
                print(ORANGE, e, RESET)
            else:
                print(e)

            # continue
            self.cmdloop(intro)


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


def status() -> str:
    """Returns 'ok' or 'x' at random.
    """
    ok = 'ok'
    nok = f'{RED}x{RESET}'

    return random.choice([ok, nok])


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


def verify_env(env):
    if env not in ENVS:
        raise ShellError(f'Invalid environment: {env}')


def parse_env(env: str):
    """Parse environment
    """
    env = env.lower()
    verify_env(env)
    return env


if __name__ == '__main__':
    STRICT = False
    COLOR = True

    shell = Shell()
    shell.cmdloop()
