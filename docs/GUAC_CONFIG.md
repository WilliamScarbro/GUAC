# Guac Config

Each assignment is configured using a file named ```guac.conf``` placed in the root directory of the assignment. All guac commands expect this file to be in the current working directory (CWD).

The parameters in ```guac.conf``` can be initialized using the command ```guac init``` which will attempt to fill in sensible default values for each parameter.

## Parameters

* HOME: Assignment home directory
  * default: CWD
* ASSIGNMENT: Assignment name
  * default: directory name of CWD
* GUAC_HOME: Location where guac is installed
  * default: $HOME/guac
* AVOCADO_HOME: Location where avocado is installed
  * default: $HOME/avocado
* SUBMISSION_HOME: Location where submissions are stored
  * default: $HOME/Checkin
* MASTER: Instructor login, used for master submission
  * no default
