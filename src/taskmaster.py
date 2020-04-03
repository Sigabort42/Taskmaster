#!/usr/bin/env python3

import os

class           Taskmaster:
    def __init__(self, config=None):
        self.config = config

    def __del__(self):
        print("del TaskMaster")

    def forkProg(self, command, args=None):
        pid = os.fork()
        lol = "ssq"
        if (pid):
            print("child is {}".format(pid))
            
        else:
            print("not child is {}".format(pid))
            lol = os.execv(command, args)
        print("sqdqsdqsd {}".format(lol))

    def launch(self):
        for conf in self.config:
            print(conf.get("command"))
            if (conf.get("command")):
                command = conf["command"].split()
                self.forkProg(command[0], command)
