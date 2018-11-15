"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""


import inspect
import shlex
import re
import sys
from pprint import pprint

command_pat = re.compile(r"[!@$?]?|[a-zA-Z0-9_-]+")
command_split_pat = re.compile(r'\s')


class ProxyNameSpace:
    def __init__(self, permanent_local, mylocal, *a, **ag):
        self.__global = permanent_local
        self.__local = mylocal

    def __getitem__(self, key):
        if key in self.__global:
            value = self.__global[key]
            self.__local[key] = value
            return value
        raise KeyError

    def __setitem__(self, key, value):
        self.__global[key] = value
        self.__local[key] = value

    def keys(self):
        return self.__global.keys()

    def items(self):
        return self.__global.items()

    def values(self):
        return self.__global.values()

    def __iter__(self):
        return self.__global.__iter__()


class BaseShell(object):
    intor_text = "Basic Shell By Md. Sabuj Sarker"
    prompt_text = "(sabuj): "

    def __init__(self, startup_commands=None, *args, **kwargs):
        self.__startup_commands = startup_commands
        self.symbol_to_method = {
            '@': 'py',
            '!': 'py',
            '?': 'help'
        }
        self.__loop_running = False
        self.__permanent_local_for_py = {}
        self.__last_set_value = None
        self.__setup_console_to_utf8()

    @staticmethod
    def __setup_console_to_utf8():
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

    def on_help(self, cmd=None):
        self.print("Help needed...")
        pass

    def on_empty(self):
        return True

    def close(self):
        self.__loop_running = False

    def on_print_last_set(self):
        self.print(self.__last_set_value)

    def on_py(self, *args):
        'write python code in one line'
        arg_0 = '' if not args else args[0]
        try:
            local = {}
            namespace = ProxyNameSpace(self.__permanent_local_for_py, local)
            line_buffer = []
            if arg_0 == "i":
                idx = 0
                while True:
                    idx += 1
                    line = self.input("%03d> " % idx)
                    if line == ":q":
                        "time to quit"
                        break
                    else:
                        line_buffer.append(line)
                        continue
            else:
                line_buffer.append(arg_0)
            src = "\n".join(line_buffer)
            self.print("Python Source:\n%s" % src)
            print("-------------")
            exec(src, globals(), namespace)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.print_error("Exception Type: %s" % exc_type.__name__)
            self.print_error("Exception: %s" % exc_value)

    def on_pyr(self, *args):
        "Recursive python - prompt another line after this one"
        'write python code in one line'

        idx = 0
        while True:
            idx += 1
            line = self.input("%04d >>> " % idx)
            line = line.strip()
            if line == ":q":
                "time to quit"
                break
            else:
                try:
                    local = {}
                    namespace = ProxyNameSpace(self.__permanent_local_for_py, local)
                    exec(line, globals(), namespace)
                    # for key, value in local.items():
                    #     self.print(key + ": " + str(value))
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.print_error("Exception Type: %s" % exc_type.__name__)
                    self.print_error("Exception: %s" % exc_value)
                continue

    def on_p(self, *args):
        return self.on_py(args)

    def on_pi(self):
        return self.on_py("i")

    def print(self, *args, **kwargs):
        print(*args, *kwargs)

    def pprint(self, *args, **kwargs):
        pprint(*args, *kwargs)

    def print_error(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def print_warning(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def input(self, prompt):
        return input(prompt)

    def pre_loop(self):
        pass

    def on_shell(self, *cmd_args):
        self.pre_loop()

        self.__loop_running = True
        last_retcode = -1
        while self.__loop_running:
            inres = self.input(self.prompt_text).strip()
            if not inres:
                empty_ret = self.on_empty()
                if empty_ret:
                    continue
                else:
                    self.__loop_running = False
                    break
            else:
                shell_args = shlex.split(inres)
                last_retcode = self.run_command(shell_args)
                continue

        self.close()
        self.post_loop()
        return last_retcode

    def run_command(self, commands: list):
        cmd_args = commands
        if not cmd_args:
            self.print_error(f'No synamic command arg(s) provided to run.')
            return 1

        first_arg = cmd_args[0]
        rest_args = cmd_args[1:]

        if not command_pat.match(first_arg):
            self.print_error("Invalid first command format")
            return 1

        if first_arg in self.symbol_to_method:
            first_arg = self.symbol_to_method[first_arg]

        attr = getattr(self, "on_" + first_arg, None)

        if not attr:
            if first_arg in self.__permanent_local_for_py:
                self.print(self.__permanent_local_for_py[first_arg])
            else:
                self.print_error(f'Command not found {first_arg}')
            return 1

        if callable(attr):
            callable_attr = attr
            kwonlyargs = inspect.getfullargspec(callable_attr).kwonlyargs
            positional_args = inspect.getfullargspec(callable_attr).args
            no_of_positional_args = len(positional_args)
            self.print(kwonlyargs)

            if no_of_positional_args > 0 + 1:
                if not len(rest_args) >= no_of_positional_args:
                    self.print_error("Insufficient amount of shellargs provided for positional args.\n"
                                     f"Positional args: {positional_args}\n"
                                     f"shellargs: {rest_args}")
                    return 1
            return callable_attr(*rest_args)
        else:
            self.print_error(f"Invalid command provided: {first_arg}")
            return 1

    def on_exit(self, *args):
        'Exitting...'
        if len(args) > 0:
            retcode = args[0]
        else:
            retcode = ''
        self.print(f"Exiting Synamic Shell with retcode {retcode}")
        self.close()
        return retcode

    def post_loop(self):
        pass

