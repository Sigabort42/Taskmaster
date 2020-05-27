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
