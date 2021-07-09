In this section we provide the code to run the tools for virtual road generation to test the vehicle lane keeping assist system. The evaluation pipeline 
was provided by the [SBST2021 competition](https://github.com/se2p/tool-competition-av).
The results for the number of faults revealed given the two hour budget are summurized  in jupyter notebook the *RESULTS* folder. 
To run the nobook you can use the [tool](https://nbviewer.jupyter.org/), where you need to enter the jupyter notebook url to view it.

To launch the implmentation of our scenario generation tool, you should execute:
```bash
python competition.py --visualize-tests --time-budget 18000 --executor beamng --map-size 200 --module-name swat_gen.swat_generator --class-name SwatTestGenerator --beamng-home "path to BeamNg installation"
```****
