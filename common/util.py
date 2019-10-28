#!/usr/bin/env python3

import os
import subprocess

#class for changing context as:
#with cd() as "newPath":
#   ...

class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class ssh_session:
    #initialize a connection through
    def __init__(self, user , host, port=22, avoidTimeout=False):
        print('\nOpen tunnel connection to server.')
        self.user_host = '{}@{}'.format(user, host)
        self.port = port
        self.socket = '~/.ssh/{}'.format(self.user_host)
        if avoidTimeout:
            self.option = '-o serverAliveInterval=120'
        else:
            self.option = ''
        print('ssh -M -f -N -o ControlPath={} {} -p {} {}'.format(self.socket, self.option, self.port, self.user_host))

    def __enter__(self):
        #subprocess.call('ssh -M -f -N -o ControlPath={} {} -p {} {}'.format(self.socket, self.option, self.port, self.user_host).split())
        return self

    def __exit__(self, etype, value, traceback):
        pass


    def __del__(self):
        print('\nClose connection.')
        subprocess.call('ssh -S {} -O exit {}'.format(self.socket, self.user_host).split())

    def get_param(self):
        return 'ssh -S {} -p {} {}'.format(self.socket, self.port, self.user_host)

    def run_commands(self, cmd):
        with open('ssh_commands.sh', 'w') as cmd_file:
            cmd_file.write(cmd)
        #subprocess.call('cat ssh_commands.sh | ssh -T asic_tuwien_gateway1'.split(),shell=True)
        #subprocess.call('cat ssh_commands.sh | ssh -T -S {} -p {} {}'.format(self.socket, self.port, self.user_host).split(),shell=True)
        proc1 = subprocess.Popen('cat ssh_commands.sh'.split(), stdout=subprocess.PIPE)
        proc2 = subprocess.Popen('ssh -T -S {} -p {} {}'.format(self.socket, self.port, self.user_host).split(), stdin=proc1.stdout, stdout=subprocess.PIPE)
        proc1.wait()
        proc2.wait()
        os.remove('ssh_commands.sh')

    def copy_to(self, source, destination):
        subprocess.call('scp -o ControlPath={socket} -P {port} {source} {server}:{dest}'.format(
            socket=self.socket,
            port=self.port,
            source=source,
            server=self.user_host,
            dest=destination
        ).split())

    def copy_from(self, source, destination):
        subprocess.call('scp -o ControlPath={socket} -P {port} {server}:{source} {dest}'.format(
            socket=self.socket,
            port=self.port,
            source=source,
            server=self.user_host,
            dest=destination
        ).split())

    def clean(self, folderPath):
        rmCmd = 'rm -r {folderPath}'.format(folderPath=folderPath)
        mkdirCmd = 'mkdir {folderPath}'.format(folderPath=folderPath)
        self.run_commands(rmCmd)
        self.run_commands(mkdirCmd)

def get_choice(options, msg='Type the number corresponding to your choice and press enter:\n', str_val=False, print_menu=True):
    if type(options).__name__ == 'range':
        str_val = False
        print_menu = False

    #prints all options in a menu like fashion
    if print_menu:
        for item in options:
            print('\t{}) {}'.format(options.index(item) + 1, item))

    choice = ''
    while True:
        choice = input(msg)
        if choice.isdigit():
            if type(options).__name__ == 'range':
                if int(choice) in options:
                    return int(choice)
                else:
                    print('Error. Invalid option. Try again.')
            elif 0 < int(choice) <= len(options):
                return int(choice)
            else:
                print('Error. Invalid option. Try again.')
        #in case I want a string choice
        #
        elif str_val:
            return choice
        else:
            print('Error. Invalid option. Try again.')
