#!/usr/bin/env python
'''
Event detection logic for simulation monitoring of autoomous agent, implemenmted by 
Arnold, J. and Alexander, R., 2013, September. Testing autonomous robot control software using procedural content generation. 
In International Conference on Computer Safety, Reliability, and Security (pp. 33-44). Springer, Berlin, Heidelberg.
'''

import math


class Event:
    # Coutesy of: http://www.valuedlessons.com/2008/04/events-in-python.html

    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        if handler in self.handlers:
            self.handlers.remove(handler)
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = getHandlerCount


class LoiterMonitor:
    def __init__(self, config):

        self.Loitering = Event()
        self.StoppedLoitering = Event()

        self.window_size = config["window-size"]  # simulation seconds
        self.loiter_radius = config["loiter-radius"]  # minimum distance trigger
        self.position_log = {}  # {agent: [[pos, time], ...]}
        self.loitering = {}  # {agent: start time}

    def update(self, state):
        """Update the monitor using the latest world state."""

        # Recalculate the loiter positions for each agent using the new state
        for agent, agent_state in state.iteritems():

            # First time we've seen this agent, not much we can do atm
            if agent not in self.position_log:
                self.position_log[agent] = [(agent_state["pos"], agent_state["time"])]
                continue

            # Save some typing
            agent_log = self.position_log[agent]

            # Truncate any positions logged outside the window
            agent_log = filter(
                lambda entry: (agent_state["time"] - entry[1]) <= self.window_size,
                agent_log,
            )

            # If there's no data, or the data we have doesn't
            # even cover the window size, we can't be loitering
            if (len(agent_log) == 0) or (
                agent_log[-1][1] - agent_log[0][1]
            ) < self.window_size:  # log duration
                self.position_log[agent].append(
                    (agent_state["pos"], agent_state["time"])
                )
                continue

            # Calculate the centre-of-mass of the position log
            # Note: Assumes regularly sampled time series data!
            com = reduce(
                lambda x, y: [(x[0][0] + y[0][0], x[0][1] + y[0][1]), 0.0], agent_log
            )
            com = (com[0][0] / len(agent_log), com[0][1] / len(agent_log))

            # Get the distance between the agent and the loitering CoM
            dist = math.hypot(
                agent_state["pos"][0] - com[0], agent_state["pos"][1] - com[1]
            )

            if dist < self.loiter_radius:
                if agent not in self.loitering:
                    # The agent has just started loitering
                    self.loitering[agent] = agent_state["time"]
                    self.Loitering(state, agent, com)
            else:
                if agent in self.loitering:
                    # The agent has just stopped loitering
                    duration = agent_state["time"] - self.loitering[agent]
                    self.StoppedLoitering(state, agent, duration)
                    del self.loitering[agent]

            # Append the agent's current position to the position log
            agent_log.append((agent_state["pos"], agent_state["time"]))


class StallMonitor:
    def __init__(self):

        self.Stalled = Event()
        self.Unstalled = Event()

        self.prev_stall = {}

    def update(self, state):
        """Update the monitor using the latest world state."""

        # See if the stall state of any agents has changed
        for agent, agent_state in state.iteritems():

            # Add new agents to the internal state
            if agent not in self.prev_stall:
                self.prev_stall[agent] = None

            if self.prev_stall[agent] is None and agent_state["stall"]:
                # The agent wasn't stalled but now is
                self.prev_stall[agent] = agent_state["time"]
                self.Stalled(state, agent)

            elif self.prev_stall[agent] is not None and not agent_state["stall"]:
                # The agent was stalled but no longer is
                duration = agent_state["time"] - self.prev_stall[agent]
                self.prev_stall[agent] = None
                self.Unstalled(state, agent, duration)


class UnsafeProximityMonitor:
    def __init__(self, config):

        self.EnteredSafetyRadius = Event()
        self.LeftSafetyRadius = Event()

        self.safety_radius = config["safety-radius"]
        self.in_proximity = {}

    def update(self, state):
        """Update the monitor using the latest world state."""

        checked = []

        # Get the distances between each of the agents
        for agent, agent_state in state.iteritems():
            for other_agent, other_state in state.iteritems():

                # Can skip this pair if it's testing an agent against itself,
                # or if this pair of agents has already been tested this update
                if (other_agent == agent) or (other_agent, agent) in checked:
                    continue

                # Save some typing
                pair = (agent, other_agent)

                # Get the distance between the two agents
                dist = math.hypot(
                    agent_state["pos"][0] - other_state["pos"][0],
                    agent_state["pos"][1] - other_state["pos"][1],
                )

                # The two agents are too close
                if dist < self.safety_radius:
                    if pair not in self.in_proximity:
                        # They're just entered an unsafe proximity
                        self.in_proximity[pair] = {
                            "start-time": agent_state["time"],
                            "closest-approach": dist,
                            "closest-approach-time": agent_state["time"],
                        }
                        self.EnteredSafetyRadius(state, agent, other_agent)
                    else:
                        # They were too close previously; are they now closer
                        # than their previous closest approach?
                        if dist < self.in_proximity[pair]["closest-approach"]:
                            self.in_proximity[pair]["closest-approach"] = dist
                            self.in_proximity[pair][
                                "closest-approach-time"
                            ] = agent_state["time"]
                else:
                    # The two agents aren't in close proximity
                    if pair in self.in_proximity:
                        # They were previously, so trigger an event
                        duration = (
                            agent_state["time"] - self.in_proximity[pair]["start-time"]
                        )
                        closest_approach = self.in_proximity[pair]["closest-approach"]
                        closest_approach_time = self.in_proximity[pair][
                            "closest-approach-time"
                        ]
                        self.LeftSafetyRadius(
                            state,
                            agent,
                            other_agent,
                            duration,
                            closest_approach,
                            closest_approach_time,
                        )
                        del self.in_proximity[pair]

                checked.append(pair)


class WaypointArrivalMonitor:
    def __init__(self, config):

        self.WaypointArrived = Event()
        self.RouteCompleted = Event()

        self.distance_tolerance = config["distance-tolerance"]
        self.waypoints = config["agents"]
        self.waypoints_reached = {}
        for agent in config["agents"]:
            self.waypoints_reached[agent] = 0

    def update(self, state):
        """Update the monitor using the latest world state."""

        # See if any agents have reached a waypoint or completed their route
        for agent, agent_state in state.iteritems():

            # Skip this agent if it's already completed its route
            if self.waypoints_reached[agent] == len(self.waypoints[agent]):
                continue

            # Calculate how far the agent is from its current waypoint
            active_waypoint = self.waypoints[agent][self.waypoints_reached[agent]]
            dist = math.hypot(
                agent_state["pos"][0] - active_waypoint["x"],
                agent_state["pos"][1] - active_waypoint["y"],
            )

            if dist < self.distance_tolerance:

                # The agent has reached its current waypoint
                self.WaypointArrived(
                    state, agent, self.waypoints_reached[agent], self.waypoints[agent]
                )

                # Has the agent now completed its route?
                self.waypoints_reached[agent] += 1
                if self.waypoints_reached[agent] == len(self.waypoints[agent]):
                    self.RouteCompleted(state, agent)
