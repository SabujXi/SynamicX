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
        pass

    def close(self):
        self.__loop_running = False

    def on_print_last_set(self):
        self.print(self.__last_set_value)

    def on_py(self, arg):
        'write python code in one line'
        try:
            local = {}
            namespace = ProxyNameSpace(self.__permanent_local_for_py, local)
            line_buffer = []
            if arg == "i":
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
                line_buffer.append(arg)
            src = "\n".join(line_buffer)
            self.print("Python Source:\n%s" % src)
            print("-------------")
            exec(src, globals(), namespace)
            # for key, value in local.items():
            #     self.print(key + ": " + str(value))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.print_error("Exception Type: %s" % exc_type.__name__)
            self.print_error("Exception: %s" % exc_value)
            # self.print_error("Exception Traceback: %s" % traceback.extract_tb(exc_traceback))

    def on_pyr(self):
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

    def on_p(self, arg):
        self.on_py(arg)

    def on_pi(self):
        self.on_py("i")

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
        self.print("pre_loop() executed.")

    def loop(self):
        self.pre_loop()

        self.__loop_running = True
        while self.__loop_running:
            _inres = self.input(self.prompt_text)
            inres = _inres.strip()
            if not inres:
                self.on_empty()
                continue
            first_command = command_split_pat.split(inres)[0]
            _arg_str = inres[len(first_command):]
            arg_str = _arg_str.strip()

            if not command_pat.match(first_command):
                self.print_error("Invalid first command format")
                continue
            if first_command in self.symbol_to_method:
                first_command = self.symbol_to_method[first_command]

            is_shellx = True
            attr = getattr(self, "on_shellx_" + first_command, None)
            if not attr:
                attr = getattr(self, "on_" + first_command, None)
                is_shellx = False

            if not attr:
                if first_command in self.__permanent_local_for_py:
                    self.print(self.__permanent_local_for_py[first_command])
                else:
                    self.print_error("Command not found")
                continue
            if callable(attr):
                callable_attr = attr
                kwonlyargs = inspect.getfullargspec(callable_attr).kwonlyargs
                positional_args = inspect.getfullargspec(callable_attr).args
                no_of_positional_args = len(positional_args)
                print(kwonlyargs)
                if is_shellx:
                    self.print("******shellargs wala fun**********")
                    shellargs = shlex.split(arg_str)
                    if no_of_positional_args > 0 + 1:
                        if not len(shellargs) >= no_of_positional_args:
                            self.print_error("Insufficient amount of shellargs provided for positional args.\n"
                                             "Positional args: %s\n"
                                             "shellargs: %s" % (positional_args, shellargs))
                            continue
                        else:
                            # _pos_args = shellargs[:no_of_positional_args]
                            # _rest_of_shellargs = shellargs[no_of_positional_args:]
                            callable_attr(*shellargs)
                    else:
                        callable_attr(*shellargs)
                else:
                    if no_of_positional_args == 0 + 1:
                        attr()
                    elif no_of_positional_args == 1 + 1:
                        attr(arg_str)
                    else:
                        self.print_error("Handling method for `%s` contains %d number of positional args" % (first_command, no_of_positional_args))
            else:
                self.print_error("Invalid command provided: `%s`" % first_command)
                continue
        self.close()
        self.post_loop()

    def on_exit(self, arg):
        'Exitting...'
        print("Exiting Synamic Shell ...")
        self.close()

    def post_loop(self):
        self.print("post_loop() executed")

