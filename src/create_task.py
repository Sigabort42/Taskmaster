#!/usr/bin/env python3

import json
import os
import subprocess


from src import utils


TAB_PROCESS = {}



class   Create():
    """Classe qui permet de creer des tasks"""

    def __init__(self, dcty, name, i_retries=0):
        self.dcty = dcty
        self.name = name
        self.i_retries = i_retries
        self.command = list(map(utils.retablir_str, dcty[name]["command"].split()))
        self.args = " ".join(dcty[name]["command"].split()[1:])

    def verif_time(self, name):
        """Methode qui verifie si un processus est toujours lancer apres un temps donné"""
        time.sleep(int(TAB_PROCESS[name]["startsecs"]))
        TAB_PROCESS[name]["ret_popen"].poll()
        TAB_PROCESS[name]["returncode"] = TAB_PROCESS[name]["ret_popen"].returncode
        TAB_PROCESS[name]["state"] = "RUNNING" if TAB_PROCESS[name]["ret_popen"].returncode == None else "ERROR: Exited too quickly (process log may have details)"

    def start_process(self):
        """Methode qui lance un processus enfant avec ses parametres"""
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
                TAB_PROCESS[self.name]["returncode"] = TAB_PROCESS[self.name]["ret_popen"].returncode
                TAB_PROCESS[self.name]["state"] = "RUNNING"
        os.umask(umask)


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
            "environment":      json.loads("{" + self.dcty[self.name]["environment"] + "}") if "environment" in self.dcty[self.name] else None,
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
            "returncode":       "0",
            "startretries":           self.dcty[self.name]["startretries"] if "startretries"
            in self.dcty[self.name] else "0",
            "i_retries":        self.i_retries,
            "startsecs":           self.dcty[self.name]["startsecs"] if "startsecs"
            in self.dcty[self.name] else "0",
            "state":             "STARTING",
            "stdout":           self.dcty[self.name]["stdout_logfile"] if "stdout_logfile"
            in self.dcty[self.name] else "/dev/null",
            "stderr":           self.dcty[self.name]["stderr_logfile"] if "stderr_logfile"
            in self.dcty[self.name] else "/dev/null",
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
        self.start_process()

    def run(self):
        self.fork_prog()
