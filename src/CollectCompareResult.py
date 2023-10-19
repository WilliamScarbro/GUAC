import Util
import Collection

import os

from avocado.utils import archive, build, process
from avocado import Test

from CompareResult import _CompareResult
from Collect import _Collect

class CollectCompareResult(Util.GuacTest,_CompareResult,_Collect):
    def test_collect_compare_result(self):
        self._guac_handler(self._test_collect)
        self._guac_handler(self._test_compare_result)

        
    
