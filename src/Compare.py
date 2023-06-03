import Util

import os

import re

from avocado.utils import archive, build, process
from avocado import Test

class Compare(Util.SafeTest):
    
    def test_compare_result(self):
        """
        :param EXEC: executable
        :Param ARG: arguments(s)
        :param HOME
        :param ARG
        """
        executable=self._safe_param("EXEC")
        arg=self._safe_param("ARG")
        self.whiteboard=f"Comparing results of command './{executable} {arg}' with master\n"
        
        student_out=Util.safe_read(Util.student_output_file_path(self))
        master_out=Util.safe_read(Util.master_output_file_path(self))

        student_result=self._parse_result(student_out)
        master_result=self._parse_result(master_out)

        if student_result!=master_result:
            self.cancel(f"Failed Result Check: \nCorrect Result: {master_result}\nYour Result: {student_result}")


    def test_compare_time(self):
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
        
        epsilon=float(self._safe_param("TIME_EPSILON"))
        #self.log.debug(f"TIME_EPSILON {self._safe_param('TIME_EPSILON')}")
        self.whiteboard=(f"Comparing time of command './{executable} {arg}' with master\n"
                         f"THREADS: {threads}\n"
                         f"EPSILON: {epsilon}\n")
         
        student_out=Util.safe_read(Util.student_output_file_path(self))
        master_out=Util.safe_read(Util.master_output_file_path(self))
        
        student_time=self._parse_time(student_out)
        master_time=self._parse_time(master_out)
        maximum = master_time*epsilon
        if student_time>maximum:
            self.cancel(f"Failed Time Test: maximum time: {maximum} < your time: {student_time}")

    def test_compare_speedup(self):
        """
        :param EXEC
        :param ARG
        :param THREADS
        :param SPEEDUP_EPSILON
        """
        executable=self._safe_param("EXEC")
        arg=self._safe_param("ARG")
        threads=self._safe_param("THREADS")
        
        epsilon=float(self._safe_param("SPEEDUP_EPSILON"))
        self.whiteboard=(f"Comparing speedup of command './{executable} {arg}' with master\n"
                         f"THREADS: {threads}\n"
                         f"EPSILON: {epsilon}\n")
        
        std_par_time=self._parse_time(Util.safe_read(Util.student_output_file_path(self)))
        std_seq_time=self._parse_time(Util.safe_read(Util.student_output_file_path(self,threads=1)))

        master_par_time=self._parse_time(Util.safe_read(Util.master_output_file_path(self)))
        master_seq_time=self._parse_time(Util.safe_read(Util.master_output_file_path(self,threads=1)))

        std_speedup = std_seq_time / std_par_time
        master_speedup = master_seq_time / master_par_time

        minimum = master_speedup*epsilon
        if std_speedup < minimum:
            self.cancel(f"Failed Speedup Test: minimum speedup: {minimum} > your speedup: {std_speedup}")
            
    def _parse_result(self,text):
        """
        :param RESULT_RE: this may not work, passing RE through YAML is tricky
        """
        result_re=self._safe_param("RESULT_RE")
        result_re=result_re.replace('\\\\','\\')
        match = re.search(result_re, text)
        if match:
            return match.group(1)
        self.cancel(f"Cannot parse result in text: {text}")

    def _parse_time(self,text):
        """
        :param TIME_RE
        """
        time_re=self._safe_param("TIME_RE")
        #self.log.debug(f"Regular expression: {time_re}")
        time_re=time_re.replace('\\\\','\\')
        self.log.debug(f"Regular expression: {time_re}")
        
        match = re.search(time_re, text)
        if match:
            return float(match.group(1))
        self.cancel(f"Cannot parse time")
