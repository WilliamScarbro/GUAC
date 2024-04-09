import Util
import Collection
import Timing

import os

import re

from avocado.utils import archive, build, process
from avocado import Test

class CompareTime(Util.GuacTest):

    def test_compare_time(self):
        self._guac_handler(self._test_compare_time)
        
    def _test_compare_time(self):
        """
        :param TIME_EPSILON
        :param HOME
        :param EXEC
        :param ARG
        :param TIME_RE
        """
        
        time_re=self._safe_param("TIME_RE")        
        epsilon=float(self._safe_param("TIME_EPSILON"))

        #
        
        timer=Timing.Timer(self)
        collector=timer.collector

        #
        
        description=collector.describe()
        description["Description"]="Comparing time with master"
        description["EPSILON"]=epsilon

        self._write_whiteboard_yaml(description)

        #
        
        student_time=timer.get_time()
        master_time=timer.get_time(master=True)
        
        maximum = master_time*epsilon
        self._write_whiteboard_yaml({"Maximum_Time":float(maximum)})

        if student_time>maximum:
            self._write_whiteboard_yaml({"Your_Time":float(student_time)})
            self.fail(f"Your_Time > Maximum_Time")
        
