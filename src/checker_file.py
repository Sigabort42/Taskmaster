# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    checker_file.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: elbenkri <elbenkri@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2020/06/30 00:53:11 by elbenkri          #+#    #+#              #
#    Updated: 2020/06/30 00:53:13 by elbenkri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python3

import re



class Checker_file:
    """Classe qui permet de checker un fichier .conf au format yaml et de le formater dans un dictionnaire"""

    def __init__(self, parser, path_file="/etc/taskmaster.conf"):
        self.args = parser.parse_args()
        self.path_file = path_file
        self.config = ""
        
    def __del__(self):
        pass


    def     verify_char_in_str(self, s):
        """Methode qui verifie un char dans une string"""
        re_s = re.compile('(\".*\"|\'.*\')')
        if re_s.search(s):
            s_re = re_s.search(s).group().replace(" ", "_")
            s = s.replace(re_s.search(s).group(), s_re)
        return s

    def     verify_file_conf(self, path_file):
        """Methode qui verifie que le fichier de conf est bien formatté"""
        with open(path_file) as file:
            re_p = re.compile("(\[.*\])")
            re_c = re.compile("(^\w.*)=(.*) ;")
            list_args_file = file.read().splitlines()
            args = []
            name_p = ""
            i = -1
            for arg in list_args_file:
                if (re_p.match(arg)):
                    i = i + 1
                    name_p = re_p.match(arg).group().strip("[").strip("]")
                    args.append({"name": name_p})
                elif (re_c.match(arg)):
                    l_tmp = list(filter(None, re_c.split(arg)))
                    key_c, value_c = l_tmp[0], l_tmp[1]
                    value_c = self.verify_char_in_str(value_c)
                    args[i][key_c] = value_c.strip()
            return (args)



    def create_dcty(self):
        """La méthode sert a crer le dictionnaire des processus a superviser par TaskMaster"""
        dcty = {}
        for conf in self.config:
            if (conf.get("name") and conf.get("command")):
                if (conf.get("numprocs") != None and int(conf.get("numprocs")) > 1):
                    for idx in range(0, int(conf.get("numprocs"))):
                        command = conf["command"].split()
                        if conf.get("process_name")[0] == '%':
                            i = conf.get("name").find(":") + 1
                            dcty[conf.get("name")[i:] + "_" + str(idx)] = conf
                        else:
                            dcty[conf.get("process_name")] = conf
                else:
                    command = conf["command"].split()
                    if conf.get("process_name")[0] == '%':
                        i = conf.get("name").find(":") + 1
                        dcty[conf.get("name")[i:]] = conf
                    else:
                        dcty[conf.get("process_name")] = conf
        return dcty
        
        
    def run(self):
        self.config = self.verify_file_conf(self.path_file)
        return self.create_dcty()
