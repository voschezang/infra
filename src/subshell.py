from cmd import Cmd
import re
import sys

PROMPT = '$ '


class ShellError(ValueError):
    pass


class Shell(Cmd):
    intro = 'Welcome to the shell. Type help or ? to list commands.\n'
    prompt = PROMPT
    path = []

    def do_list(self, arg):
        for i in range(3):
            print(f'file {i}')

    def do_cd(self, arg):
        """"Change directory

        cd [path]
        """
        if not arg:
            args = []
        elif re.fullmatch(r'(\w+\s*)+', arg):
            args = arg.split()
        else:
            raise ShellError('Invalid arguments')

        if not args:
            self.path = []
        else:
            self.path.extend(args)

        self.prompt = generate_prompt(self.path)

    def cmdloop(self, intro=''):
        try:
            super().cmdloop(intro)

        except KeyboardInterrupt:
            sys.exit('(user exit)')


def generate_prompt(path: list[str]) -> str:
    if not path:
        return PROMPT

    s = '/'.join(path)
    return f'{s}\n{PROMPT}'


if __name__ == '__main__':
    Shell().cmdloop()
