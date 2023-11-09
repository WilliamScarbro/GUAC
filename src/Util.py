import os
import re
import subprocess
import tarfile
import yaml
from colorama import Fore,Style
from pathlib import Path

from avocado.utils import archive, build, process
from avocado import Test

class GuacTest(Test):
    def _safe_param(self,name):
        var = self.params.get(name,default=None)
        if not var:
            raise Exception(f"Configuration variable '{name}' undefined")
        return var
    def _guac_handler(self,test):
        """
        :param LIST
        """
        listing=self._safe_param("LIST")=="True"
        if listing:
            return
        test()

    @staticmethod
    def desc_order():
        return ["Description","COMMAND"]
    
    def _write_whiteboard_yaml(self,test_desc):
        #self.whiteboard=""
        self.whiteboard+=yaml.safe_dump(test_desc,sort_keys=False)
        #order=self.desc_order()
        #for var in order:
        #    if not var in test_desc:
        #        continue
        #    #self.whiteboard+=f"{var}: {test_desc[var]}\n"
        #    self.whiteboard+=yaml.dump({var:test_desc[var]})
        #    del test_desc[var]
        #
        #for key,value in test_desc.items():
        #    #self.whiteboard+=f"{key}: {value}\n"
        #    self.whiteboard+=yaml.dump({key:value})
        self.log.debug(self.whiteboard)

class Score:
    def __init__(self,score,total):
        self.score=score
        self.total=total
    @staticmethod
    def fromString(string):
        str0,str1=string.split('/')
        score=int(str0)
        total=int(str1)
        return Score(score,total)
    def __add__(self,other):
        if not isinstance(other,Score):
            raise ValueError("{other} is not instance of Score")
        return Score(self.score+other.score,self.total+other.total)
    def __str__(self):
        return f"{self.score} / {self.total}"
            
def safe_read(file_path):
    if not os.path.isfile(file_path):
        raise Exception(f"Missing {file_path}")
    f=open(file_path,"r")
    out = f.read()
    f.close()
    return out



def parse_for_regex(text,regex):
    regex_replaced=regex.replace('\\\\','\\')
    match = re.search(regex_replaced, text)
    if match:
        return match.group(0)
    raise ValueError(f"Cannot match '{regex_replaced}' against: '{text}'")

def parse_for_regex_group(text,regex):
    regex_replaced=regex.replace('\\\\','\\')
    match = re.search(regex_replaced, text)
    if match:
        return match.group(1)
    raise ValueError(f"Cannot match '{regex_replaced}' against: '{text}'")

def parse_for_regex_set(text,regex):
    regex_replaced=regex.replace('\\\\','\\')
    matched=re.findall(regex_replaced,text)
    return "\n".join(matched)

def write_output(file_name,output,append=False):
    #self.log.debug(f"writing to {file_name}")
    file_name=open(file_name,"w" if not append else 'a')
    file_name.write(output)
    file_name.close

def yaml_file_append(dest,src,src_is_data=False):
    if not src_is_data:
        src_handle=open(src,"r")
        src_data=src_handle.read()
        src_handle.close()
        src_desc=src
    else:
        src_data=src
        src_desc="appended"
        
    dest_handle=open(dest,"a")
    dest_handle.write(f"\n\n####### Start of {src_desc} #######\n\n")
    dest_handle.write(src_data)
    dest_handle.write(f"\n\n###### End of {src_desc} ######\n\n")
    dest_handle.close()
import subprocess

# Avocado has its own default timeout per task (120s)
# timeout here is just in case
def run_command(cwd, cmd, env=None, timeout=1000):
    try:
        # Execute the command
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,cwd=cwd)

        # Wait for the process to complete or timeout
        stdout, stderr = process.communicate(timeout=timeout)

        # Get the exit code
        exit_code = process.returncode

        # Decode stdout and stderr
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')

        return exit_code, stdout, stderr

    except subprocess.TimeoutExpired:
        # Process timed out
        process.kill()
        return -1, '', 'Timeout expired'

    except Exception as e:
        # Other exceptions
        return -1, '', str(e)
    

# collor should be Fore.{Color}, this function automatically escapes color
def color(color,text):
    return color+text+Style.RESET_ALL
                
def list_to_yaml_str(vals):
    res=""
    for val in vals:
        res+=f"\n - {val}"
    return res

