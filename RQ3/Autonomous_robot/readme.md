# Testing autonomous robot model in Player/Stage simulator

## Stage 1: generating the scenarios

To generate the scenarios using the multiobjective configuration of AmbieGen you can use the module [AmbieGen_mo](https://github.com/dgumenyuk/Environment_generation/tree/main/RQ3/Autonomous_robot/AmbieGen_mo). To generate the scenarios randomly [AmbieGen_ran](https://github.com/dgumenyuk/Environment_generation/tree/main/RQ3/Autonomous_robot/AmbieGen_ran). To launch the modules you should execute:
```
python Optimize.py
```
inside the folder. It will launch the 2 hour experiment to run 30 times. The generated scenarios will be saved in the "Results" folder.
## Stage 2: running the scenarios in the Player stage simulator
