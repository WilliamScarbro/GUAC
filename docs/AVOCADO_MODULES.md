# Avocado Modules

Avocado modules use parameters defined by config files. The set of parameters required depends on the module used (below).

Config files are referenced in RECIPE_FILES through the CONFIG variable (see docs/RECIPE_FILE).

Many modules require all of the parameters from another set. Rather than repeating parameters we use the notation \<param-set\> to reference previously defined parameter sets.

When multiple configuration files are listed for a task in the RECIPE_FILE their contents are concatenated. To see the resulting module configuration inspect the file argument to ```--mux-yaml``` in the logs of ```guac generate```.

## Environment Parameters

Some parameters are automatically included in the configuration for all Avocado modules by guac. These values are defined by ***guac.conf*** or by the execution context.

#### env: 
* HOME: String
* ASSIGNMENT: String
* SUBMISSION_HOME: String
* AVOCADO_HOME : String
* MASTER: String
* STUDENT: String


## Modules

#### SetUp:

**Description**

* Creates new working directory: *.work*
* Extracts submission tarball from SUBMISSION_HOME/ASSIGNMENT/STUDENT/ASSIGNMENT.tar to working directory
* Checks submission tarball contains TAR_CONTENTS
* Copies LIB_CONTENTS from *lib* to *.work*

**Parameters**

* \<env\>
* TAR_CONTENTS: [String]
* LIB_CONTENTS: [String]
 
#### MakeTargets:
**Description**

* Checks ```make clean``` removes MAKE_TARGETS
* Checks ```make``` creates MAKE_TARGETS

**Parameters**

* \<env\>
* MAKE_TARGETS: [String]

#### Collect:
**Description**

* Executes program specified by EXEC with argument(s) in ARG
* Writes output to .work/RECIPE_NAME/{VARIABLES} (the variables used depends on the RUNNER specified)
* When MASTER is True, also writes output to .master_results/RECIPE_NAME/{VARIABLES}
* When SAMPLES is greater than 1, program is executed multiple times
* For timing, CENTRAL_MEASURE determines how the final time is calculated
* THREADS is required when using a parallel runner, and specifies the degree of parallelism
* The **Python** runner executes a python program e.g. ```python EXEC ARG```
* The **OMP** runner executes an OMP program by setting the environment variable OMP_NUM_THREADS to THREADS
* The **MPI** runner executes an MPI program e.g. ```mpirun -np THREADS EXEC ARG```


**Parameters**

- \<env\>
- EXEC: String
- ARG: String

**Optional Parameters**

- RUNNER: {\DEFAULT,OMP,MPI,Python} default DEFAULT<br>
- SAMPLES: Int default 1<br>
- CENTRAL_MEASURE: {\_,MEAN,MEDIAN} default MEAN<br>

**OMP/MPI Required Parameters**

- THREADS: Int

#### CompareResult:

**Description**

* Compares result of Student and Master collection outputs
* Requires the collection context: \<Collect\>
* By default, compares entire result
* When RESULT_RE is specified, only compares result matching regular expression group
* RESULT_RE must contain one group: a string surrounded by parenthesis e.g. ```"result: (\\\\d+)"``` will compare result integer

**Parameters**

- \<Collect\>

**Optional Parameters**

- RESULT_RE: RegEx

#### CompareTime:

**Description**

* Compares the time of Student and Master outputs
* Requires the collection context: \<Collect\>
* Extracts time from stdout using TIME_RE
* TIME_RE must contain one group: a string surrounded by parenthesis e.g. ```"time : (\\\\d+\\\\.\\\\d+) sec"``` will extract float time
* TIME_EPSILON allows forgiveness in the comparison e.g. when TIME_EPSILON is 1.5 the STUDENT_TIME must be less than ```1.5*MASTER_TIME```

**Parameters**

- \<Collect\>
- TIME_RE: RegEx
- TIME_EPSILON: float

#### CompareSpeedup:

**Description**

* Compares the speedup of Student and Master outputs
* Requires the collection context: \<Collect\>
* Requires that RUNNER is set to a parallel runner.
* Extracts time from stdout using TIME_RE
* Speedup is calculated as ```SEQ_TIME/PAR_TIME```, this requires that the program was executed with ```THREADS: 1```
* SPEEDUP_EPSILON allows forgiveness in comparison e.g. when SPEEDUP_EPSILON is 0.75 the STUDENT_SPEEDUP must be more than ```0.75*MASTER_SPEEDUP```

**Parameters**

- \<Collect\>
- TIME_RE: RegEx
- SPEEDUP_EPSILON: float
