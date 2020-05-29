#!/usr/bin/env python3

import argparse

from src import taskmaster
from src import checker_file

PARSER = argparse.ArgumentParser(
    prog="taskmaster",
    description="Superviser des programmes",
    epilog="Programme servant à superviser les porgrammes donnée"
)
PARSER.add_argument(
    "-c",
    default="/etc/taskmaster.conf",
    help="path file of [taskmaster.conf] by default is %(default)s",
    metavar=""
)

if __name__ == "__main__":

    conf = checker_file.Checker_file(PARSER).run()
#    print("conf {}".format(conf))
    TM = taskmaster.Taskmaster(conf)
    TM.launch()
