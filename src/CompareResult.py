import Util
import Collection

import os

from avocado.utils import archive, build, process
from avocado import Test

class CompareResult(Util.GuacTest):

    def test_compare_result(self):
        self._guac_handler(self._test_compare_result)
        
    def _test_compare_result(self):
        """
        :param EXEC: executable
        :Param ARG: arguments(s)
        :param HOME
        :param COLLECTOR
        """
                
        executable=self._safe_param("EXEC")
        arg=self._safe_param("ARG")
        result_re=self._safe_param("RESULT_RE")
        
        collector=Collection.Collector(self)

        # write yaml description to whiteboard
        description=collector.describe()
        description["Description"]="Comparing results with master"
        
        self._write_whiteboard_yaml(description)

        #
        
        student_out=collector.get_output()
        master_out=collector.get_output(master=True)
        
        student_result=Util.parse_for_regex(student_out,result_re)
        master_result=Util.parse_for_regex(master_out,result_re)

        self.log.debug(f"Result: master {master_result} student {student_result}")

        self._write_whiteboard_yaml({"Master_Result":master_result})
        
        if student_result!=master_result:
            self._write_whiteboard_yaml({"Your_Result":student_result})
            self.fail(f"Your_Result does not match Master_Result")

        
