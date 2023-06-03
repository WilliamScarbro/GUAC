import Util

import os

import re

from avocado.utils import archive, build, process
from avocado import Test

class CompareTimePAR(Util.GuacTest):

    def test_compare_time(self):
        self._guac_handler(self._test_compare_time)
        
    def _test_compare_time(self):
        """
        :param TIME_EPSILON
        :param HOME
        :param EXEC
        :param ARG
        :param THREADS
        """
        
        executable=self._safe_param("EXEC")
        arg=self._safe_param("ARG")
        threads=self._safe_param("THREADS")
        time_re=self._safe_param("TIME_RE")
        
        epsilon=float(self._safe_param("TIME_EPSILON"))
        #self.log.debug(f"TIME_EPSILON {self._safe_param('TIME_EPSILON')}")
        self.whiteboard=(f"Comparing time of command './{executable} {arg}' with master\n"
                         f"THREADS: {threads}\n"
                         f"EPSILON: {epsilon}\n")

        collector=Util.getCollector(self)
        
        student_out=Util.safe_read(collector.student_output_file_path())
        master_out=Util.safe_read(collector.master_output_file_path())
        
        student_time=float(Util.parse_for_regex(student_out,time_re))
        master_time=float(Util.parse_for_regex(master_out,time_re))
        
        self.log.debug(f"Times: master: {master_time} student: {student_time}")

        maximum = master_time*epsilon
        if student_time>maximum:
            self.cancel(f"Failed Time Test: maximum time: {maximum} < your time: {student_time}")
        
