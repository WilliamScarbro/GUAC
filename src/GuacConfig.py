
from ParseYaml import *

class GuacConfig:
    def __init__(self):
        self.assignment,self.home,self.avo_home,self.sub_home,self.guac_home,self.master = parse_guac_yaml("guac.yaml")

class RunConfig:
    def __init__(self,guac_config,recipe,student=None,is_listing="False"):
        self.guac_config=guac_config
        self.recipe=recipe
        self.is_master=student is None
        if student is None:
            self.student=self.guac_config.master
            self.is_master="True"
        else:
            self.student=student
            self.is_master="False"
        self.is_listing=is_listing
    
    def get_run_config_yaml(self):
        return yaml.dump({"ASSIGNMENT":self.guac_config.assignment,
                          "HOME":self.guac_config.home,
                          "SUBMISSION_HOME":self.guac_config.sub_home,
                          "RECIPE":self.recipe,
                          "STUDENT":self.student,
                          "MASTER":self.is_master,
                          "LIST":self.is_listing})
