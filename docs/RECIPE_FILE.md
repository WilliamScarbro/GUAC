# Recipe File

* A recipe file defines a set of tasks used to assign a grade. 
* Each task is defined using a source file containing an Avocado module and a list of config files. 
* Executing a task with guac produces a set of tests. 
* The set of tests associated with all tasks in a recipe are assigned weights by a WEIGHTS_FILE (see docs/WEIGHTS_FILE.md). 
* Tests are evaluated as pass (full points) or fail (no points).
* Guac produces a summary of the total score for each task and a final score for the entire recipe.

## Structure

WEIGHTS: String

TaskList: [Task]

**where:**
```
Task:
  Name: String
  Source: String
  Config: String | [String]
```
## Description
 
WEIGHTS: links to WEIGHTS_FILE<br>
Task: describes a single avocado execution<br>
Name: Task name, must be unique across all tasks in recipe (not checked)<br>
Source: defines the Avocado module to be executed<br>
Config: List (or single) file containing parameters to configure Avocado module
  
## Example

(add python example)
