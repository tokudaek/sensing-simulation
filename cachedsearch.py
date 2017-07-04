#!/usr/bin/python3
""" A* implementation by tokudaek
"""

import sys
import heapq
import math
import numpy as np
import operator

import pprint
import utils
import search

MAX = 9999999

class Cachedsearch:
    """Caches paths between crossings
    """

    def __init__(self, graph, waypoints):
        self.graph = graph
        self.waypoints = waypoints
        self.wpspaths = self.get_paths_btw_all_wps(graph, waypoints)
        #import pprint
        #pprint.pprint(self.wpspaths)
        #input()
    
    def get_wps_path(self, wp1, wp2):
        cr = sorted([wp1, wp2], key=operator.itemgetter(0, 1))
        return self.wpspaths[cr[0]][cr[1]]

    def choose_random_waypoint(self, waypoints):
        """Choose the first waypoint of the list and extracts just
        the position
    
        Args:
        waypoints(list of tuples): each element contain (cost, pos)
    
        Returns:
        tuple: position of first element of the list
        """

        return waypoints[0][1]

    def choose_closest_waypoints(self, wps1, wps2):
        """Choose the nearest waypoints, given two sets of waypoints
    
        Args:
        waypoints1(lists of tuples): each element is a tuple (cost, pos)
        waypoints2(lists of tuples): each element is a tuple (cost, pos)
    
        Returns:
        tuple of tuples: return the positions of the two closest waypoints
    
        Raises:
        """
    
        _min = 99999
        closestwps = []

        for _, wp1 in wps1:
            for _, wp2 in wps2:
                potentialmin = len(self.get_wps_path(wp1, wp2))
                if potentialmin > _min:
                    continue
                else:
                    _min = potentialmin
                    closestwps = wp1, wp2
        return closestwps

    def get_path(self, start, goal):
        """Find a path using the cached paths between waypoints
    
        Args:
        start(tuple): start
        goal(tuple): goal
    
        Returns:
        list of tuples: list of paths from end to beginning
        """

        if start == goal: return []

        startiswp = goaliswp = False
        if start in self.waypoints: startiswp = True
        if goal in self.waypoints: goaliswp = True

        if startiswp and goaliswp:
            return list(self.get_wps_path(start, goal))

        swps = self.get_nearby_crossings(self.graph, start, self.waypoints)
        gwps = self.get_nearby_crossings(self.graph, goal, self.waypoints)

        if startiswp and not goaliswp:
            swayp = self.choose_random_waypoint(swps)
            wayppath = self.get_wps_path(start, swayp)
            finalpath = search.get_astar_path(self.graph, swayp, goal)
            _path = finalpath + wayppath
        elif not startiswp and not goaliswp:
            swayps = [ s[1] for s in swps ]
            gwayps = [ g[1] for g in gwps ]
            common = []
            for aux in swayps:
                if aux in gwayps: common.append(aux)
            
            if len(common) == 0:
                #print(swps)
                #print(gwps)
                swayp, gwayp = self.choose_closest_waypoints(swps, gwps)

                startpath = search.get_astar_path(self.graph, start, swayp)
                wayppath = self.get_wps_path(swayp, gwayp)

                goalpath = search.get_astar_path(self.graph, gwayp, goal)
                _path = goalpath + wayppath + startpath
            else:
                goalpath = search.get_astar_path(self.graph, start, goal)
                _path = goalpath
        elif not startiswp and goaliswp:
            swayp = self.choose_random_waypoint(gwps)
            startpath = search.get_astar_path(self.graph, start, swayp)
            wayppath = self.get_wps_path(swayp, goal)
            _path =  startpath + wayppath
        else:
            print('error occured')
            _path = []
        return _path
    
    def get_nearby_crossings(self, graph, start, crossings, maxcrossings=2):
        """Get reachable crossings according to graph from @start position
    
        Args:
        graph(dict of list): position and list of neighbours
        start(tuple): position of the starting node
        crossings(list): list of crossings
    
        Returns:
        list of tuple: list of crossings nearby
        """

        ncrossings = []
        visitted = set()
        _crossings = crossings.copy()

        if start in _crossings: _crossings.discard(start)

        for i in range(maxcrossings):
            _path = search.get_dfs_path(graph, start, _crossings, visitted)

            if not _path: break

            v = _path[0]
            cost = len(_path)
            visitted.add(v)

            if ncrossings and cost < ncrossings[0][0]:
                ncrossings.insert(0, (cost, v))
            else:
                ncrossings.append((cost, v))
            _crossings.discard(v)

        return ncrossings


    def get_paths_btw_all_wps(self, graph, crossings):
        """Get paths of all combinations of waypoints
    
        Args:
        graph(dict of list): position and respective neighbours
        crossings(list): list of crossings
    
        Returns:
        dict of lists: tuple of tuple as keys and list (path) as a value
        """
    
        paths = {}
        crossingpaths = {}
        cr = sorted(list(crossings), key=operator.itemgetter(0, 1))
        ncrossings = len(crossings)

        for i in range(ncrossings):
            crss1 = cr[i]
            crossingpaths[crss1] = {}
            for j in range(i + 1, ncrossings):
                crss2 = cr[j]
                finalpath = search.get_astar_path(graph, crss1, crss2)
                crossingpaths[crss1][crss2] = finalpath
        return crossingpaths

##########################################################
def main():
    import time
    t0 = time.time()

    #start = (4, 10)
    #goal  = (7, 20)
    start = (16, 9)
    goal  = (23, 16)
    image = 'maps/toy5.png'
    print(start)
    print(goal)

    #import pprint
    crossings = utils.get_crossings_from_image(image)
    #pprint.pprint(crossings)
    #pprint.pprint(crossings)
    x = [ z[0] for z in crossings]
    y = [ z[1] for z in crossings]
    #import matplotlib.pyplot as plt
    #plt.scatter(y, x)
    #plt.gca().invert_yaxis()
    #plt.show()
    #return
    graph = utils.get_adjmatrix_from_image(image)
    search = Cachedsearch(graph, crossings)
    _path = search.get_path(start, goal)
    pprint.pprint(_path)

    print('Total time:{}'.format(time.time() - t0))
if __name__ == "__main__":
    main()

