#!/usr/bin/env python3

import json
import signal
import os
import sys
import termios
import curses
import subprocess
import asyncio
import time
import _thread

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
        
class   Create():
    """Classe qui permet de creer des tasks"""

    def __init__(self, dcty, name, name_i):
        self.dcty = dcty
        self.name = name
        self.name_i = name_i
        self.command = list(map(utils.retablir_str, dcty[name]["command"].split()))
        self.args = " ".join(dcty[name]["command"].split()[1:])

    def verif_time(self, name):
        time.sleep(int(TAB_PROCESS[name]["stopwaitsecs"]))
        TAB_PROCESS[name]["ret_popen"].poll()
        TAB_PROCESS[name]["state"] = "RUNNING" if TAB_PROCESS[name]["ret_popen"].returncode == None else "ERROR: Exited too quickly (process log may have details)"

    async def start_process(self):
        umask = os.umask(TAB_PROCESS[self.name_i]["umask"])
        os.chdir(TAB_PROCESS[self.name_i]["directory"])
        with open(TAB_PROCESS[self.name_i]["stdout"], "a") as fout:
            with open(TAB_PROCESS[self.name_i]["stderr"], "a") as ferr:
                out = subprocess.Popen(
                    args=self.command,
                    cwd=TAB_PROCESS[self.name_i]["directory"],
                    env=TAB_PROCESS[self.name_i]["environment"],
                    stdout=fout,
                    stderr=ferr,
                )
                TAB_PROCESS[self.name_i]["ret_popen"] = out
                TAB_PROCESS[self.name_i]["pid"] = out.pid
                print(utils.STARTING.format(self.name_i))
                TAB_PROCESS[self.name_i]["ret_popen"].poll()                
                TAB_PROCESS[self.name_i]["state"] = "RUNNING"
        os.umask(umask)
        _thread.start_new_thread(self.verif_time, (self.name_i, ))
        
        
    def fork_prog(self):
        """La methode sert a  executer et recuperer les informations d'un processus enfant"""
        TAB_PROCESS[self.name_i] = {
            "autostart":      self.dcty[self.name]["autostart"] if "autostart"
            in self.dcty[self.name] else "",
            "autorestart":      self.dcty[self.name]["autorestart"] if "autorestart"
            in self.dcty[self.name] else "",
            "command":          " ".join(self.command),
            "directory":        self.dcty[self.name]["directory"] if "directory"
            in self.dcty[self.name] else "./",
            "environment":      json.loads("{" + self.dcty[self.name]["environment"] + "}") if "environment"
            in self.dcty[self.name] else None,
            "exitcodes":        self.dcty[self.name]["exitcodes"] if "exitcodes"
            in self.dcty[self.name] else "",
            "name":             self.name if self.name is not None else "",
            "numprocs":         self.dcty[self.name]["numprocs"] if "numprocs"
            in self.dcty[self.name] else "1",
            "pid":              "",
            "ret_popen":        "",
            "redirect_stdout":  self.dcty[self.name]["redirect_stdout"] if "redirect_stdout"
            in self.dcty[self.name] else "true",
            "redirect_stderr":  self.dcty[self.name]["redirect_stderr"] if "redirect_stderr"
            in self.dcty[self.name] else "true",
            "startretries":           self.dcty[self.name]["startretries"] if "startretries"
            in self.dcty[self.name] else "0",
            "state":             "STARTING",
            "stdout":           self.dcty[self.name]["stdout_logfile"] if "stdout_logfile"
            in self.dcty[self.name] else "/dev/fd/1",
            "stderr":           self.dcty[self.name]["stderr_logfile"] if "stderr_logfile"
            in self.dcty[self.name] else "/dev/fd/2",
            "stopsignal":       self.dcty[self.name]["stopsignal"] if "stopsignal"
            in self.dcty[self.name] else "TERM",
            "stopwaitsecs":     self.dcty[self.name]["stopwaitsecs"] if "stopwaitsecs"
            in self.dcty[self.name] else "0",
            "umask":            int(self.dcty[self.name]["umask"]) if "umask"
            in self.dcty[self.name] else 22,
        }
        if (TAB_PROCESS[self.name_i]["redirect_stdout"] == "false"):
            TAB_PROCESS[self.name_i]["stdout"] = "/dev/null"
        if (TAB_PROCESS[self.name_i]["redirect_stderr"] == "false"):
            TAB_PROCESS[self.name_i]["stderr"] = "/dev/null"
        asyncio.run(self.start_process())
        
    def run(self):
        self.fork_prog()


