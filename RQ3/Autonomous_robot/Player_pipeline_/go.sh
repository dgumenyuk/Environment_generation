
#!/bin/bash
# Script to launch the scenario and collect the events occured during its execution

echo "Starting go script"

if pgrep player; then 
	echo "Killing player";
	pkill player 
	sleep 3
	fi


echo 'Starting Player/Stage...'


player player.cfg & > player.log &
sleep 5


#echo $PID1

echo 'Starting Event Detector...'
python -u eventdetector.py --log=DEBUG events.json > eventdetector.log 2> /dev/null &
PIDe=$!
sleep 4
echo "event pid"
echo $PIDe


echo 'Starting autonomous agent controller...'
python -u autonomous_agent_controller.py autonomous_agents.json > autonomous_agent_controller.log 2> /dev/null &
PID=$!
sleep 4

echo "agent pid"
echo $PID
m=0
p=300  # longest possible timeout to execute the scenario (used to stop the simulation after the robot failure occured)

while kill -0 $PID; do 
    sleep 1

    m=$((m+1))

    if [ $m -ge $p ]
    then

    	#echo $m
    	#killall player
    	echo "killing python and player"
    	if pgrep player; then pkill player ; fi
    	sleep 3
    	kill $PID
        sleep 3
        kill $PIDe
        sleep 3
    fi
done

if kill -0 $PIDe; then
echo "killing event"
kill $PIDe
sleep 3
fi
echo '******************DONE**************'
