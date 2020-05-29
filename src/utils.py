#!/usr/bin/env python3

import signal

COMMAND_AVAILABLE = "========================================\n\tcommands available are:\n========================================\n{start [name|all]}\t{stop [name|all]}\t{restart [name|all]}\n{help}\t{status}\n"

ALREADY_STOPPED = "-----------------------------\n{}: Already Stopped\n-----------------------------"

STOPPED = "-----------------------------\n{}: Stopped\n-----------------------------"

FINISHED = "-----------------------------\n{}: Finished\n-----------------------------"

STARTING = "-----------------------------\nStarting {}\n-----------------------------"

STARTED = "-----------------------------\n{}: Started\n-----------------------------"

ALREADY_RUNNING = "-----------------------------\n{}: Already Running\n-----------------------------"

CMD_STATUS = "\n{} [{}]\t\t\t[{}]\ncommand is [{}]\n"

def retablir_str(s):
    if s.find("\"") != -1:
        s = s.replace("\"", "")
        s = s.replace("_", " ")
    elif s.find("'") != -1:
        s = s.replace("'", "")
        s = s.replace("_", " ")
    return s


def graceful_stop(name_stop):
    if (name_stop == "HUP"):
        return signal.SIGHUP
    elif (name_stop == "INT"):
        return signal.SIGINT
    elif (name_stop == "QUIT"):
        return signal.SIGQUIT
    elif (name_stop == "ABRT"):
        return signal.SIGABRT
    elif (name_stop == "KILL"):
        return signal.SIGKILL
    elif (name_stop == "ALRM"):
        return signal.SIGALRM
    elif (name_stop == "TERM"):
        return signal.SIGTERM

def compare_file_reload():
    pass
