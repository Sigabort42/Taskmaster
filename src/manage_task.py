#!/usr/bin/env python3

import signal
import os
import sys
import termios
import curses
import subprocess
#import asyncio

from src import utils


TAB_PROCESS = {}

def check_proc(n):
    if n == None:
        return "RUNNING"
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
    elif n == -15:
        return "STOPPED"
    elif n > 0:
        return "ERROR: " + str(n)
    return "FINISHED"

def receive_sig(sig_nb, frame):
    print("sig is {}".format(sig_nb))
    check_proc(sig_nb)

def handler_sig():
    signal.signal(signal.SIGHUP, receive_sig)
    signal.signal(signal.SIGINT, receive_sig)
    signal.signal(signal.SIGQUIT, receive_sig)
    signal.signal(signal.SIGILL, receive_sig)
    signal.signal(signal.SIGTRAP, receive_sig)
    signal.signal(signal.SIGABRT, receive_sig)
    signal.signal(signal.SIGBUS, receive_sig)
    signal.signal(signal.SIGFPE, receive_sig)
    #signal.signal(signal.SIGKILL, receive_sig)
    signal.signal(signal.SIGUSR1, receive_sig)
    signal.signal(signal.SIGSEGV, receive_sig)
    signal.signal(signal.SIGUSR2, receive_sig)
    signal.signal(signal.SIGPIPE, receive_sig)
    signal.signal(signal.SIGALRM, receive_sig)
    signal.signal(signal.SIGTERM, receive_sig)

class   Create():
    """Classe qui permet de creer des tasks"""

    def __init__(self, dcty, name):
        self.dcty = dcty
        self.name = name
        self.command = list(map(utils.retablir_str, dcty[name]["command"].split()))
        self.args = " ".join(dcty[name]["command"].split()[1:])

    def start_process(self):
        umask = os.umask(TAB_PROCESS[self.name]["umask"])
        os.chdir(TAB_PROCESS[self.name]["directory"])
        with open(TAB_PROCESS[self.name]["stdout"], "a") as fout:
            with open(TAB_PROCESS[self.name]["stderr"], "a") as ferr:
                out = subprocess.Popen(
                    args=self.command,
                    cwd=TAB_PROCESS[self.name]["directory"],
                    env=TAB_PROCESS[self.name]["environment"],
                    stdout=fout,
                    stderr=ferr,
                )
                TAB_PROCESS[self.name]["ret_popen"] = out
                TAB_PROCESS[self.name]["pid"] = out.pid
                print(utils.STARTING.format(self.name))
                TAB_PROCESS[self.name]["state"] = "RUNNING"
        os.umask(umask)
        
    def fork_prog(self):
        """La methode sert a  executer et recuperer les informations d'un processus enfant"""
        TAB_PROCESS[self.name] = {
            "autostart":      self.dcty[self.name]["autostart"] if "autostart"
            in self.dcty[self.name] else "",
            "autorestart":      self.dcty[self.name]["autorestart"] if "autorestart"
            in self.dcty[self.name] else "",
            "command":          " ".join(self.command),
            "directory":        self.dcty[self.name]["directory"] if "directory"
            in self.dcty[self.name] else "./",
            "environment":      self.dcty[self.name]["environment"] if "environment"
            in self.dcty[self.name] else None,
            "exitcodes":        self.dcty[self.name]["exitcodes"] if "exitcodes"
            in self.dcty[self.name] else "",
            "name":             self.name if self.name is not None else "",
            "numprocs":         self.dcty[self.name]["numprocs"] if "numprocs"
            in self.dcty[self.name] else "",
            "pid":              "",
            "ret_popen":        "",
            "state":             "STARTING",
            "stdout":           self.dcty[self.name]["stdout_logfile"] if "stdout_logfile"
            in self.dcty[self.name] else "/dev/fd/1",
            "stderr":           self.dcty[self.name]["stderr_logfile"] if "stderr_logfile"
            in self.dcty[self.name] else "/dev/fd/2",
            "umask":            int(self.dcty[self.name]["umask"]) if "umask"
            in self.dcty[self.name] else 22,
        }
        self.start_process()
        
    def run(self):
        self.fork_prog()


class   Manage:
    """Manager de Task"""

    def __init__(self, dcty):
        self.dcty = dcty


    def stop(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    print(utils.ALREADY_STOPPED.format(name))
                elif TAB_PROCESS[name]["state"] == "FINISHED":
                    print(utils.FINISHED.format(name_proc))
                else:
                    pid = TAB_PROCESS[name]["pid"]
                    os.kill(int(pid), signal.SIGTERM)
                    TAB_PROCESS[name]["state"] = "STOPPED"
                    print(utils.STOPPED.format(name))
        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "RUNNING":
                pid = TAB_PROCESS[name_proc]["pid"]
                os.kill(int(pid), signal.SIGTERM)
                TAB_PROCESS[name_proc]["state"] = "STOPPED"
                print(utils.STOPPED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "FINISHED":
                print(utils.FINISHED.format(name_proc))
            else:
                print(utils.ALREADY_STOPPED.format(name_proc))
                    
    def start(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    Create(self.dcty, name).run()
                    print(utils.STARTED.format(name))
                elif TAB_PROCESS[name]["state"] == "FINISHED":
                    Create(self.dcty, name).run()
                    print(utils.FINISHED.format(name_proc))
                else:
                    print(utils.ALREADY_RUNNING.format(name))
        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "STOPPED":
                Create(self.dcty, name_proc).run()
                print(utils.STARTED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "FINISHED":
                Create(self.dcty, name_proc).run()
                print(utils.FINISHED.format(name_proc))
            else:
                print(utils.ALREADY_RUNNING.format(name_proc))

    def run(self):
        for name in self.dcty:
            if ("autostart" in self.dcty[name] and
                self.dcty[name]["autostart"] == "true"):
                Create(self.dcty, name).run()
            else:
                Create(self.dcty, name).run()
                self.stop(name)

        while 1:
            prompt = input("TaskMaster $>")    
            p = prompt.split()
            if prompt == "help":
                print(utils.COMMAND_AVAILABLE)
            elif prompt == "status":
                for name in list(TAB_PROCESS):
                    TAB_PROCESS[name]["ret_popen"].poll()
                    TAB_PROCESS[name]["state"] = check_proc(TAB_PROCESS[name]["ret_popen"].returncode) 
                    print(utils.CMD_STATUS.format(
                        name,
                        TAB_PROCESS[name]["pid"],
                        TAB_PROCESS[name]["state"],
                        TAB_PROCESS[name]["command"]
                    ))
            elif prompt.find("stop") != -1:
                name_proc = prompt.replace("stop", "").strip()
                self.stop(name_proc)
            elif prompt.find("restart") != -1:
                name_proc = prompt.replace("restart", "").strip()
                self.stop(name_proc)
                self.start(name_proc)
            elif prompt.find("start") != -1:
                name_proc = prompt.replace("start", "").strip()
                self.start(name_proc)
            elif prompt == "exit":
                for name in list(TAB_PROCESS):
                    self.stop(name)
                print("Exit Succesfully")
                sys.exit(0)
