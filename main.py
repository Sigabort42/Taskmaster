# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    main.py                                            :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: elbenkri <elbenkri@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2020/06/30 00:52:57 by elbenkri          #+#    #+#              #
#    Updated: 2020/06/30 00:53:00 by elbenkri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python3

import os
import argparse


from src import manage_task
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
    path_file = os.path.abspath(PARSER.parse_args().c)
    conf = checker_file.Checker_file(PARSER, path_file).run()
    manage_task.Manage(conf, PARSER, path_file).run()
