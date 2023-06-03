import Util
import Collection

import os

from avocado.utils import archive, build, process
from avocado import Test

class Collect(Util.GuacTest):
    def test_collect(self):
        self._guac_handler(self._test_collect)
        
    def _test_collect(self):
        """
        :param EXEC: executable
        :param ARG: argument(s)
        :param HOME
        :param MASTER
        :param LIST
        """
        
        collector=Collection.Collector(self)

        #
        
        desc=collector.describe()
        desc["Description"]="Collecting Results"

        self._write_whiteboard_yaml(desc)

        #
        
        code,out,error=collector.collect()

        if error != "":
            #self.whiteboard+=f"ERROR: {error}"
            #self.log.debug(f"ERROR: {error}")
            self._write_whiteboard_yaml({"ERROR":error})
            self.fail(f"ERROR: {error}")
            
        if code!=0:
            self.whiteboard+=f"EXIT-CODE: {code}\n"
            self.fail(f"Program produced non-zero exit code: {code}")
        

