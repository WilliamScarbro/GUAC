import Util

import os

class Collector:
    def __init__(self,test):
        #self.name="Collector"
        self.home=test._safe_param("HOME")
        self.recipe=test._safe_param("RECIPE")
        self.runner=get_runner(test.params.get("RUNNER",default="DEFAULT"),test)
        self.samples=int(test.params.get("SAMPLES",default=1))
        self.master=test._safe_param("MASTER")=="True"

        #self._make_linear_dirs(self.result_dir(),[])
        #self._make_linear_dirs(self.result_dir(),master=True,[])
            
        
    @staticmethod
    def _make_linear_dirs(initial,dirs):
        so_far=initial
        os.makedirs(so_far,exist_ok=True)
        for cur in dirs:
            so_far=os.path.join(so_far,str(cur))
            os.makedirs(so_far,exist_ok=True)
        return so_far

    @staticmethod
    def _context_path(context):
        return [f"{val}~{context[val]}" for val in context.keys()]
            
    def result_dir(self,master=False):
        if master:
            return Util.get_master_dir(self.home,self.recipe)
        return os.path.join(Util.get_work_dir(self.home),"results")

    def get_output(self,master=False,context=None):
        if context is None:
            context=self.context(sample=1)
        ofp=self.output_file_path(master=master,context=context)
        return Util.safe_read(ofp)
    
    def output_file_path(self,master=False,context=None):
        if context is None:
            context=self.context()
        result_dir=self.result_dir(master)
        cp=self._context_path(context)
        directory=self._make_linear_dirs(result_dir,cp[:-1])
        return f"{directory}/{cp[-1]}"

    # when self.samples!=1, sample should be specified
    def context(self,sample=None):
        rc=self.runner.context()
        if self.samples==1:
            return rc
        rc["SAMPLE"]=sample
        return rc
        
    def command(self):
        return self.runner.command()

    def collect(self):
        context=self.runner.context()
        if self.samples==1:
            code,out,error=self.runner.run()
            self._record(out,context=self.context())
            return code,out,error
        #
        for i in range(self.samples):
            code,out,error=self.runner.run()
            context=self.context(sample=i)
            self._record(out,context)
        return code,out,error

    def _record(self,out,context):
        if self.master:
            out_file=self.output_file_path(master=True,context=context)
            Util.write_output(out_file,out)
        out_file=self.output_file_path(context=context)
        Util.write_output(out_file,out)

    def describe(self):
        return self.runner.describe()
#


def get_runner(runner_name,test):
    runner_map={"DEFAULT":Runner,
                "MPI":MPIRunner,
                "OMP":OMPRunner,
                "Python":PythonRunner}
    if not runner_name in runner_map:
        raise ValueError(f"Runner Name: '{runner_name}' is not in list of known runners: {list(runner_map.keys())}")
    return runner_map[runner_name](test)
#

class Runner:
    def __init__(self,test):
        self.name="DEFAULT"
        self.home=test._safe_param("HOME")
        self.executable=test._safe_param("EXEC")
        self.args=test._safe_param("ARG")
        
    def command(self):
        return f"./{self.executable} {self.args}"

    def run(self):
        code,out,error= Util.run_command(Util.get_work_dir(self.home),self.command())
        return code,out,error

    def context(self):
        return {"EXEC":self.executable,"ARG":str(self.args).replace(" ","_")}

    def describe(self):
        return {"COMMAND":self.command()}

class PythonRunner(Runner):
    def __init__(self,test):
        Runner.__init__(self,test)
        #self.version=test.get_param

    def command(self):
        return f"python {self.executable} {self.args}"
    
# abstract
class PARRunner(Runner):
    def __init__(self,test):
        Runner.__init__(self,test)
        self.threads=test._safe_param("THREADS")

    def context(self):
        super_context = super().context()
        super_context["THREADS"]=self.threads
        return super_context

    def describe(self):
        desc=super().describe()
        desc["THREADS"]=self.threads
        return desc
#

class MPIRunner(PARRunner):
    def __init__(self,test):
        PARRunner.__init__(self,test)
        self.name="MPI"
        
    def command(self):
        return f"mpirun -np {self.threads} {self.executable} {self.args}"

    # inherit run,context,describe
#

class OMPRunner(PARRunner):
    def __init__(self,context):
        PARRunner.__init__(self,context)
        self.name="OMP"
        
    def run(self):
        code,out,error=Util.run_command(Util.get_work_dir(self.home),self.command(),env={"OMP_NUM_THREADS":str(self.threads)})
        return code,out,error

    # inherit command,context,describe
#
