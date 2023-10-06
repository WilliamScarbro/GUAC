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
        desc=yaml.safe_load(self.description)

        if self.status == "PASS":
            desc["Status"]="PASS"
        else:
            desc["Status"]=self.status
            desc["Error_Message"]=self.fail_message

        desc["Score"]=f"{self.score} / {self.points}"
        return yaml.dump(desc)
                

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
    cmd = f"avocado run {run_config.guac_config.guac_home}/src/{script} --mux-yaml {new_config} --job-timeout {run_config.guac_config.job_timeout} "
    logger.log(color(Fore.BLUE,f"Executing: {cmd}"),verbose=2)
    #try:
    code,out,error = run_command(run_config.guac_config.home,cmd)
    if code==1: # test error
        logger.log(color(Fore.RED,out),verbose=2)
        logger.log(color(Fore.RED,error),verbose=2)
    if code!=2: # avocado does not produce logs in this case
        try:
            logs=parse_for_regex_group(out,"JOB LOG\s+:\s+(.*)")
            logger.log(color(Fore.BLUE,f"Logs: {logs}"),verbose=2)
        except Exception as e:
            print(out)
            print(e)
    if code==2: # this is an avocado error, not a test error
        print(color(Fore.RED,error))
    if code!=0 and run_config.is_listing=="True":
        raise Exception("Task failed")
        
    if code==0 or code==1:
        return parse_result_json()
    else:
        return []

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
        try:
            res=execute(task,run_config,logger)
            if res:
                resutls+=res
        except Exception as e:
            print(e)
        logger.update()
    logger.close()
    print(color(Fore.GREEN,">>>>>> Begin Test List <<<<<<<"))
    for result in results:
        print(result.name)
    

class GradeResults:
    # Score, {}, Bool
    def __init__(self,assignment,grade,task_scores,task_results,sub_status,messages):
        self.assignment=assignment
        self.grade=grade
        self.task_scores=task_scores
        self.task_results=task_results # results of individual tests
        self.sub_status=sub_status # "OnTime","Late","Missing"
        self.messages=messages
    
    def dump(self,verbose=0):
        if verbose==0:
            res=f"Grade: {self.grade}"
            if self.sub_status=="Late" or self.sub_status=="Missing":
                res+=f" # ({self.sub_status})" 
            return res

        summery={}
        summery["Grade"]=str(self.grade)
        summery["Task_Scores"]=self.task_scores

        summery["Submission_Status"]=self.sub_status

        if not self.messages is None:
            summery["Messages"]=self.messages
            
        if verbose==1:
            return yaml.dump(summery,sort_keys=False)
        if verbose==2:
            summery["Assignment"]=self.assignment
            summery["Task_Results"]=self.task_results
            return yaml.safe_dump(summery,sort_keys=False)

    def add_message(self,message):
        if self.messages==None:
            self.messages=[message]
        else:
            self.messages.append(message)
            
    @staticmethod
    def from_data(data):
        grade=safe_get_var(data,"Grade")
        task_scores=safe_get_var(data,"Task_Scores")
        assignment=safe_get_var(data,"Assignment")
        sub_status=safe_get_var(data,"Submission_Status")
        task_results=safe_get_var(data,"Task_Results")
        messages=data["Messages"] if "Messages" in data else None
        return GradeResults(assignment,grade,task_scores,task_results,sub_status,messages)

    @staticmethod
    def get_task_scores(task_results):
        return {safe_get_var(task,"Task_Name"):safe_get_var(task,"Score") for task in task_results}

    @staticmethod
    def get_grade(task_scores):
        total=Score(0,0)
        for name,score in task_scores.items():
            total+=Score.fromString(score)
        return str(total)
    
# run_tasks :: String -> String -> [Task] -> RunConfig -> (Int,Int)
def run_tasks(recipe_file,weights,to_execute,run_config,verbose=0):

    def set_points(tests,weights):
        if not tests:
            return
        test_names=[test.name for test in tests]
        check_weights(weights,test_names)
        for test in tests:
            test.points=int(safe_get_var(weights,test.name))
        
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
    

    task_results=[]
    task_status_history={}
    
    #task_counter=0
    for task in to_execute:
        logger.log("---",verbose=1)
        task_name=safe_get_var(task,'Name').replace(" ","_")
        #task_name=f"{task_counter}-{task_name_given}"

        task_data={"Task_Name":task_name}
        
        dependencies = task['Depends'] if 'Depends' in task else []
        if not isinstance(dependencies,list):
            dependencies=[dependencies]
            
        all_dep_filled=True
        for dep in dependencies:
            dep_replaced=dep.replace(" ","_")
            if not dep_replaced in task_status_history or task_status_history[dep_replaced]!="Passed":
                all_dep_filled=False
                first_not_passed=dep_replaced
                break
            
        if not all_dep_filled:
            if first_not_passed in task_status_history:
                logger.log(color(Fore.RED,f"Skipping task: {task_name}, required task '{first_not_passed}' was {task_status_history[first_not_passed]}"),verbose=1)
                task_data["Message"]=f"Skipped, required task '{first_not_passed}' was {task_status_history[first_not_passed]}"
            else:
                logger.log(color(Fore.RED,f"Skipping task: {task_name}, required task '{first_not_passed}' is missing"),verbose=1)
                task_data["Message"]=f"skipped, required task '{first_not_passed}' is Missing"
                
            copied_run_config=RunConfig(run_config.guac_config,run_config.recipe,is_listing="True")
            exec_results=execute(task,copied_run_config,logger)
            set_points(exec_results,weights)
            #for test in exec_results
            task_points=sum(test.points for test in exec_results)

            task_data["Score"]=f"0 / {task_points}"
            task_status_history[task_name]="Skipped"
            
        else:
        
            logger.log(color(Fore.GREEN,f"Starting task: {task_name}"),verbose=1)

            exec_results=execute(task,run_config,logger) # [AvocadoTest]
            set_points(exec_results,weights)
            
            all_passed=True
            for test in exec_results:
                if test.status!="PASS":
                    all_passed=False
                    break

            task_status_history[task_name] = "Passed" if all_passed else "Failed"
                
            task_points=0
            task_score=0
            for test in exec_results:
                task_points+=test.points
                task_score+=test.get_score()
            
        
            parsed_results=[]
            for test in exec_results:
                parsed_results.append(yaml.safe_load(test.verbose()))
                
            task_data["Score"]=f"{task_score} / {task_points}"
            task_data["Test_Results"]=parsed_results
                            
                                 
        task_results.append(task_data)
        #task_counter+=1

        logger.update() # updates progress bar

    logger.close()
    # save result

    assignment = run_config.guac_config.assignment
    sub_home = run_config.guac_config.sub_home
    student = run_config.student
    
    _,late=file_location(sub_home,assignment,student,"tar")
                        
    task_scores=GradeResults.get_task_scores(task_results)
    grade=GradeResults.get_grade(task_scores)
    
    grade_results=GradeResults(assignment,grade,task_scores,task_results,late,None)

    write_output(os.path.join(student_dir,f"{student}.grade"),grade_results.dump(verbose=2))

    return grade_results


## Interface functions
# included here to avoid circular dependence with Server

def run_student(student,recipe_file,guac_config,weights,to_execute,verbose=0):
    print(f"Grading {student}")
    run_config=RunConfig(guac_config,recipe_file,student=student)
    return run_tasks(recipe_file,weights,to_execute,run_config,verbose=verbose)

        
        
                 
