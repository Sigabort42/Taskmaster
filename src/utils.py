#!/usr/bin/env python3

COMMAND_AVAILABLE = "========================================\n\tcommands available are:\n========================================\n{start [name|all]}\t{stop [name|all]}\t{restart [name|all]}\n{help}\t{status}\n"

ALREADY_STOPPED = "-----------------------------\n{}: Already Stopped\n-----------------------------"

STOPPED = "-----------------------------\n{}: Stopped\n-----------------------------"

STARTED = "-----------------------------\n{}: Started\n-----------------------------"

ALREADY_RUNNING = "-----------------------------\n{}: Already Running\n-----------------------------"

CMD_STATUS = "\nname of program: {}\npid is: [{}]\ncommand is [{}]\nEtat is [{}]\n"

def retablir_str(s):
    if s.find("\"") != -1:
        s = s.replace("\"", "")
        s = s.replace("_", " ")
    elif s.find("'") != -1:
        s = s.replace("'", "")
        s = s.replace("_", " ")
    return s

def check_proc(n):
    if n == -1:
        return "HUP"
    elif n == -2:
        return "INTERRUPT"
    elif n == -3:
        return "QUIT"
    elif n == -6:
        return "SIGABORT"
    elif n == -9:
        return "STOPPED"
    elif n == -14:
        return "ALARM"
    elif n == -15 or n == 0:
        return "STOPPED"
    return "RUNNING"

