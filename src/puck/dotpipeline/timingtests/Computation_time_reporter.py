#Written by David Harris-Birtill
#written on 15/04/2020
#
#Automatically create some of the computation time lite template for reporting time
#note that this automates most of the variables, some information still needs to be edited
#these editing points are left as [] in the text.
#If the variable pro is set to true, includes the pro template, but as all of these are dependant
#on the timed program itself, their variables are left as [] in the text for the user to fill in.
#
#See the generated output in "Computation_time_text.txt"
#
#Run this by running the command: 
#python Computation_time_reporter.py
#
#Thanks to Abdou Rockikz for the get_size function below and suggestions for where to get system info from.

import psutil
import platform
from datetime import datetime
import sys
from datetime import date

#get_size function below by Abdou Rockikz from: https://www.thepythoncode.com/article/get-hardware-system-information-python
#date accessed 15/04/2020
def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

uname = platform.uname()
cpufreq = psutil.cpu_freq()
svmem = psutil.virtual_memory()

today = date.today()
todaysDate = today.strftime("%d %B %Y")

def TimeOutput(total = 0, pro=False,):

    print("Computation time:")
    print((f"This program was tested on the {todaysDate} on a computer with a {uname.processor} processor "
           f"with a maximum clock frequency of {str(cpufreq.max)} MHz with {str(psutil.cpu_count(logical=False))} physical cores, "
           f"{str(psutil.cpu_count(logical=True))} logical cores and {get_size(svmem.total)} of RAM using the Operating System {uname.system} {uname.version}. " 
           f"With this hardware and software combination the response time (time taken from start to end of process)"
           f"for this program took {total} nanoseconds to complete. \n"))
    if pro:
        print(("This program can be downloaded with a [insert licence type: preferably an easy to share open source licence11] license "
               "from [insert link to where code can be downloaded from, e.g. GitHub12]."
               "The computation time was measured using function [insert name of timing function] with the programming language [insert programming language]. "
               "The majority of the computation time is spent in [insert name of the part of the code which is computationally expensive], "
               f"which on testing took [insert percentage of the computation time spent in that part of the code]% of the time to run. "
               "Methods [insert names of parallisable methods] can [completely/mostly/partially] be run using parallel processing, " 
               "while methods [insert series methods] need to be run in series. "
               "The current implementation uses [CPU hyperthreading/GPU acceleration/other type of acceleration] for [insert methods]. "
               "It is anticipated that further optimisation could be achieved in [insert names of methods], "
               "possibly using [insert names of techniques/algorithms to further optimise]; however, this has not yet been investigated. \n"))

    print("This text was generated using the open source code and text template in:")
    print(('D Harris-Birtill and R Harris-Birtill, "Understanding computation time: A critical discussion of time as a computational performance metric", '
   'Time in Variance (The Study of Time XVII), Brill. \n'))
   
# TimeOutput()

# #MAKE IT SAVE THE TEXT TO A TEXT FILE
# orig_stdout = sys.stdout
# file_out = open(f'.results/Computation_time_text.txt', 'w')
# sys.stdout = file_out

# TimeOutput()

# sys.stdout = orig_stdout
# file_out.close()

