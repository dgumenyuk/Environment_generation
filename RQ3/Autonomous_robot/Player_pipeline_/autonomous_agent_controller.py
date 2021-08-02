#!/usr/bin/env python

'''
Script for controlling the autoomous agent, implemenmted by 
Arnold, J. and Alexander, R., 2013, September. Testing autonomous robot control software using procedural content generation. 
In International Conference on Computer Safety, Reliability, and Security (pp. 33-44). Springer, Berlin, Heidelberg.
'''

import math

from playerc import *


class WaypointController:

    def __init__(self, player_client, config):
        """Instantiates a new WaypointController class."""

        self.player_client = player_client
        self.agents = []

        # Create a WaypointFollower for each agent
        for agent in config['agents']:

            # Create a positon2d_proxy for each agent
            pp = playerc_position2d(self.player_client, config['agents'][agent]['position2d_index'])
            if pp.subscribe(PLAYERC_OPEN_MODE) != 0:
                print "failed to subscribe position2d proxy for %s" % (agent)
                print playerc_error_str()
                sys.exit(2)
            print (config['agents'][agent]['waypoints'])

            # Allocate each agent a WaypointFollower
            self.agents.append(WaypointFollower(name=agent,
                                                waypoints=config['agents'][agent]['waypoints'],
                                                position2d_proxy=pp,
                                                waypoint_distance_tolerance=config['waypoint-distance-tolerance']))

    def Start(self):
        """Starts the controller for all agents."""

        # Keep updating until all agents have completed their waypoints
        all_finished = False
        while not all_finished:
            all_finished = True
            self.player_client.read()
            for agent in self.agents:
                all_finished = agent.update() and all_finished


class WaypointFollower():

    def __init__(self, name, waypoints, position2d_proxy, waypoint_distance_tolerance):
        """Instantiates a new WaypointFollower class."""

        self.name = name
        self.waypoints = waypoints
        self.pp = position2d_proxy
        self.waypoint_distance_tolerance = waypoint_distance_tolerance

        self.active_waypoint_index = 0
        self.active_waypoint = self.waypoints[self.active_waypoint_index]
        self.first_update = True
        self.finished = False
        self.last_read = None

    def get_heading(self, curr, next):
        return math.atan2(next['y'] - curr['y'], next['x'] - curr['x']) - (math.pi / 2)

    def update(self):
        """Informs the agent that its position has changed."""

        # If the agent has already reached the
        # last waypoint it doesn't need to update
        if self.finished:
            return True

        # Skip if the proxy don't have any [new] data
        if (self.pp.info.datatime == 0) or  \
           (self.pp.info.datatime == self.last_read):
            return False

        self.last_read = self.pp.info.datatime

        # If this is the first update then head toward the first waypoint
        if self.first_update:
            self.pp.set_cmd_pose(self.active_waypoint['x'],
                                 self.active_waypoint['y'],
                                 self.get_heading({'x': self.pp.px, 'y': self.pp.py}, self.active_waypoint),
                                 1)
            self.first_update = False
            return False

        # Calculate how far the agent is from its current waypoint
        dist = math.hypot(self.pp.px - self.active_waypoint['x'],
                          self.pp.py - self.active_waypoint['y'])

        # Has it reached it yet?
        if dist < self.waypoint_distance_tolerance:

            # If all waypoints have been reached, stop the agent and return True
            if (self.active_waypoint_index + 1) >= len(self.waypoints):
                self.pp.set_cmd_vel(0.0, 0.0, 0.0, 0)
                self.pp.enable(False)  # redundant?
                self.finished = True
                return True

            # Otherwise select the next waypoint
            prev_waypoint = self.active_waypoint
            self.active_waypoint_index += 1
            self.active_waypoint = self.waypoints[self.active_waypoint_index]

            # ...and drive to it
            self.pp.set_cmd_pose(self.active_waypoint['x'],
                                 self.active_waypoint['y'],
                                 self.get_heading(prev_waypoint, self.active_waypoint),
                                 1)

        # Still have waypoints to visit
        return False


if __name__ == '__main__':

    import getopt
    import json
    import os.path
    import sys

    hostname = "localhost"
    port = 6665

    def usage():
        print "usage: %s [-h] [-p] CONFIG_FILE" % (os.path.basename(sys.argv[0]))
        print ""
        print "Player client to allow autonomous agents to follow waypoints."
        print ""
        print "positional arguments:"
        print " CONFIG_FILE    the file containing agent definitions"
        print ""
        print "optional arguments:"
        print " -h,--hostname  the player server hostname (default: %s)" % (hostname)
        print " -p,--port      the player server port (default: %d)" % (port)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:p:", ["hostname=", "port="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--hostname"):
            hostname = a
        elif o in ("-p", "--port"):
            port = a
        else:
            assert False, "unhandled option"

    if len(args) != 1:
        usage()
        sys.exit(2)

    # Attempt to parse the config file
    config = json.load(open(args[0], 'r'))

    # Instantiate a player client
    client = playerc_client(None, hostname, port)
    if client.connect() != 0:
        print playerc_error_str()
        sys.exit(2)

    # Instantiate a WaypointController
    controller = WaypointController(player_client=client, config=config)

    # Start the clients for the defined robots
    controller.Start()
