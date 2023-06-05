# guac

Guac is a system for grading assignments. G uac provides several modules which can be easily configured using YAML files. This method is made possible by the [Avocado](https://github.com/avocado-framework/avocado) test framework. In addition, guac provides several tools to aid grading such as manually editing task scores, and exporting class results.

## Installation
**Prerequisites**

```python3.8``` <br>
```git```

Execute ```./install.sh```<br>
This will:

* download Avocado in ~/avocado
* configure Avocado (install plugins, require sequential task execution)
* modify Avocado to use correct Python version (Avocado requires >=3.8 CS machines default to 3.6)
* link guac executable to ~/.local/bin/guac
* install necessary Python libraries

## Usage
### Initialize Assignment Grading Directory
* Create a new directory; named the same as the assignment (not necessary).
* execute ```guac init```
* See [docs/GUAC_CONFIG.md](./docs/GUAC_CONFIG.md) for details of configuration variables.

### Define Tests
Tests are defined by a series of tasks. Each task consists of a source module (which will be run by Avocado) and a series of config files.
The source modules in guac are intended to be generic, therefore creating a test harness for a new assignment should only require writing a series of config files.

* Tasks are defined in a RECIPE_FILE (see [docs/RECIPE_FILE.md](./docs/RECIPE_FILE.md))
* The set of variables required in a config file is dependent on the module being used (see [docs/AVOCADO_MODULES.md](./docs/AVOCADO_MODULES.md))

### Assign Test Weights
```guac list --recipe RECIPE_FILE```

* Before grading assignments we must assign weights to each one of the tests associated with a particular recipe. 
* After running ```guac list``` copy the list of tests to a new file and assign weights to each test (see [docs/WEIGHTS_FILE.md](./docs/WEIGHTS_FILE.md)).
* *Hint: you may find the command ```sed "s/$/: 1/g" -i WEIGHTS_FILE``` useful as a starting point.*

### Generate Master Results
```guac generate --recipe RECIPE_NAME```

* This step executes the recipe for the submission associated with MASTER.
* The results are stored in ASSIGNMENT_HOME/.master_results
* The .master_results directory has the general structure RECIPE_NAME/{VARIABLES} (the variables used depends on the condiguration of the collector module).

### Automatic Grading
```guac run --name NAME --recipe RECIPE_FILE```<br>
```guac run --these STUDENT_FILE --recipe RECIPE_FILE```

* Student submissions can be graded one at a time (by specifying -\-name) or in sets (by specifying -\-these).
* See [docs/STUDENT_FILE.md](./docs/STUDENT_FILE.md) for details.
* Results are written to ASSIGNMENT_HOME/.scores/RECIPE/NAME/{TASK_NAMES,NAME.grade}
* The -\-verbose flag will change log level.

### Manual Grading
#### Inspect 
```guac inspect --name NAME --file FILE```

When manual grading is required, use inspect to cat a file from a student's submission.

#### Extract
```guac extract --these STUDENTS_FILE --file FILE --dest DIST_DIR```

* For manual grading of multiple students (e.g. reports) ```guac extract``` will collect all files in a single directory.
* DEST_DIR will default to ASSIGNMENT_HOME/bin when unspecified.
* Files are copied to DEST_DIR/FILE_NAME/NAME.FILE_SUFFEX e.g. Bob's file *report.pdf* will be copied to DEST_DIR/report/Bob.pdf.

#### Update
```guac update --name NAME --recipe RECIPE_NAME --task TASK --score SCORE``` 

When grading manually, ```guac update``` updates the score for a single task.

### View Grade
```guac grade --name NAME --recipe RECIPE_NAME```

The -\-verbose flag will change grade detail.

* -v 0 $\rightarrow$ only final score
* -v 1 $\rightarrow$ include task summary
* -v 2 $\rightarrow$ include all tests

### Export to Canvas
```guac export --these STUDENTS_FILE --recipe RECIPE_NAME```

