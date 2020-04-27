#!/usr/bin/env python3

import signal
import os
import sys
import os
import subprocess
import asyncio


TAB_PROCESS = {}

class   Create():
    """Classe qui permet de creer des tasks"""

    def __init__(self, dcty, name):
        self.dcty = dcty
        self.name = name
        self.command = list(map(self.retablir_str, dcty[name]["command"].split()))
        self.args = " ".join(dcty[name]["command"].split()[1:])

    def retablir_str(self, s):
        if s.find("\"") != -1:
            s = s.replace("\"", "")
            s = s.replace("_", " ")
        elif s.find("'") != -1:
            s = s.replace("'", "")
            s = s.replace("_", " ")
        return s
        
    async def write_fd(self):
        with open(TAB_PROCESS[self.name]["stdout"], "a") as fout:
            with open(TAB_PROCESS[self.name]["stderr"], "a") as ferr:
                out = subprocess.Popen(self.command, stdout=fout, stderr=ferr)
                TAB_PROCESS[self.name]["ret_popen"] = out
                TAB_PROCESS[self.name]["pid"] = out.pid
                TAB_PROCESS[self.name]["state"] = "RUNNING"
                print("Starting {}".format(self.name))
                
    def fork_prog(self):
        """La methode sert a  executer et recuperer les informations d'un processus enfant"""

        pid = None
        TAB_PROCESS[self.name] = {
            "autorestart":      self.dcty[self.name]["autorestart"] if "autorestart"
            in self.dcty[self.name] else "",
            "command":          " ".join(self.command),
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
        }
        asyncio.run(self.write_fd())
        
    def run(self):
        self.fork_prog()


class   Manage:
    """Manager de Task"""

    def __init__(self, dcty):
        self.dcty = dcty


    def check_proc(self, n):
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

    def stop(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    print(
                        "-----------------------------\n{}: Already Stopped\n-----------------------------".
                        format(name)
                    )
                else:
                    TAB_PROCESS[name]["ret_popen"].terminate()
                    TAB_PROCESS[name]["state"] = "STOPPED"
                    print(
                        "-----------------------------\n{}: Stopped\n-----------------------------".
                        format(name)
                    )
        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "RUNNING":
                TAB_PROCESS[name_proc]["ret_popen"].terminate()
                TAB_PROCESS[name_proc]["state"] = "STOPPED"
                print(
                    "-----------------------------\n{}: Stopped\n-----------------------------".
                    format(name_proc)
                )
            else:
                print(
                    "-----------------------------\n{}: Already Stopped\n-----------------------------".
                    format(name_proc)
                )


                    
    def start(self, name_proc):
        if name_proc == "all":
            for name in list(TAB_PROCESS):
                if TAB_PROCESS[name]["state"] == "STOPPED":
                    Create(self.dcty, name).run()
                    print(
                        "-----------------------------\n{}: Started\n-----------------------------".
                        format(name)
                    )
                else:
                    print(
                        "-----------------------------\n{}: Already Running\n-----------------------------".
                        format(name)
                    )                    
        elif name_proc in TAB_PROCESS:
            if TAB_PROCESS[name_proc]["state"] == "STOPPED":
                Create(self.dcty, name_proc).run()
                print(
                    "-----------------------------\n{}: Started\n-----------------------------".
                    format(name_proc)
                )
            else:
                print(
                    "-----------------------------\n{}: Already Running\n-----------------------------".
                    format(name_proc)
                )
                
    def run(self):
        for name in self.dcty:
            Create(self.dcty, name).run()

        while 1:
            prompt = input("TaskMaster $>")
            p = prompt.split()
            if prompt == "help":
                print("commands available are:\n{start [name|all]}\t{stop [name|all]}\t{restart [name|all]}\n{help}\t{status}\n")
            elif prompt == "status":
                for name in list(TAB_PROCESS):
                    TAB_PROCESS[name]["ret_popen"].poll()
            if prompt == "status":
                for name in list(TAB_PROCESS):
                    TAB_PROCESS[name]["ret_popen"].poll()
                    print(
                        "\nname of program: {}\npid is: [{}]\ncommand is [{}]\nEtat is [{}]\n".
                        format(
                            name,
                            TAB_PROCESS[name]["pid"],
                            TAB_PROCESS[name]["command"],
                            self.check_proc(TAB_PROCESS[name]["ret_popen"].returncode)
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