class   Manage:
    """Manager de Task"""

    def __init__(self, dcty):
        self.dcty = dcty
        self.handler_sig()


    def handler_sig(self):
        signal.signal(signal.SIGHUP, receive_sig)
        signal.signal(signal.SIGINT, self.receive_sigT)
        signal.signal(signal.SIGQUIT, self.receive_sigT)
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
        signal.signal(signal.SIGTERM, self.receive_sigT)

    def receive_sigT(self, sig_nb, frame):
        print("sigtttt is {}".format(sig_nb))
        for name in list(TAB_PROCESS):
            self.stop(name)
        print("Exit Succesfully")
        sys.exit(0)

    def stop(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    print(utils.ALREADY_STOPPED.format(name))
                elif TAB_PROCESS[name]["state"] == "FINISHED":
                    print(utils.FINISHED.format(name_proc))
                else:
                    pid = TAB_PROCESS[name]["pid"]
                    os.kill(int(pid), utils.graceful_stop(TAB_PROCESS[name]["stopsignal"]))
                    TAB_PROCESS[name]["state"] = "STOPPED"
                    print(utils.STOPPED.format(name))
                TAB_PROCESS[name]["ret_popen"].poll()
        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "RUNNING":
                pid = TAB_PROCESS[name_proc]["pid"]
                os.kill(int(pid), utils.graceful_stop(TAB_PROCESS[name_proc]["stopsignal"]))
                TAB_PROCESS[name_proc]["state"] = "STOPPED"
                print(utils.STOPPED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "FINISHED":
                print(utils.FINISHED.format(name_proc))
            else:
                print(utils.ALREADY_STOPPED.format(name_proc))
            TAB_PROCESS[name_proc]["ret_popen"].poll()
                    
    def start(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    print(utils.STARTED.format(name))
                    Create(self.dcty, name, name).run()
                elif TAB_PROCESS[name]["state"] == "FINISHED":
                    print(utils.FINISHED.format(name_proc))
                    Create(self.dcty, name, name).run()
                elif TAB_PROCESS[name]["state"] == "RUNNING":
                    print(utils.ALREADY_RUNNING.format(name))
                else:
                    Create(self.dcty, name_proc, name_proc).run()
                    print(utils.STARTED.format(name_proc))

        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "STOPPED":
                Create(self.dcty, name_proc, name_proc).run()
                print(utils.STARTED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "FINISHED":
                print(utils.FINISHED.format(name_proc))
                Create(self.dcty, name_proc, name_proc).run()
                print(utils.STARTED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "RUNNING":
                print(utils.ALREADY_RUNNING.format(name_proc))
            else:
                Create(self.dcty, name_proc, name_proc).run()
                print(utils.STARTED.format(name_proc))

    def run(self):
        for name in self.dcty:
            if ("autostart" in self.dcty[name] and
                self.dcty[name]["autostart"] == "true"):
                if ("numprocs" in self.dcty[name] and
                    int(self.dcty[name]["numprocs"]) > 1):
                    for i in range(0, int(self.dcty[name]["numprocs"])):
                        Create(self.dcty, name, name + "_" + str(i)).run()
                else:
                    Create(self.dcty, name, name).run()
            else:
                Create(self.dcty, name, name).run()
                self.stop(name)

        while 1:
            prompt = input("TaskMaster $>")    
            p = prompt.split()
            if prompt == "help" or prompt == "?":
                print(utils.COMMAND_AVAILABLE)
            elif prompt == "status":
                for name in list(TAB_PROCESS):
                    TAB_PROCESS[name]["ret_popen"].poll()
                    if "Exited" not in TAB_PROCESS[name]["state"] and "FINISHED" not in TAB_PROCESS[name]["state"]:
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
