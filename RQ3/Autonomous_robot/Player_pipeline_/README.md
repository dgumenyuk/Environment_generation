Install Python dependencies using pip:

    $ pip install -r requirements.txt

Files
*****

Most scripts have usage information printed when passed no arguments. If they
don't explicitly print it, they usually have examples at the end of the file.



autonomous_agent_controller.py
    Commands a Player robot to follow waypoints from  a "autonomous_agents.json" file (w/collision avoidance).



eventdetector.py
    Monitors Stage simulation for events and logs to file. The set of possible events is specified in "events.json"
    See https://github.com/Rezzie/eventdetector for more information.


monitors.py
    Event detection logic for simulation monitoring.

go.sh
    Launches the scenarios and collects the data

player.cfg 
    Specification of the autonomous agent model (robot type, type of control algorithm used)

stage.world 
    Speification of the environment, where the robot is navigating (the scenario file, the map size, etc.)


Usage
*****

Some scripts contain path to certain files, and it should be modified to suit your systems before usage. You should change the paths in the following files:
```player.cfg```, ```stage.world```.

All the scenarios should be placed in the "Results" folder, as shown in the examples.
To execute the scenarios, you should launch the "run.py" script:
```python run.py```
The execution results will be saved to the "fails.json" in "Results" folder.
