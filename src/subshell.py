

from cmd import Cmd

PROMPT = '$ '


class Shell(Cmd):
    intro = 'Welcome to the shell. Type help or ? to list commands.\n'
    prompt = PROMPT
    path = []

    def do_list(self, arg):
        for i in range(3):
            print(f'file {i}')

    def do_cd(self, arg):
        if arg == '':
            return
        self.path.append(arg)
        self.prompt = f'{arg}> '


if __name__ == '__main__':
    Shell().cmdloop()
