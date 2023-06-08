# guac Server

Grading server for guac.

### Configuration
* RECIPE_NAME
* ASSIGNMENT
* SUBMISSION_HOME

### Overview
* Looks for request file in SUBMISSION_HOME/ASSIGNMENT/ASSIGNMENT.requests/{NAME}
* Grades most recent submission for student NAME using recipe RECIPE_NAME
* Copies result to SUBMISSION_HOME/ASSIGNMENT/ASSIGNMENT/ASSIGNMENT.prelim/NAME.grade
* Moves request file to SUBMISSION_HOME/ASSIGNMENT/ASSIGNMENT.tested/
* Logs to SUBMISSION_HOME/ASSIGNMENT/GuacServer.log

### Details
* GuacServer locks the assignment directory to all guac actions while running (by creating a .server file)
  * This avoids overwriting local data while server is running
  * Therefor, it is recommended to have a separate development and production directories

