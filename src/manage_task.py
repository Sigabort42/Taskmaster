#!/usr/bin/env python3

import smtplib
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
import re

from src import utils
from src import checker_file


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

    def __init__(self, dcty, name):
        self.dcty = dcty
        self.name = name
        self.command = list(map(utils.retablir_str, dcty[name]["command"].split()))
        self.args = " ".join(dcty[name]["command"].split()[1:])

    def verif_time(self, name):
        time.sleep(int(TAB_PROCESS[name]["startsecs"]))
        TAB_PROCESS[name]["ret_popen"].poll()
        TAB_PROCESS[name]["state"] = "RUNNING" if TAB_PROCESS[name]["ret_popen"].returncode == None else "ERROR: Exited too quickly (process log may have details)"

    async def start_process(self):
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
#                print(utils.STARTING.format(self.name, out.pid))
                TAB_PROCESS[self.name]["ret_popen"].poll()                
                TAB_PROCESS[self.name]["state"] = "RUNNING"
        os.umask(umask)
        _thread.start_new_thread(self.verif_time, (self.name, ))
        
    def fork_prog(self):
        """La methode sert a  executer et recuperer les informations d'un processus enfant"""
        TAB_PROCESS[self.name] = {
            "autostart":      self.dcty[self.name]["autostart"] if "autostart"
            in self.dcty[self.name] else "",
            "autorestart":      self.dcty[self.name]["autorestart"] if "autorestart"
            in self.dcty[self.name] else "never",
            "command":          " ".join(self.command),
            "directory":        self.dcty[self.name]["directory"] if "directory"
            in self.dcty[self.name] else "./",
            "environment":      json.loads("{" + self.dcty[self.name]["environment"] + "}") if "environment"
            in self.dcty[self.name] else None,
            "exitcodes":        self.dcty[self.name]["exitcodes"] if "exitcodes"
            in self.dcty[self.name] else "0",
            "mail_report":      self.dcty[self.name]["mail_report"] if "mail_report"
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
            "startsecs":           self.dcty[self.name]["startsecs"] if "startsecs"
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
        if (TAB_PROCESS[self.name]["redirect_stdout"] == "false"):
            TAB_PROCESS[self.name]["stdout"] = "/dev/null"
        if (TAB_PROCESS[self.name]["redirect_stderr"] == "false"):
            TAB_PROCESS[self.name]["stderr"] = "/dev/null"
        asyncio.run(self.start_process())
        
    def run(self):
        self.fork_prog()

        
class   Manage:
    """Manager de Task"""

    def __init__(self, dcty, parser, path_file):
        self.dcty = dcty
        self.parser = parser
        self.checker_file = checker_file.Checker_file(parser, path_file)
        self.path_file = path_file
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

    def time_sleep_graceful_stop(self, pid, name):
        time.sleep(int(TAB_PROCESS[name]["stopwaitsecs"]))
        TAB_PROCESS[name]["ret_popen"].poll()
        if (TAB_PROCESS[name]["ret_popen"].returncode == None):
            os.kill(int(pid), utils.graceful_stop(TAB_PROCESS[name]["stopsignal"]))            
        TAB_PROCESS[name]["state"] = "STOPPED"
        print(utils.STOPPED.format(name))

    def restart_proc_unexpected(self, name):
        i = 0
        re_email = re.compile("([^@]+@[^@]+\.[^@]+)")
        while (1):
            TAB_PROCESS[name]["ret_popen"].poll()
            n = check_proc(TAB_PROCESS[name]["ret_popen"].returncode)
            if (n != "RUNNING" and
                (TAB_PROCESS[name]["autorestart"] == "always" or TAB_PROCESS[name]["autorestart"] == "unexpected")):
                if (TAB_PROCESS[name]["autorestart"] == "unexpected" and
                    i < int(TAB_PROCESS[name]["startretries"])):
                    if (TAB_PROCESS[name]["exitcodes"] != str(TAB_PROCESS[name]["ret_popen"].returncode)):
                        time.sleep(2)
                        i += 1
                        Create(self.dcty, name).run()
                elif (TAB_PROCESS[name]["autorestart"] == "unexpected" and
                      i == int(TAB_PROCESS[name]["startretries"]) and
                      "mail_report" in TAB_PROCESS[name] and
                      re_email.match(TAB_PROCESS[name]["mail_report"])):
                    i += 1
                    dest = TAB_PROCESS[name]["mail_report"]
                    serveur = smtplib.SMTP('smtp.gmail.com', 587)
                    serveur.ehlo()
                    serveur.starttls()
                    serveur.ehlo()
                    serveur.login("allinplans@gmail.com", "Okokokok8")
                    message = "Le programme {} sous le pid {} a ete arrete".format(
                        name,
                        TAB_PROCESS[name]["pid"])
                    serveur.sendmail("allinplans@gmail.com", dest, message)
                    serveur.quit()

                elif TAB_PROCESS[name]["autorestart"] == "always":
                    time.sleep(2)
                    Create(self.dcty, name).run()
        
    def stop(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    print(utils.ALREADY_STOPPED.format(name))
                elif TAB_PROCESS[name]["state"] == "FINISHED":
                    print(utils.FINISHED.format(name_proc))
                else:
                    pid = TAB_PROCESS[name]["pid"]
                    if ("RUNNING" in TAB_PROCESS[name]["state"]):
                        _thread.start_new_thread(self.time_sleep_graceful_stop, (pid, name, ))
                TAB_PROCESS[name]["ret_popen"].poll()
        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "RUNNING":
                pid = TAB_PROCESS[name_proc]["pid"]
                if ("RUNNING" in TAB_PROCESS[name_proc]["state"]):
                    _thread.start_new_thread(self.time_sleep_graceful_stop, (pid, name_proc, ))
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
                    Create(self.dcty, name).run()
                    _thread.start_new_thread(self.restart_proc_unexpected, (name, ))
                elif TAB_PROCESS[name]["state"] == "FINISHED":
                    print(utils.FINISHED.format(name_proc))
                    Create(self.dcty, name).run()
                    _thread.start_new_thread(self.restart_proc_unexpected, (name, ))
                elif TAB_PROCESS[name]["state"] == "RUNNING":
                    print(utils.ALREADY_RUNNING.format(name))
                else:
                    Create(self.dcty, name).run()
                    _thread.start_new_thread(self.restart_proc_unexpected, (name, ))
                    print(utils.STARTED.format(name_proc))

        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "STOPPED":
                Create(self.dcty, name_proc).run()
                _thread.start_new_thread(self.restart_proc_unexpected, (name_proc, ))
                print(utils.STARTED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "FINISHED":
                print(utils.FINISHED.format(name_proc))
                Create(self.dcty, name_proc).run()
                _thread.start_new_thread(self.restart_proc_unexpected, (name_proc, ))
                print(utils.STARTED.format(name_proc))
            elif TAB_PROCESS[name_proc]["state"] == "RUNNING":
                print(utils.ALREADY_RUNNING.format(name_proc))
            else:
                Create(self.dcty, name_proc).run()
                _thread.start_new_thread(self.restart_proc_unexpected, (name_proc, ))
                print(utils.STARTED.format(name_proc))

    def run(self):
        global TAB_PROCESS
        for name in self.dcty:
            if ("autostart" in self.dcty[name] and
                self.dcty[name]["autostart"] == "true"):
                Create(self.dcty, name).run()
                _thread.start_new_thread(self.restart_proc_unexpected, (name, ))
            else:
                Create(self.dcty, name).run()
                _thread.start_new_thread(self.restart_proc_unexpected, (name, ))
                self.stop(name)
            TAB_PROCESS[name]["ret_popen"].poll()

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
                secs = TAB_PROCESS[name_proc]["stopwaitsecs"]
                TAB_PROCESS[name_proc]["stopwaitsecs"] = "0"
                time.sleep(0.5)
                self.stop(name_proc)
                self.start(name_proc)
                TAB_PROCESS[name_proc]["stopwaitsecs"] = secs
                
            elif prompt.find("start") != -1:
                name_proc = prompt.replace("start", "").strip()
                self.start(name_proc)
                
            elif prompt.find("reload") != -1:
                self.dcty, TAB_PROCESS, name_modify = utils.compare_file_reload(self.dcty, self.checker_file.run(), TAB_PROCESS)
                for name in self.dcty:
                    if name not in list(TAB_PROCESS) or name in name_modify:
                        Create(self.dcty, name).run()
                        
            elif prompt.find("info") != -1:
                name_proc = prompt.replace("info", "").strip()
                if name_proc in list(TAB_PROCESS):
                    print(utils.INFO_PROC.format(name_proc))
                    for k, v in TAB_PROCESS[name_proc].items():
                        if k != "ret_popen":
                            print("{}={}".format(k, v))

            elif prompt == "exit":
                for name in list(TAB_PROCESS):
                    TAB_PROCESS[name]["stopwaitsecs"] = "0"
                    self.stop(name)
                time.sleep(1)
                print("Exit Succesfully")
                sys.exit(0)
