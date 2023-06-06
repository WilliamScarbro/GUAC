#
import argparse
import yaml
import subprocess
import os
import shutil
import json
from colorama import Fore,Style

from ParseYaml import *
from Util import *
from Logger import Logger

from GuacConfig import *


###
# Interface with Avocado

class AvocadoTest:
    def __init__(self,name,status,description="",fail_message="",points=0):
        self.full_name=name
        self.name=self.full_name[:-5] # ignore last 4 digits (hash of config params)
        self.status=status
        self.description=description
        self.fail_message=fail_message
        self.points=points
        self.score=-1

        
    @staticmethod
    def parse_json_dict(json_data):
        return AvocadoTest(json_data["id"],json_data["status"],description=json_data["whiteboard"],fail_message=json_data["fail_reason"])
    
    def __str__(self):
        return f"{self.name} : {self.status} : {self.fail_message} : {self.score} / {self.points}"

    def get_score(self):
        if self.status == "PASS":
            self.score= self.points
        else:
            self.score= 0
        return self.score

    def verbose(self):
        res=self.description
        
        if self.status == "PASS":
            res+="Status: PASS\n"
        else:
            res+=f"Status: {self.status}\n"
            res+=f"Message: {self.fail_message}\n"

        res+=f"Score: {self.score} / {self.points}\n"
        return res
                

# avocado_run_wrapper :: String -> [String] -> RunConfig -> [AvocadoTest]
def avocado_run_wrapper(script,script_config,run_config,logger):

    # parse_result_json :: [AvocadoTest]
    def parse_result_json():
        avo_home = run_config.guac_config.avo_home
        with open(avo_home+"/job-results/latest/results.json","r") as f:
            data = json.load(f)
        return [AvocadoTest.parse_json_dict(test) for test in data["tests"]]

    
    # aggregate config files and RunConfig
    run_config_yaml=run_config.get_run_config_yaml()
    config_dir=run_config.guac_config.home+"/.config/"
    #shutil.rmtree(config_dir,ignore_errors=True)
    os.makedirs(config_dir,exist_ok=True)
    new_config=config_dir+'-'.join(script_config).replace("/","_")
    try:
        os.remove(new_config)
    except OSError:
        pass
    
    for config in script_config:
        logger.log(color(Fore.BLUE,f"Including config: {config}"),verbose=2)
        yaml_file_append(new_config,config)
    yaml_file_append(new_config,run_config_yaml,src_is_data=True)
    
    # execute avocado script
    cmd = f"avocado run {run_config.guac_config.guac_home}/src/{script} --mux-yaml {new_config}  "
    logger.log(color(Fore.BLUE,f"Executing: {cmd}"),verbose=2)
    #try:
    code,out,error = run_command(run_config.guac_config.home,cmd)
    if code==1: # test error
        logger.log(color(Fore.RED,out),verbose=2)
        logger.log(color(Fore.RED,error),verbose=2)
    if code!=2: # avocado does not produce logs in this case
        logs=parse_for_regex_group(out,"JOB LOG\s+:\s+(.*)")
        logger.log(color(Fore.BLUE,f"Logs: {logs}"),verbose=2)
    if code==2: # this is an avocado error, not a test error
        print(color(Fore.RED,error))
    if code!=0 and run_config.is_listing=="True":
        raise Exception("Task failed")
        
    return parse_result_json()

###
# Transform guac actions to avocado
        
# execute :: Task -> RunConfig -> Logger -> AvocadoTest
def execute(task,run_config,logger):
    source=safe_get_var(task,"Source")
    config=safe_get_var(task,"Config")
    if not isinstance(config,list):
        config=[config]
        
    task_results=avocado_run_wrapper(source,config,run_config,logger)
    return task_results
    
# list_tests :: [Task] -> RunConfig -> String
def list_tests_internal(to_execute,run_config):
    results=[]
    logger=Logger(len(to_execute),2)
    
    for task in to_execute:
        results+=execute(task,run_config,logger)
        logger.update()
    logger.close()
    print(color(Fore.GREEN,">>>>>> Begin Test List <<<<<<<"))
    for result in results:
        print(result.name)
    

# run_tasks :: String -> String -> [Task] -> RunConfig -> (Int,Int)
def run_tasks(recipe_file,weights,to_execute,run_config,verbose=0):

    logger=Logger(len(to_execute),verbose)
    
    # clear .work
    work_dir=get_work_dir(run_config.guac_config.home)
    shutil.rmtree(work_dir,ignore_errors=True)
    os.makedirs(work_dir)
    
    recipe_name=os.path.basename(recipe_file).split('.')[0] # remove directories and file type
    
    score_dir=run_config.guac_config.home+"/.scores"
    os.makedirs(score_dir,exist_ok=True)

    recipe_dir=os.path.join(score_dir,recipe_name)
    os.makedirs(recipe_dir,exist_ok=True)

    student_dir=os.path.join(recipe_dir,run_config.student)
    shutil.rmtree(student_dir,ignore_errors=True)
    os.makedirs(student_dir)
    
    total=0
    score=0
    all_results=""
    task_counter=0
    task_scores={}
    for task in to_execute:
        task_name_given=safe_get_var(task,'Name').replace(" ","_")
        task_name=f"{task_counter}-{task_name_given}"
        
        logger.log(color(Fore.GREEN,f"Starting task: {task_name}"),verbose=1)

        task_results=execute(task,run_config,logger)
        test_names=[test.name for test in task_results]
        check_weights(weights,test_names)

        task_points=0
        task_score=0
        for test in task_results:
            test.points=int(safe_get_var(weights,test.name))
            task_points+=test.points
            task_score+=test.get_score()
        task_scores[safe_get_var(task,'Name')]=f"{task_score} / {task_points}"
        total+=task_points
        score+=task_score
            
        result=""
        for test in task_results:
            result+="---\n"
            result+=test.verbose()
        write_output(os.path.join(student_dir,f"{task_name}"),result)
        all_results+=result
        task_counter+=1

        logger.update() # updates progress bar

    logger.close()
    # save result

    final_score=Score(score,total)
    all_results = summerize_task_results(run_config.guac_config.assignment,task_scores,final_score)+all_results
    
    write_output(os.path.join(student_dir,f"{run_config.student}.grade"),all_results)
    
    return score,total

## Interface functions
# included here to avoid circular dependence with Server

def run_student(student,recipe_file,guac_config,weights,to_execute,verbose=0):
    print(f"Grading {student}")
    run_config=RunConfig(guac_config,recipe_file,student=student)
    score,total=run_tasks(recipe_file,weights,to_execute,run_config,verbose=verbose)
    print(f"{student} Grade: {score}/{total}")

        
        
                 
