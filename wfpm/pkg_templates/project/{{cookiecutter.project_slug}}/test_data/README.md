# Data for testing

This folder keeps test data used by all packages of this project. You are free to choose
however way you'd like to organize the test data. However here is some general guidance:

* keep test files small to save space and reduce test execution time
* specific files used by different packages should be symlinked to individual package test directory
* since one file can be used by multiple packages, be careful when update the files, it may work for
one package but break for others
