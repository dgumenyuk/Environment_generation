#!/usr/bin/env python

'''
Script for detecting events of the autoomous agent, implemenmted by 
Arnold, J. and Alexander, R., 2013, September. Testing autonomous robot control software using procedural content generation. 
In International Conference on Computer Safety, Reliability, and Security (pp. 33-44). Springer, Berlin, Heidelberg.
Original library implemented by:  https://github.com/Rezzie/eventdetector for more information.
'''


import logging

from playerc import *

import monitors


class EventDetector:

    def __init__(self, player_client, config):
        """Instantiates a new EventDetector class."""

        self.player_client = player_client
        self.proxies = {}
        self.state = {}
        self.monitors = []

        # Instantiate monitors for the desired events
        logging.info("Instantiating event monitors...")
        for event, properties in sorted(config['events'].iteritems()):

            monitor = None

            if event == 'loitering':
                logging.debug("  Loiter...")
                monitor = monitors.LoiterMonitor(config=properties)
                monitor.Loitering += self.OnAgentLoitering
                monitor.StoppedLoitering += self.OnAgentStoppedLoitering

            elif event == 'stall':
                logging.debug("  Stall...")
                monitor = monitors.StallMonitor()
                monitor.Stalled += self.OnAgentStall
                monitor.Unstalled += self.OnAgentUnstall

            elif event == 'unsafe_proximity':
                logging.debug("  Unsafe Proximity...")
                monitor = monitors.UnsafeProximityMonitor(config=properties)
                monitor.EnteredSafetyRadius += self.OnEnteredSafetyRadius
                monitor.LeftSafetyRadius += self.OnLeftSafetyRadius

            elif event == 'waypoint_arrival':
                logging.debug("  Waypoint Arrival...")
                monitor = monitors.WaypointArrivalMonitor(config=properties)
                monitor.RouteCompleted += self.OnRouteCompleted
                monitor.WaypointArrived += self.OnWaypointArrived

            if monitor is not None:
                self.monitors.append(monitor)

        logging.info("Creating client proxies...")
        max_agent_len = reduce(lambda x, y: max(x, len(y)), config['agents'].iterkeys(), 0)
        for agent, properties in sorted(config['agents'].iteritems()):

            # Create a positon2d_proxy for each agent
            pp = playerc_position2d(self.player_client, properties['position2d_index'])
            if pp.subscribe(PLAYERC_OPEN_MODE) != 0:
                print "failed to subscribe position2d proxy for %s" % (agent)
                print playerc_error_str()
                sys.exit(2)

            self.proxies[agent] = pp
            logging.debug("  %s = position2d:%d", str.ljust(str(agent), max_agent_len), properties['position2d_index'])

    def Start(self):
        """Starts monitoring Player for events."""

        logging.info("Starting client read loop...")

        # Start by printing out route starts
        for monitor in self.monitors:
            if not isinstance(monitor, monitors.WaypointArrivalMonitor):
                continue
            for agent in sorted(monitor.waypoints.keys()):
                logging.info("[EVENT] '%s' starting route of %d waypoint(s)",
                  agent,
                  len(monitor.waypoints[agent]))

        while True:

            # Fetch new data from player
            fresh_data = False
            self.player_client.read()

            # Update world state for each model
            for agent, proxy in self.proxies.iteritems():

                # Skip if the proxy don't have any data
                if proxy.info.datatime == 0:
                    continue

                if agent not in self.state:
                    self.state[agent] = {'time': None, 'pos': None, 'vel': None, 'stall': None}

                # Fetch the latest data from the proxy
                time = proxy.info.datatime
                if (time != self.state[agent]['time']):
                    # Data is new; update the cache
                    self.state[agent]['time'] = time
                    self.state[agent]['pos'] = (proxy.px, proxy.py, proxy.pa)
                    self.state[agent]['vel'] = (proxy.vx, proxy.vy, proxy.va)
                    self.state[agent]['stall'] = proxy.stall
                    fresh_data = True

            # If there was no new state there's nothing to do
            if not fresh_data:
                continue

            # Otherwise update the monitors with the new state
            for monitor in self.monitors:
                monitor.update(self.state)

    def OnAgentLoitering(self, state, agent, loiter_position):
        """Called when an agent loiters in an area."""

        logging.info("[EVENT] '%s' is loitering around (x: %f, y: %f) at %fs",
          agent,
          loiter_position[0],
          loiter_position[1],
          state[agent]['time'])

    def OnAgentStoppedLoitering(self, state, agent, duration):
        """Called when an agent stops loitering."""

        logging.info("[EVENT] '%s' stopped loitering at %fs after %fs",
          agent,
          state[agent]['time'],
          duration)

    def OnAgentStall(self, state, agent):
        """Called when an agent stalls."""

        logging.info("[EVENT] '%s' stalled at (x: %f, y: %f, yaw: %f) at %fs",
          agent,
          state[agent]['pos'][0],
          state[agent]['pos'][1],
          state[agent]['pos'][2],
          state[agent]['time'])

    def OnAgentUnstall(self, state, agent, duration):
        """Called when an agent stalls."""

        logging.info("[EVENT] '%s' unstalled from (x: %f, y: %f, yaw: %f) at %fs after %fs",
          agent,
          state[agent]['pos'][0],
          state[agent]['pos'][1],
          state[agent]['pos'][2],
          state[agent]['time'],
          duration)

    def OnEnteredSafetyRadius(self, state, agent, other_agent):
        """Called when two agents enter an unsafe proximity."""

        logging.info("[EVENT] '%s' and '%s' entered unsafe proximity ('%s' at (x: %f, y: %f, yaw: %f), '%s' at (x: %f, y: %f, yaw: %f)) at %fs",
          agent,
          other_agent,
          agent,
          state[agent]['pos'][0],
          state[agent]['pos'][1],
          state[agent]['pos'][2],
          other_agent,
          state[other_agent]['pos'][0],
          state[other_agent]['pos'][1],
          state[other_agent]['pos'][2],
          state[agent]['time'])

    def OnLeftSafetyRadius(self, state, agent, other_agent, duration, closest_approach, closest_approach_time):
        """Called when two agents are no longer in an unsafe proximity."""

        logging.info("[EVENT] '%s' and '%s' left unsafe proximity ('%s' at (x: %f, y: %f, yaw: %f), '%s' at (x: %f, y: %f, yaw: %f)) at %fs after %fs (closest approach = %fm at %fs)",
          agent,
          other_agent,
          agent,
          state[agent]['pos'][0],
          state[agent]['pos'][1],
          state[agent]['pos'][2],
          other_agent,
          state[other_agent]['pos'][0],
          state[other_agent]['pos'][1],
          state[other_agent]['pos'][2],
          state[agent]['time'],
          duration,
          closest_approach,
          closest_approach_time)

    def OnRouteCompleted(self, state, agent):
        """Called when an agent completes its route."""

        logging.info("[EVENT] '%s' completed its route at %fs",
          agent,
          state[agent]['time'])

    def OnWaypointArrived(self, state, agent, waypoint_number, route):
        """Called when an agent arrives at a waypoint."""

        logging.info("[EVENT] '%s' reached waypoint %d (x: %f, y: %f) of %d (%d%%) at %fs",
          agent,
          waypoint_number + 1,
          route[waypoint_number]['x'],
          route[waypoint_number]['y'],
          len(route),
          ((waypoint_number + 1) * 100.0) / len(route),
          state[agent]['time'])


