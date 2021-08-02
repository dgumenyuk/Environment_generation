# Testing autonomous robot model in Player/Stage simulator

## Stage 1: generating the scenarios

To generate the scenarios using the multiobjective configuration of AmbieGen you can use the module [AmbieGen_mo](https://github.com/dgumenyuk/Environment_generation/tree/main/RQ3/Autonomous_robot/AmbieGen_mo). To generate the scenarios randomly [AmbieGen_ran](https://github.com/dgumenyuk/Environment_generation/tree/main/RQ3/Autonomous_robot/AmbieGen_ran). To launch the modules you should execute:
```
python Optimize.py
```
inside the folder. It will launch the 2 hour experiment to run 30 times. The generated scenarios will be saved in the "Results" folder.
## Stage 2: running the scenarios in the Player stage simulator
Firstly, the [Player/Stage simulator](http://playerstage.sourceforge.net/) should be installed. We have installed in Ubuntu 16.04 environment, using the following instructions:
1. Download the files: https://www.cpp.edu/~ftang/courses/player%20stage/installation_Bash_Files.zip . They contain the list of dependencies needed for installation.
2. The latest Player/Stage version can downloaded from: https://playerproject.github.io/ .

Once installed, copy the [Player_pipeline_](https://github.com/dgumenyuk/Environment_generation/tree/main/RQ3/Autonomous_robot/Player_pipeline_) in the home directory and follow the instructions from readme in that folder.
