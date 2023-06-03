import Util
import Collection
import Timing

import os

from avocado.utils import archive, build, process
from avocado import Test

class CompareSpeedup(Util.GuacTest):

    def test_compare_speedup(self):
        self._guac_handler(self._test_compare_speedup)
        
    def _test_compare_speedup(self):
        """
        :param EXEC
        :param ARG
        :param THREADS
        :param SPEEDUP_EPSILON
        """
        
        epsilon=float(self._safe_param("SPEEDUP_EPSILON"))

        timer=Timing.Timer(self)
        collector=timer.collector
        runner=timer.collector.runner
        assert isinstance(runner,Collection.PARRunner), f"Invalid RUNNER {runner.name}: CompareSpeedup can only be used with extensions of PARRunner"

        #
        
        description=collector.describe()
        description["Description"]="Comparing speedup with master"
        description["EPSILON"]=str(epsilon)
        self._write_whiteboard_yaml(description)
        
        #
        
        std_par_time=timer.get_time()
        master_par_time=timer.get_time(master=True)

        context=timer.collector.runner.context()
        context["THREADS"]=1

        std_seq_time=timer.get_time(context=context)
        master_seq_time=timer.get_time(master=True,context=context)

        #
        
        if std_par_time==0:
            self.fail(f"your parallel time is 0 seconds")
            
        if master_par_time==0:
            self.warning("master parallel time is 0 seconds")

        #
        
        std_speedup = std_seq_time / std_par_time
        master_speedup = master_seq_time / master_par_time

        self.log.debug(f"Speedup: master {master_speedup} student {std_speedup}")
                       
        minimum = master_speedup*epsilon
        if std_speedup < minimum:
            self.fail(f"minimum speedup: {minimum} > your speedup: {std_speedup}")    
