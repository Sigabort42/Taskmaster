#!/usr/bin/env python3

import string

from datetime import datetime
from time import strftime


class Reporter:
    """Reporter de log"""

    def __init__(self, fd):
        self.fd = fd
        self.t = str.maketrans("\n\t\r\v\f-", "      ")

    def info(self, msg):
        self.fd.write("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - [INFO]    - " + msg + "\n")
    
    def log(self, msg):
        self.fd.write("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - [LOG]     - " + msg + "\n")

    def warning(self, msg):
        self.fd.write("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - [WARNING] - " + msg + " WARNING ❌\n")

    def error(self, msg):
        self.fd.write("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - [ERROR]   - " + msg + " ERROR   🆘\n")

    def fatal(self, msg):
        self.fd.write("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - [FATAL]   - " + msg + " FATAL   ⛔️\n")    

    def success(self, msg):
        self.fd.write("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - [SUCESS]  - " + msg + " DONE    ✅\n")