def check_dir_contains(test,direc,contents):
    for file_name in contents:
        file_path=os.path.join(direc,file_name)
        test.log.debug(f"checking {file_name} exists")
        if not os.path.isfile(file_path):
            test.fail(f"Missing file {file_name}")
             
 
def check_not_contains(test,direc,contents):
    for file_name in contents:
        file_path=os.path.join(direc,file_name)
        test.log.debug(f"checking {file_name} doesn't exists")
        if os.path.isfile(file_path):
            test.fail(f"File {file_name} should not exist")

def get_master_dir(home,recipe_name):
    rname=os.path.basename(recipe_name).split('.')[0] # remove directories and file type
    return home+"/.master_results/"+rname

def get_work_dir(home):
    return os.path.join(home,".work")

# {sub_home}/{assignment}/{student}/{assignment}.{file_type}
# if FILE_NAME env var is set, match file name
# if FILE_NAME is not matched, or FILE_NAME is not set, use most recent file 
def file_location(sub_home,assignment,student,file_type):

    std_dir=os.path.join(os.path.join(sub_home,assignment),student)
    if not os.path.isdir(std_dir):
        return None,"Missing"
    
    #on_time=os.path.join(std_dir,assignment+"."+file_type)
    #late=os.path.join(std_dir,f"LATE_{assignment}.{file_type}")

    
    files = sorted(Path(std_dir).iterdir(), key=os.path.getmtime)

    if not files:
        return None, "Missing" #raise Exception(f"No submission found for {student}") 

    if "FILE_NAME" in os.environ:
        file_name = os.environ['FILE_NAME']
        cur_file=None
        for path in files:
            if os.path.basename(path) == file_name:
                cur_file = path
                break
        if cur_file is None:
            cur_file = files[-1] #return None, "Missing" #raise Exception(f"Cannot find tar submission named TAR_NAME: 'tar_name'")
    else:
        # get latest file
        cur_file = files[-1]

    
    # specify a deadline other than checkin's
    if "DEADLINE" in os.environ:
        #print("Checking deadline")
        deadline = float(os.environ["DEADLINE"]) # expects epoch
        mtime = os.stat(cur_file).st_mtime
        status = "Late" if mtime > deadline else "OnTime"
    else:
        status = "Late" if "LATE" in os.path.basename(cur_file) else "OnTime"

    # remove later
    if "PREDEADLINE" in os.environ:
        predeadline = float(os.environ["PREDEADLINE"])
        mtime = os.stat(cur_file).st_mtime
        status = "BeforeTime" if mtime < predeadline else status
        
    return str(cur_file),status

def get_score_file(home,recipe_file,name):
    recipe_name=os.path.basename(recipe_file).split('.')[0]

    # $home/.scores/$recipe_name/$name/$name.grade
    score_file=os.path.join(os.path.join(os.path.join(os.path.join(home,".scores"),recipe_name),name),f"{name}.grade")
    
    if not os.path.isfile(score_file):
        raise Exception(f"Missing score file: student '{name}' has not been graded on recipe '{recipe_name}'")
    return score_file

def get_server_file(home):
    return os.path.join(home,".server")

def list_tar_contents(file_path):
    contents=""
    try:
        with tarfile.open(file_path, 'r') as tar:
            for member in tar.getmembers():
                contents+=member.name+"\n"
    except tarfile.TarError:
        print(f"Error: Failed to open or read the tar file '{file_path}'.")
    return contents

def read_file_from_tar(tar_file_path, file_name):
    """
    Read a file from inside a tar file.

    Args:
        tar_file_path (str): Path to the tar file.
        file_name (str): Name of the file to be read.

    Returns:
        str: Content of the file.
    """
    try:
        with tarfile.open(tar_file_path, 'r') as tar:
            # Check if the file exists inside the tar archive
            if file_name in tar.getnames():
                # Extract the file from the tar archive and read its content
                file = tar.extractfile(file_name)
                if file:
                    content = file.read().decode('utf-8')
                    return content
                else:
                    return f"Error: Failed to read file '{file_name}' from the tar archive."
            else:
                return f"Error: File '{file_name}' does not exist in the tar archive."
    except tarfile.TarError as e:
        return f"Error: Failed to open or extract tar file - {str(e)}"

def confirm(action,force):
    if force:
        return
    while True:
        resp=input(f"Confirm to {action} [Y/N]: ")
        if resp=="Y":
            break
        if resp=="N":
            exit()
        print("Please enter 'Y' or 'N'")

