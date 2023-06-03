import Util
import os

from avocado.utils import archive, build, process

class MakeTargets(Util.GuacTest):
    
    def test_make_clean(self):
        self._guac_handler(self._test_make_clean)
        
    def _test_make_clean(self):
        """
        :avocado: tags=make_clean
        :param ASSIGNMENT
        :param HOME
        :param MAKE_TARGETS
        """
        assignment = self._safe_param("ASSIGNMENT")
        srcdir = Util.get_work_dir(self._safe_param("HOME"))
        make_targets = self._safe_param("MAKE_TARGETS")

        desc={"Description":"Checking 'make clean' removes targets",
              "MAKE_TARGETS":Util.list_to_yaml_str(make_targets) }
        self._write_whiteboard_yaml(desc)
        
        build.make(srcdir,extra_args="clean")

        Util.check_not_contains(self,srcdir,make_targets)
    #

    def test_make(self):
        self._guac_handler(self._test_make)
        
    def _test_make(self):
        """
        :avocado: tags=make
        :param ASSIGNMENT
        :param HOME
        :param MAKE_TARGETS
        """
        assignment = self._safe_param("ASSIGNMENT")
        srcdir = Util.get_work_dir(self._safe_param("HOME"))
        make_targets = self._safe_param("MAKE_TARGETS")

        desc={"Description":"Checking 'make' produces targets",
              "MAKE_TARGETS":Util.list_to_yaml_str(make_targets) }
        self._write_whiteboard_yaml(desc)
        
        build.make(srcdir)

        Util.check_dir_contains(self,srcdir,make_targets)
    #    
