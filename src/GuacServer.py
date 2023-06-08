
# Test Server for guac runner

# config:
#  HOME
#  SUB_HOME
#  ASSIGNMENT
#  RECIPE

# looks for SUB_HOME/PA3.requests/STUDENT

# triggers ```guac run --name STUDENT --recipe RECIPE```

# then copies STUDENT.grade file to SUB_HOME/PA3.prelim/

# then moves SUB_HOME/PA3.requests/STUDENT to SUB_HOME/PA3.tested/

import sys
import time
import shutil
import os
import datetime
import socket
        
from GuacConfig import *
from GuacInternal import *
from ParseYaml import *
from Util import *

class Server:
    def __init__(self,recipe_file,guac_config):
        self.recipe_file=recipe_file
        self.guac_config=guac_config
        self.submiss_dir=os.path.join(self.guac_config.sub_home,self.guac_config.assignment)
        weights_file,self.to_execute=parse_recipe_yaml(recipe_file)
        self.weights=read_yaml_file(weights_file)

        self.desc=self._desc()
        self._make_dirs()

    def _make_dirs(self):
        dirs=[self._prelim_dir(),self._request_dir(),self._tested_dir()]
        for direc in dirs:
            os.makedirs(direc,exist_ok=True)
            
    def serve(self):
        # copy
        try:
            self._write_server_file()
            self._init_log()
            
            sleeping=False
            while True:
                self._check_current_server()
                
                cur=self._check_for_requests()
                if cur is None:
                    if not sleeping:
                        self._log(f"Sleeping: {datetime.datetime.now()}")
                    time.sleep(10)
                    sleeping=True
                else:
                    sleeping=False
                    self._run(cur)

        except Exception as e:
            print(e)
        finally: # this will handle keyboard interrupts
            self._close_log()
            self._close_server_file()
            sys.exit()

    def _run(self,student):
        # execute tasks
        grade_result = run_student(student,self.recipe_file,self.guac_config,self.weights,self.to_execute)
        self._log(f'{student} {grade_result.dump(verbose=0)}')
        
        # copies student grade file to prelim_dir
        try:
            score_file=get_score_file(self.guac_config.home,self.recipe_file,student)
        except Exception as e: # grading failed for some reason
            print(e)
            
        shutil.copyfile(score_file,os.path.join(self._prelim_dir(),os.path.basename(score_file)))

        # moves request file from request_dir to tested_dir
        shutil.move(os.path.join(self._request_dir(),student),os.path.join(self._tested_dir(),student))

    def _server_file(self):
        return get_server_file(self.guac_config.home)
    
    def _log(self,message):
        print(message)
        write_output(self._log_file(),message+"\n",append=True)
                
    def _check_for_requests(self):
        new_requests=os.listdir(self._request_dir())
        if not new_requests:
            return None
        else:
            return new_requests[0]

    def _desc(self):
        
        start_time=str(datetime.datetime.now())
        host_name=socket.gethostname()
        pid=os.getpid()
        
        desc={"Start_Time":start_time,"Host_Name":host_name,"Recipe_File":self.recipe_file,"PID":pid}
        
        return desc

    def _log_file(self):
        return os.path.join(self.submiss_dir,"GuacServer.log")

    def _init_log(self):
        write_output(self._log_file(),yaml.dump(self.desc,sort_keys=False))

    def _close_log(self):
        write_output(self._log_file(),f"End_Time: {datetime.datetime.now()}\n",append=True)
        
    def _check_current_server(self):
        try:
            desc=read_yaml_file(self._server_file())
        except Exception as e:
            print(e)
            exit(1)
            
        if desc!=self.desc:
            print("Server file does not match my description, exiting")
            exit(1)
            
    def _write_server_file(self):
        write_output(get_server_file(self.guac_config.home),yaml.dump(self.desc,sort_keys=False))

    def _close_server_file(self):
        server_file=get_server_file(self.guac_config.home)
        write_output(server_file,f"Ended: {datetime.datetime.now()}\n",append=True)
        shutil.move(server_file,os.path.join(self.guac_config.home,".last_server"))
    
    def _request_dir(self):
        return os.path.join(self.submiss_dir,f"{self.guac_config.assignment}.requests")

    def _tested_dir(self):
        return os.path.join(self.submiss_dir,f"{self.guac_config.assignment}.tested")

    def _prelim_dir(self):
        return os.path.join(self.submiss_dir,f"{self.guac_config.assignment}.prelim")
        
