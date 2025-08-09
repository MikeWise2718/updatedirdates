# UpdateDirDates App
9 August 2025 - Mike Wise

# Purpose
These are specs for an "UpdateDirDates" App - it sets modified dates on a set of directories to accurately reflect the latest modified dates of the files (not subdirectories) in that directory or in sub-directories. Only actual file modification times are considered, not subdirectory modification times which may have incorrect copy dates. These will sometimes get out of synchronization when directories are copied or files are deleted.


# Tech and Structure
It should be a command line python app, using Python 3.13.

It should uses a virtual python environment.

It should follow current conventional python directory layout structures.

It should have a test suite with over 80 percent code coverage.

It should have command line parameters using argprase.

It should have colored output using colorrama, that has errors as red, warnings as yellow, success as green.

# Features
It should have verbosity levels, 0 being mostly quiet except for statistics, 1 printing first level directories as they are traversed, and 2 printing all directories as they are traversed along with a message that either the date is ok, or what it needs to be changed to.

It should - by default - do a "dry run" where no changes are actually made. Only if a flag "-x" is executed

It should print out statistics at the end including execution time and number of directory dates changed, or would have been changed in a dry run (the labels should reflect whether it was a dry run or not).

It should have a readme that gives examples of how to use it

It should have a "testing readme" that describes the current code coverage, but also how to run the tests and run the code coverage.