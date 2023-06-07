
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

from GuacConfig import *
from GuacInternal import *
from ParseYaml import *


class Server:
    def __init__(self,recipe_file,guac_config):
        self.recipe_file=recipe_file
        self.guac_config=guac_config
        self.submiss_dir=os.path.join(self.guac_config.sub_home,self.guac_config.assignment)
        weights_file,self.to_execute=parse_recipe_yaml(recipe_file)
        self.weights=read_yaml_file(weights_file)

        self._make_dirs()

    def _make_dirs(self):
        dirs=[self._prelim_dir(),self._request_dir(),self._tested_dir()]
        for direc in dirs:
            os.makedirs(direc,exist_ok=True)
            
    def serve(self):
        # copy
        try:
            self._write_server_file()
        
            while True:
                cur=self._check_for_requests()
                if cur is None:
                    print("Sleeping")
                    time.sleep(5)
                else:
                    self._run(cur)

        except Exception as e:
            print(e)
        finally: # this will handle keyboard interrupts
            self._remove_server_file()
            sys.exit()

    def _run(self,cur):
        # execute tasks
        grade_result = run_student(cur,self.recipe_file,self.guac_config,self.weights,self.to_execute)
        print(f'{student} {grade_result.dump(verbose=0)}')
        
        # copies student grade file to prelim_dir
        score_file=get_score_file(self.recipe_file,cur)
        shutil.copyfile(score_file,os.path.join(self._prelim_dir(),os.path.basename(score_file)))

        # moves request file from request_dir to tested_dir
        shutil.move(os.path.join(self._request_dir(),cur),os.path.join(self._tested_dir(),cur))

    def _check_for_requests(self):
        new_requests=os.listdir(self._request_dir())
        if not new_requests:
            return None
        else:
            return new_requests[0]

    def _write_server_file(self):
        import datetime
        import socket
        
        start_time=str(datetime.datetime.now())
        host_name=socket.gethostname()
        
        desc={"Server":{"Start Time":start_time,"Host Name":host_name,"Recipe File":self.recipe_file}}
        output=yaml.dump(desc)
        
        write_output(get_server_file(self.guac_config.home),output)

    def _remove_server_file(self):
        server_file=get_server_file(self.guac_config.home)
        shutil.move(server_file,os.path.join(self.guac_config.home,".last_server"))

    def _request_dir(self):
        return os.path.join(self.submiss_dir,f"{self.guac_config.assignment}.requests")

    def _tested_dir(self):
        return os.path.join(self.submiss_dir,f"{self.guac_config.assignment}.tested")

    def _prelim_dir(self):
        return os.path.join(self.submiss_dir,f"{self.guac_config.assignment}.prelim")
        
