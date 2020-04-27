#!/usr/bin/env python3

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
            "stdout":           self.dcty[self.name]["stdout_logfile"] if "stdout_logfile"
            in self.dcty[self.name] else "/dev/fd/1",
            "stderr":           self.dcty[self.name]["stderr_logfile"] if "stderr_logfile"
            in self.dcty[self.name] else "/dev/fd/2",
        }
        asyncio.run(self.write_fd())
        
    def run(self):
        print("run Task")
        self.fork_prog()


class   Manage:
    """Manager de Task"""

    def __init__(self, dcty):
        self.dcty = dcty

    def run(self):
        for name in self.dcty:
            Create(self.dcty, name).run()

        while 1:
            prompt = input("TaskMaster $>")
            p = prompt.split()
            if prompt == "status":
                for name in list(TAB_PROCESS):
                    TAB_PROCESS[name]["ret_popen"].poll()
                    if TAB_PROCESS[name]["ret_popen"].returncode == None:
                        print(
                            "\nname of program: {}\npid is: [{}]\ncommand is [{}]\nEtat is [{}]\n".
                            format(
                                name,
                                TAB_PROCESS[name]["pid"],
                                TAB_PROCESS[name]["command"],
                                "Running"
                            ))
                    else:
                        del TAB_PROCESS[name]

#                print("TAB IS {}".format(TAB_PROCESS))
