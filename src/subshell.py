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

vms = {'api': [f'vm00{i}' for i in range(6)],
       'core': [f'vm00{i}' for i in range(4)],
       'db': [f'vm00{i}' for i in range(2)],
       }


class ShellError(ValueError):
    pass


class Shell(Cmd):
    intro = 'Welcome to the shell. Type help or ? to list commands.\n'

    def __init__(self):
        self.path = []
        self.prompt = ''
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

    def do_dev(self, line):
        """Alias for cd dev
        """
        self.do_cd('dev')

    def do_test(self, line):
        """Alias for cd test
        """
        self.do_cd('test')

    def do_acc(self, line):
        """Alias for cd acc
        """
        self.do_cd('acc')

    def do_prod(self, line):
        """Alias for cd prod
        """
        self.do_cd('prod')

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
        - [ENV, components]
        - [ENV, components, api]
        - [ENV, components, core]
        - [ENV, components, db]
        """
        match path:
            case [env]:
                return ['users', 'vms']
            case [env, 'users']:
                return ['alice', 'bob']
            case [env, 'users', *_]:
                return []
            case [env, 'vms']:
                return self.list_vms()
            case [env, 'vms', vm]:
                return self.list_vm(vm)
            case [env, 'components']:
                return ['api', 'core', 'db']
            case [env, 'components', component]:
                return self.list_components(env, component)
            case _:
                raise ShellError(f'Invalid path: {path}')

    def list_vms(self) -> list[str]:
        return [component
                for components in vms.values()
                for component in components]

    def list_vm(self, vm: str) -> list[str]:
        if vm in self.list_vms():
            return []

        raise ShellError(f'Invalid path: vm/{vm}')

    def list_components(self, env: str, component: str) -> list[str]:
        match component:
            case 'api':
                return vms['api']
            case 'core':
                return vms['core']
            case 'db':
                return vms['db']
            case _:
                raise ShellError(f'Invalid path: {env}/components/{component}')

    def validate_path(self, path):
        self.list_dirs(path)

    def cmdloop(self, intro=''):
        try:
            super().cmdloop(intro)

        except KeyboardInterrupt:
            sys.exit('(user exit)')
        except ShellError as e:
            if COLOR:
                print(ORANGE, '***', e, RESET, file=sys.stderr)
            else:
                print(e)

            # continue
            self.cmdloop(intro)

    def default(self, line):
        raise ShellError(f'Unknown syntax: {line}')

    def complete_cd(self, text, line, begidx, endidx) -> list[str]:
        return self.completions(text, line, begidx, endidx)

    def complete_list(self, text, line, begidx, endidx) -> list[str]:
        return self.completions(text, line, begidx, endidx)

    def completions(self, text, line, begidx, endidx) -> list[str]:
        try:
            # remove the last command prefix to obtain the leading args
            line = line[:begidx]

            args = parse_path(line)
            # subtract the command 'cd'
            path = self.path + args[1:]

            dirs = self.list_dirs(path)
        except ShellError:
            return []

        if text:
            return [item for item in dirs if item.startswith(text)]

        return dirs


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
    # format: word [word ...]
    words = r'[\w\-\.@]+(\s+[\w\-\.@]+)*'

    arg = arg.strip()

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
