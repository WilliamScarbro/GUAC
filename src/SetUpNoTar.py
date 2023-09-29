import Util

import os
import shutil

from avocado.utils import archive, build, process

from avocado import Test

class SetUpNoTar(Util.GuacTest):  


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

    def test_file_exists(self):
        self._guac_handler(self._test_file_exists)
        
    def _test_file_exists(self):
        """
        :avocado: tags=tar_exists 
        :param STUDENT
        :param HOME
        :param ASSIGNMENT
        """
        
        desc={"Description":"Testing submission exists"}
        self._write_whiteboard_yaml(desc)

        file_loc = self._file_location()
        #
            
        file_desc={"Message":f"Grading {os.path.basename(file_loc)}"}
              # "Contents":Util.list_tar_contents(tar_loc)}
        self._write_whiteboard_yaml(file_desc)
        
    #

    def test_copy_file(self):
        self._guac_handler(self._test_copy_file)
        
    def _test_copy_file(self):
        """
        :avocado: tags=extract_tar
        :param STUDENT
        :param HOME
        :param ASSIGNMENT
        :param FILE_TYPE
        """
       
        desc={"Description":"Moving submission to working directory"}
        self._write_whiteboard_yaml(desc)
        #
        work=Util.get_work_dir(self._safe_param("HOME"))
        file_loc=self._file_location()
        shutil.copy(file_loc,os.path.join(work))

        # not the best, should find a better solution, or a better standard
        #assignment_dir=os.path.join(work,self._safe_param("ASSIGNMENT"))
        #if os.path.isdir(assignment_dir):
        #    for el in os.listdir(assignment_dir):
        #        shutil.move(os.path.join(assignment_dir,el),os.path.join(work,el))
                
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
        
    def _file_location(self):
        sub_home=self._safe_param("SUBMISSION_HOME")
        assignment=self._safe_param("ASSIGNMENT")
        student=self._safe_param("STUDENT")
        file_type=self._safe_param("FILE_TYPE")

        file_loc,status = Util.file_location(sub_home,assignment,student,file_type)

        if status=="Missing" or file_loc==None: # should be true at the same time
            self.fail("Missing submission")

        return file_loc
