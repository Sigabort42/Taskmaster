#!/usr/bin/env python3

import os
from src import manage_task

class           Taskmaster:
    def __init__(self, config=None):
        self.config = config

    def __del__(self):
        print("del TaskMaster")

    def fork_all_prog(self, dcty):
        """La methode sert a fork tout les processus enfant du fichier de conf"""
        
        for name in dcty:
            print("name {}:{}".format(name, dcty[name][1]))
        
    def create_dcty(self):
        """La méthode sert a crer le dictionnaire des processus a superviser par TaskMaster"""
        dcty = {}
        for conf in self.config:
            if (conf.get("name") and conf.get("command")):
                command = conf["command"].split()
                if conf.get("process_name")[0] == '%':
                    i = conf.get("name").find(":") + 1
                    dcty[conf.get("name")[i:]] = conf
                else:
                    dcty[conf.get("process_name")] = conf
        return dcty
        
    def launch(self):
        dcty = self.create_dcty()
#        print("dcty == {}".format(dcty))
        manage_task.Manage(dcty).run()