if __name__ == "__main__":

    import json
    import sys
    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [options] DEFINITIONS_FILE")
    parser.add_option("--host", default="localhost", dest="hostname", help="hostname of player server             [default: %default]", metavar="HOSTNAME")
    parser.add_option("--port", default=6665, dest="port", help="port player server is listening to    [default: %default]", metavar="PORT")
    parser.add_option("--log", default="INFO", dest="loglevel", help="verbosity of logging output           [default: %default]", metavar="LEVEL")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    # Ensure a valid logging level was specified
    loglevel = getattr(logging, options.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        sys.exit("fatal: invalid log level '%s' (valid: DEBUG, INFO, WARNING, ERROR, CRITICAL)" % options.loglevel)

    # Prepare the log file
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s: %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%SZ',
                        level=loglevel)

    # Attempt to parse the definitions file
    logging.info("Parsing definitions from '%s'...", args[0])
    config = json.load(open(args[0], 'r'))

    # Instantiate a player client
    logging.info("Connecting to Player server at '%s:%d'...", options.hostname, options.port)
    client = playerc_client(None, options.hostname, options.port)
    if client.connect() != 0:
        print playerc_error_str()
        sys.exit(2)

    # Instantiate the event detector
    detector = EventDetector(player_client=client, config=config)

    # Start monitoring for events
    detector.Start()
