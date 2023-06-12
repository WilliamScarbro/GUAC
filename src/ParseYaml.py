import yaml

import Util

###
# YAML Helper functions 

# safe_get_var :: String -> IO String
def safe_get_var(dt,var):
    val=dt.get(var)
    if val is None:
        raise ValueError(f"Invalid YAML format: '{var}' key not found in {dt}.")
    return val

# read_yaml_file :: String -> {a}
def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        file.close()
    return data

# parse_guac_yaml :: String -> (String,String,String)
def parse_guac_yaml(file_path):

    data = read_yaml_file(file_path)
    assignment=safe_get_var(data,"ASSIGNMENT")
    home=safe_get_var(data,"HOME")
    master=safe_get_var(data,"MASTER")
    avo_home=safe_get_var(data,"AVOCADO_HOME")
    sub_home=safe_get_var(data,"SUBMISSION_HOME")
    guac_home=safe_get_var(data,"GUAC_HOME")
    return assignment,home,avo_home,sub_home,guac_home,master

# data Task = {Name:String,Source:String,Config:[String]}
# parse_recipe_yaml :: String -> (String,[Task])
def parse_recipe_yaml(file_path):
    data=read_yaml_file(file_path)
    #print(data)
    weights=safe_get_var(data,"WEIGHTS")
    tasklist=safe_get_var(data,"TaskList")
    if not isinstance(tasklist,list):
        raise ValueError("Invalid YAML format: {file_path} does not contain a list of Tasks")

    uw_tasks=[safe_get_var(task,"Task") for task in tasklist]
    for task in uw_tasks:
        safe_get_var(task,"Name")
        safe_get_var(task,"Source")
        safe_get_var(task,"Config")
    return weights,uw_tasks

# parse_students_yaml :: String -> [String]
def parse_students_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            yaml_data = yaml.safe_load(file)
            students = yaml_data.get('students')
            if students is None or not isinstance(students, list):
                raise ValueError("Invalid YAML format: 'students' key not found or is not a list.")
            return students
        except yaml.YAMLError as e:
            raise ValueError(f"Error while parsing YAML file: {e}")

# parse_weights :: String -> [String] -> {String:String}
def check_weights(weights,test_names):
    #data = read_yaml_file(file_path)
    for name in test_names:
        val=weights.get(name)
        if val is None:
            raise ValueError(f"Test '{name}' missing from weights file.")


def parse_score_file(file_path):
    score_data=Util.safe_read(file_path)
    score_data_split=score_data.split("---")

    summery=yaml.safe_load(score_data_split[0])

    score=Util.Score.fromString(safe_get_var(summery,"Grade"))

    late = "LATE" in summery
    
    return score_data,score_data_split[0],summery,score,late
    
# converts to ordered dict, necessary to preserve order
# data : [(a,b)]
def yamlDumpList(data):
    od = ordereddict(data)
    yaml.dump(od)
