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
        result_re=self.params.get("RESULT_RE",default=None)
        match_method=self.params.get("MATCH_METHOD",default="Default")
        
        collector=Collection.Collector(self)

        # write yaml description to whiteboard
        description=collector.describe()
        description["Description"]="Comparing results with master"
        
        self._write_whiteboard_yaml(description)

        #
        
        student_out=collector.get_output()
        master_out=collector.get_output(master=True)

        self.log.debug(master_out)
        
        if not result_re:
            student_result=student_out
            master_result=master_out
        else:
            match_method_map = {"Default":Util.parse_for_regex,
                                "Group":Util.parse_for_regex_group,
                                "Set":Util.parse_for_regex_set}
            if match_method in match_method_map:
                match_func=match_method_map[match_method]
                student_result=match_func(student_out,result_re)
                master_result=match_func(master_out,result_re)
            else:
                raise ValueError(f"MATCH_METHOD '{match_method}' is not in known methods: {list(match_method_map.keys)}")

        if master_out=='':
            raise Exception(f"Master matched result is empty output '{master_out}' result_re '{result_re}'")
        
        self.log.debug(f"Result: master {master_result} student {student_result}")

        self._write_whiteboard_yaml({"Master_Result":master_result})
        
        if student_result!=master_result:
            self._write_whiteboard_yaml({"Your_Result":student_result})
            self.fail(f"Your_Result does not match Master_Result")

        
