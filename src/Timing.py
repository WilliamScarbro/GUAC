import Util
import numpy as np

import Timing
import Collection

# Timer and Collector must have the sample values for EXEC,ARGS,{CONTEXT},SAMPLES otherwise the results directory will not have the correct structure
class Timer:
    def __init__(self,test):
        self.samples=int(test.params.get("SAMPLES",default=1))
        self.central_measure=test.params.get("CENTRAL_MEASURE",default="MEAN")
        self.collector=Collection.Collector(test)
        self.time_re=test._safe_param("TIME_RE")
        
    def get_time(self,master=False,context=None):
        if context==None:
            context=self.collector.runner.context()

        output_files=[]
        if self.samples==1:
            output_files+=[self.collector.output_file_path(master,context=context)]
        else:
            for i in range(self.samples):
                copy_context=context.copy()
                copy_context["SAMPLE"]=i
                output_files+=[self.collector.output_file_path(master,context=copy_context)]

        output_data=[Util.safe_read(fname) for fname in output_files]
        times=[float(Util.parse_for_regex_group(data,self.time_re)) for data in output_data]

        return self._summerize(times)

    def _summerize(self,times):
        time_arr=np.array(times)
        cm_map={"MEAN":np.mean,
                "MEDIAN":np.median}
        if not self.central_measure in cm_map:
            raise ValueError(f"CENTRAL_MEASURE Name: '{self.central_measure}' is not in list of known CENTRAL_MEASURES: {list(cm_map.keys())}")
        return cm_map[self.central_measure](time_arr)
