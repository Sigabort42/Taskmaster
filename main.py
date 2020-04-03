#!/usr/bin/env python3

import argparse
import json
import re
from src import taskmaster

def verify_file_conf(path_file):
    with open(path_file) as file:
        re_p = re.compile("(\[\w*\])")
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
                args[i][key_c] = value_c.strip()
        return (args)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="taskmaster",
        description="Superviser des programmes",
        epilog="Programme servant à superviser les porgrammes donnée"
    )
    parser.add_argument(
        "-c",
        default="/etc/taskmaster.conf",
        help="path file of [taskmaster.conf] by default is %(default)s",
        metavar=""
    )
    args = parser.parse_args()
    print("icicicii {}".format(args.c))
    conf = verify_file_conf(args.c)
    print(conf)
    obj = taskmaster.Taskmaster(conf)
    obj.launch()
