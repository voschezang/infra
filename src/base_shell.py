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
        if not line:
            # return home
            self.path = []

        path = self.path + parse_path(line)
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

    def generate_prompt(self) -> str:
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

            args = parse_path(line)
            # subtract the command 'cd'
            path = self.path + args[1:]

            dirs = self.list_dirs(path)

        except ShellError:
            return []

        if text:
            return [item for item in dirs if item.startswith(text)]

        return dirs


def parse_path(line: str) -> list[str]:
    """Extract words from the `arg` string.
    """
    # format: word [word ...]
    words = r'[\w\-\.@]+(\s+[\w\-\.@]+)*'

    line = line.strip()

    if not line:
        return []
    elif re.fullmatch(words, line):
        return [s.lower() for s in line.split()]

    raise ShellError('Syntax error: Invalid arguments')


if __name__ == '__main__':
    COLOR = True

    shell = BaseShell()
    shell.cmdloop()
