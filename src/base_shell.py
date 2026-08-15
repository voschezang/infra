from cmd import Cmd
import re
import sys

PROMPT = '$ '

# enable colored output
COLOR = False

BOLD = '\033[1m'
ORANGE = '\033[38;5;208m'
RED = '\033[31m'
RESET = '\033[0m'


class ShellError(ValueError):
    pass


class BaseShell(Cmd):
    intro = 'Welcome to the shell. Type help or ? to list commands.\n'

    def __init__(self):
        super().__init__()
        self.path = []
        self.prompt = ''

        # go home
        self.do_cd('')

    def do_list(self, line: str):
        """List directories

        list [PATH ...]
        """
        path = self.path + parse_path(line)
        dirs = self.list_dirs(path)

        for directory in dirs:
            print(directory)

    def do_cd(self, line: str):
        """Change directory
        Return home when PATH is not provided.

        cd [PATH ...]
        """
        if line:
            # infer absolute path
            path = self.path + parse_path(line)
        else:
            # clear path to return home
            path = []

        self.mutate_path(path)
        self.validate_path(path)
        self.path = path

        self.prompt = self.generate_prompt()

    def list_dirs(self, path: list[str]) -> list[str]:
        """Stub to list directories
        """
        return []

    def validate_path(self, path: list[str]):
        """Validate path
        Raises ShellError if validation fails.
        """
        self.list_dirs(path)

    def mutate_path(self, path: list[str]):
        """Implements `cd ..` to go up a directory.
        Modifies `path`.
        """
        for i, folder in enumerate(path):
            if folder == '..':
                if i > 0:
                    del path[i]
                    del path[i-1]
                else:
                    raise ShellError(f'cd: Cannot go up: {path}')

    def generate_prompt(self) -> str:
        """Generate a user prompt.
        Returns 
        ```
        (path/to/directory)
        $
        ```
        """
        if not self.path:
            return PROMPT

        s = '/'.join(self.path)

        if COLOR:
            return f'( {BOLD}{s}{RESET} )\n{PROMPT}'

        return f'( {s} )\n{PROMPT}'

    ########################################################################
    # Overrides of Cmd
    ########################################################################

    def cmdloop(self, intro=''):
        """Run Cmd.cmdloop but catch ShellError instances.
        Continue after errors.
        Overrides Cmd.cmdloop
        """
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
        """Default command handler
        Overrides Cmd.default
        """
        raise ShellError(f'Unknown syntax: {line}')

    def completedefault(self, *args) -> list[str]:
        """This enables autocompletions for the `do_cd` command.
        Overrides Cmd.completedefualt
        """
        text, line, begidx, endidx = args

        try:
            # remove the last command prefix to obtain the leading args
            line = line[:begidx]

            match parse_args(line):
                case [_command]:
                    path = self.path
                case [_command, *paths]:
                    # focus on completing the last argument
                    path = self.path + paths[-1]
                case _:
                    path = self.path

            dirs = self.list_dirs(path)

        except ShellError:
            # ignore ShellError raised by parse_args() or list_dirs()
            return []

        if text:
            return [item for item in dirs if item.startswith(text)]

        return dirs


def parse_args(line: str) -> list[list[str]]:
    """Extract words from the `arg` string.
    E.g.
    - list this/directory and/this/one
    """
    # format: word [word ...]
    words = r'[\w\-\.@]+(\s+[\w\-\.@]+)*'
    lines = line.strip().split()

    if lines == []:
        return []

    return [parse_path(line) for line in lines]


def parse_path(line: str) -> list[str]:
    """Extract words from the `arg` string.
    Expects a single term like:
    - my_path
    - users/First.Second@company.com
    """
    words = r'[\w/\-\.@]+'
    lines = line.strip().split()

    match lines:
        case []:
            return []
        case [path]:
            if re.fullmatch(words, path):
                return [s.lower() for s in path.split('/')]
        case _:
            raise ShellError(f'Too many arguments: {lines}')

    raise ShellError(f'Syntax error: Invalid arguments: {lines}')


if __name__ == '__main__':
    COLOR = True

    shell = BaseShell()
    shell.cmdloop()
