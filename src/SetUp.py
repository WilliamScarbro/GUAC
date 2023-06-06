import Util

import os
import shutil

from avocado.utils import archive, build, process

from avocado import Test

class SetUp(Util.GuacTest):  


    def test_clear_work(self):
        self._guac_handler(self._test_clear_work)
        
    def _test_clear_work(self):
        """
        :param HOME: test directory
        """
        desc={"Description":"Clearing working directory"}
        self._write_whiteboard_yaml(desc)
        #
        home = self._safe_param("HOME")
        work = Util.get_work_dir(home)

        shutil.rmtree(work)
        os.makedirs(work)
    #

    def test_tar_exists(self):
        self._guac_handler(self._test_tar_exists)
        
    def _test_tar_exists(self):
        """
        :avocado: tags=tar_exists 
        :param STUDENT
        :param HOME
        :param ASSIGNMENT
        """
        
        desc={"Description":"Testing Tarball exists"}
        self._write_whiteboard_yaml(desc)
        tar_loc = self._tar_location()
        #
        if not os.path.isfile(tar_loc):
            self.cancel(f"Missing {os.path.basename(tar_loc)}")
            
        tar_desc={"Message":f"Grading {os.path.basename(tar_loc)}",
              "Contents":Util.list_tar_contents(tar_loc)}
        self._write_whiteboard_yaml(tar_desc)
        
    #

    def test_extract_tar(self):
        self._guac_handler(self._test_extract_tar)
        
    def _test_extract_tar(self):
        """
        :avocado: tags=extract_tar
        :param STUDENT
        :param HOME
        :param ASSIGNMENT
        """
       
        desc={"Description":"Extracting Tarball to working directory"}
        self._write_whiteboard_yaml(desc)
        #
        work=Util.get_work_dir(self._safe_param("HOME"))
        tar_loc=self._tar_location()
        archive.extract(tar_loc,work)

        # not the best, should find a better solution, or a better standard
        assignment_dir=os.path.join(work,self._safe_param("ASSIGNMENT"))
        if os.path.isdir(assignment_dir):
            for el in os.listdir(assignment_dir):
                shutil.move(os.path.join(assignment_dir,el),os.path.join(work,el))
                
    #

    def test_tar_contents(self):
        self._guac_handler(self._test_tar_contents)
        
    def _test_tar_contents(self):
        """
        :param STUDENT
        :param HOME
        :param ASSIGNMENT
        :param TAR_CONTENTS
        """
        tar_contents=self._safe_param("TAR_CONTENTS")

        desc={"Description":"Checking Tarball Contents",
              "Required Contents":tar_contents}
        self._write_whiteboard_yaml(desc)

        assignment = self._safe_param("ASSIGNMENT")
        srcdir = Util.get_work_dir(self._safe_param("HOME"))

        Util.check_dir_contains(self,srcdir,tar_contents)
    #

    def test_copy_lib_contents(self):
        self._guac_handler(self._test_copy_lib_contents)
        
    def _test_copy_lib_contents(self):
        """
        :param STUDENT
        :param HOME
        :param ASSIGNMENT
        :param LIB_CONTENTS
        """
        
        lib_contents=self.params.get("LIB_CONTENTS",default=[])
        desc={"Description":"Copying into working directory",
              "LIB_CONTENTS":lib_contents}
        self._write_whiteboard_yaml(desc)
        
        home = self._safe_param("HOME")
        srcdir = Util.get_work_dir(home)
        libdir = os.path.join(home,"lib")
        
        for book in lib_contents:
            shutil.copyfile(os.path.join(libdir,book),os.path.join(srcdir,book))
    #       
        
    def _tar_location(self):
        sub_home=self._safe_param("SUBMISSION_HOME")
        assignment=self._safe_param("ASSIGNMENT")
        student=self._safe_param("STUDENT")

        return Util.tar_location(sub_home,assignment,student)
