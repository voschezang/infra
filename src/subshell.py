import random
from tabulate import tabulate

from baseshell import BaseShell, ShellError, parse_path, COLOR, BOLD, RED, ORANGE, RESET

ENVS = ['dev', 'test', 'acc', 'prod']
OK = '✓'

vms = {'api': [f'vm00{i}' for i in range(6)],
       'core': [f'vm00{i}' for i in range(4)],
       'db': [f'vm00{i}' for i in range(2)],
       }


class Shell(BaseShell):
    def do_show(self, line):
        """Displays a summary of the current working directory.

        show
          - shows the status of each environment
        show ENV
          - shows the status of environment ENV
        show ENV vms
          - show the status of all VMs in environment ENV
        """
        path = self.path + parse_path(line)
        self.validate_path(path)

        match path:
            case []:
                show_envs()
            case [env]:
                print(f'{env}: {env_status(env)}')
            case [env, 'vms']:
                print(show_cluster(env))
            case [env, 'vms', vm]:
                print(vm, status())
            case [env, 'components', component]:
                for vm in vms[component]:
                    print(f'{vm}: {status()}')
            case _:
                self.do_list(line)

    def do_dev(self, line):
        """Alias for `cd dev`
        """
        self.do_cd('dev')

    def do_test(self, line):
        """Alias for `cd test`
        """
        self.do_cd('test')

    def do_acc(self, line):
        """Alias for `cd acc`
        """
        self.do_cd('acc')

    def do_prod(self, line):
        """Alias for `cd prod`
        """
        self.do_cd('prod')

    def list_dirs(self, path: list[str]) -> list[str]:
        """List directories
        Path must be one of:
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
        Path must be one of:
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

    if COLOR:
        return f'{BOLD}{OK}{RESET}'
    return OK


def show_cluster(env: str) -> str:
    data = [
        ['core'] + [status() for _ in vms['core']],
        ['db'] + [status() for _ in vms['db']],
        ['api'] + [status() for _ in vms['api']],
    ]

    return tabulate(data,
                    headers=['', '1', '2', '3', '4', '5', '6'],
                    tablefmt="plain")


def status() -> str:
    """Returns 'ok' or 'x' at random.
    """
    if COLOR:
        nok = f'{RED}x{RESET}'
        ok = f'{BOLD}{OK}{RESET}'
    else:
        nok = 'x'
        ok = OK

    return random.choice([ok, nok])


def parse_env(env: str):
    """Parse environment
    """
    env = env.lower()
    verify_env(env)
    return env


def verify_env(env):
    if env not in ENVS:
        raise ShellError(f'Invalid environment: {env}')


if __name__ == '__main__':
    STRICT = False
    COLOR = True

    shell = Shell()
    shell.cmdloop()
