#!/usr/bin/env python3

import signal

COMMAND_AVAILABLE = "========================================\n\tcommands available are:\n========================================\n{start [name|all]}\t{stop [name|all]}\n{restart [name|all]}\t{info [name program]}\n{help}\t\t\t{status}\n"

ALREADY_STOPPED = "\n-----------------------------\n{}: Already Stopped\n-----------------------------\n"

STOPPED = "\n-----------------------------\n{}: Stopped\n-----------------------------"

FINISHED = "\n-----------------------------\n{}: Finished\n-----------------------------\n"

STARTING = "\n-----------------------------\nStarting {} {}\n-----------------------------\n"

STARTED = "\n-----------------------------\n{}: Started\n-----------------------------\n"

ALREADY_RUNNING = "\n-----------------------------\n{}: Already Running\n-----------------------------\n"

CMD_STATUS = "\n{} [{}]\t\t\t[{}]\ncommand is [{}]\n"

INFO_PROC = "----------------------------- Informations: {}-----------------------------"


def receive_sig(sig_nb, frame):
    """Fonction qui check le type de retour d'un processus fils"""
    check_proc(sig_nb)

def check_proc(n):
    """Fonction qui return le type de code de retour d'un processus"""
    if n == None:
        return "RUNNING"
    if n == -1:
        return "HUP"
    elif n == -2:
        return "INTERRUPT"
    elif n == -3 or n == 3:
        return "QUIT"
    elif n == -6 or n == 6:
        return "SIGABORT"
    elif n == -9 or n == 9:
        return "STOPPED"
    elif n == -14 or n == 14:
        return "ALARM"
    elif n == -15 or n == 15:
        return "STOPPED"
    elif n > 0:
        return "ERROR: " + str(n)
    return "FINISHED"


def retablir_str(s):
    if s.find("\"") != -1:
        s = s.replace("\"", "")
        s = s.replace("_", " ")
    elif s.find("'") != -1:
        s = s.replace("'", "")
        s = s.replace("_", " ")
    return s


def graceful_stop(name_stop):
    if (name_stop == "HUP"):
        return signal.SIGHUP
    elif (name_stop == "INT"):
        return signal.SIGINT
    elif (name_stop == "QUIT"):
        return signal.SIGQUIT
    elif (name_stop == "ABRT"):
        return signal.SIGABRT
    elif (name_stop == "KILL"):
        return signal.SIGKILL
    elif (name_stop == "ALRM"):
        return signal.SIGALRM
    elif (name_stop == "TERM"):
        return signal.SIGTERM



def check_arg_file(prev_dcty, new_dcty, name_prev):
    if ("command" in prev_dcty[name_prev] and "command" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["command"] == new_dcty[name_prev]["command"]):
            pass
        else:
            return (True)
    else:
        return (True)
    if ("directory" in prev_dcty[name_prev] and "directory" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["directory"] == new_dcty[name_prev]["directory"]):
            pass
        else:
            return (True)
    elif ("directory" not in prev_dcty[name_prev] and "directory" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    if ("umask" in prev_dcty[name_prev] and "umask" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["umask"] == new_dcty[name_prev]["umask"]):
            pass
        else:
            return (True)
    elif ("umask" not in prev_dcty[name_prev] and "umask" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    if ("redirect_stdout" in prev_dcty[name_prev] and "redirect_stdout" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["redirect_stdout"] == new_dcty[name_prev]["redirect_stdout"]):
            pass
        else:
            return (True)
    elif ("redirect_stdout" not in prev_dcty[name_prev] and "redirect_stdout" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    if ("redirect_stderr" in prev_dcty[name_prev] and "redirect_stderr" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["redirect_stderr"] == new_dcty[name_prev]["redirect_stderr"]):
            pass
        else:
            return (True)
    elif ("redirect_stderr" not in prev_dcty[name_prev] and "redirect_stderr" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    if ("stdout_logfile" in prev_dcty[name_prev] and "stdout_logfile" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["stdout_logfile"] == new_dcty[name_prev]["stdout_logfile"]):
            pass
        else:
            return (True)
    elif ("stdout_logfile" not in prev_dcty[name_prev] and "stdout_logfile" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    if ("stderr_logfile" in prev_dcty[name_prev] and "stderr_logfile" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["stderr_logfile"] == new_dcty[name_prev]["stderr_logfile"]):
            pass
        else:
            return (True)
    elif ("stderr_logfile" not in prev_dcty[name_prev] and "stderr_logfile" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    if ("environement" in prev_dcty[name_prev] and "environement" in new_dcty[name_prev]):
        if (prev_dcty[name_prev]["environement"] == new_dcty[name_prev]["environement"]):
            pass
        else:
            return (True)
    elif ("environement" not in prev_dcty[name_prev] and "environement" not in new_dcty[name_prev]):
        pass
    else:
        return (True)
    
    return (False)


def return_data_file(prev_dcty, new_dcty, name_prev, name_data, default_data):
    if name_data in new_dcty[name_prev]:
        return new_dcty[name_prev][name_data]
    elif name_data in prev_dcty[name_prev]:
        return prev_dcty[name_prev][name_data]
    else:
        return default_data



def compare_file_reload(prev_dcty, new_dcty, TAB_PROCESS):
    dcty_change = {}
    name_modify = []
    if prev_dcty != new_dcty:
        for name_new, value_new in new_dcty.items():
            if name_new not in prev_dcty:
                dcty_change[name_new] = new_dcty[name_new]

        for name_prev, value_prev in prev_dcty.items():
            if name_prev in new_dcty:
                if new_dcty[name_prev] == prev_dcty[name_prev]:
                    dcty_change[name_prev] = new_dcty[name_prev]
                else:
                    if check_arg_file(prev_dcty, new_dcty, name_prev) == False:
                        TAB_PROCESS[name_prev]["startsecs"] = return_data_file(prev_dcty, new_dcty, name_prev, "startsecs", "0")
                        TAB_PROCESS[name_prev]["startretries"] = return_data_file(prev_dcty, new_dcty, name_prev, "startretries", "0")
                        TAB_PROCESS[name_prev]["autorestart"] = return_data_file(prev_dcty, new_dcty, name_prev, "autorestart", "0")
                        TAB_PROCESS[name_prev]["exitcodes"] = return_data_file(prev_dcty, new_dcty, name_prev, "exitcodes", "0")
                        TAB_PROCESS[name_prev]["stopsignal"] = return_data_file(prev_dcty, new_dcty, name_prev, "stopsignal", "TERM") 
                        dcty_change[name_prev] = new_dcty[name_prev]
                    else:
                        TAB_PROCESS[name_prev]["ret_popen"].send_signal(signal.SIGTERM)
                        print(STOPPED.format(name_prev))
                        dcty_change[name_prev] = new_dcty[name_prev]
                        name_modify.append(name_prev)
            else:
                print(STOPPED.format(name_prev))
                TAB_PROCESS[name_prev]["ret_popen"].send_signal(signal.SIGTERM)
                del TAB_PROCESS[name_prev]

    return (dcty_change, TAB_PROCESS, name_modify)
