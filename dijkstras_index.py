# debugging = False
from eastOCD import get_text_boxes
import cv2
import pdb
import heapq
"""
global_matches: dictionary

1. start at any point and look upward. do litmus test of at least 30 long, 3 ccw, not crooked
2. assume we're on an outer edge of graphic if we pass the litmust test -> dijkstra's follow it till ends, always going cw. 
3. at a break add "endpoint" to minheap. search it till an edge is found, add to minheap
4. explore minheap, removing finished edges. 

todo - 
1. clean up bad edges - just kill em if we hit bad (like 100...) weight/distance w/ min distance of 50 or something.. or min weight of 1000 (5 black pxs)
    ret val self.evaluate(retVal) if True do heapq.push
3. terminate search with starting coord discovered...
    -easy:  matches[c] = founder
    if c in matches AND distance > 200 and matches[c].parentChain[1] != self.parentChain[1]
    words - if the coord has been discovered already, adn the path to find it is over 200, then only requirement is that it's not part of some obscure branch, thus no shared relatives other than the very root

"""
tm = "targetMedia\\"
testFns = ["picOriginal1.png", "picOriginal10.png", "picOriginal11.png", "picOriginal12.png", "picOriginal13.png", "picOriginal14.png", "picOriginal15.png", "picOriginal16.png", "picOriginal17.png", "picOriginal18.png", "picOriginal19.png", "picOriginal2.png", "picOriginal20.png", "picOriginal21.png", "picOriginal22.png", "picOriginal23.png", "picOriginal24.png", "picOriginal25.png", "picOriginal26.png", "picOriginal27.png", "picOriginal28.png", "picOriginal29.png", "picOriginal3.png", "picOriginal30.png", "picOriginal31.png", "picOriginal32.png", "picOriginal33.png", "picOriginal34.png", "picOriginal35.png", "picOriginal36.png", "picOriginal37.png", "picOriginal38.png", "picOriginal39.png", "picOriginal4.png", "picOriginal40.png", "picOriginal41.png", "picOriginal42.png", "picOriginal43.png", "picOriginal44.png", "picOriginal45.png", "picOriginal46.png", "picOriginal47.png", "picOriginal48.png", "picOriginal49.png", "picOriginal5.png", "picOriginal50.png", "picOriginal51.png", "picOriginal52.png", "picOriginal53.png", "picOriginal54.png", "picOriginal55.png", "picOriginal56.png", "picOriginal57.png", "picOriginal58.png", "picOriginal59.png", "picOriginal6.png", "picOriginal60.png", "picOriginal61.png", "picOriginal62.png", "picOriginal63.png", "picOriginal64.png", "picOriginal65.png", "picOriginal66.png", "picOriginal67.png", "picOriginal68.png", "picOriginal69.png", "picOriginal7.png", "picOriginal70.png", "picOriginal71.png", "picOriginal72.png", "picOriginal8.png", "picOriginal9.png"]
exampleFn = testFns[0]
exampleStartCoord = (542, 547)
exampleOrigin = (542, 560)
exampleDxdy = (0, -1)
imD = tm + exampleFn
global_matches = {}
pic = cv2.imread(imD)
edges = cv2.Canny(pic, 90, 100, L2gradient=True)

#this class is just helper functions for getting err numbers and finding neighbouring pixels.  
class EdgeExplorer:
    debugging = False
    allowPdb = False
    def __init__(self, path, debugging=False):
        self.debugging = debugging
        self.path = path
        self.pic = cv2.imread(path)
        self.H, self.W = self.pic.shape[:2]
        self.edges = cv2.Canny(self.pic, 90, 100, L2gradient=True)
        self.allowPdb = False
        self.debugging = False
    
    def __lt__(self, other):
        return self.weight < other.weight

    def check_termination(self, other):
        foundAMatch = False
        try:
            if self.parentChain[-2] != other.parentChain[-2] and self.distance > 50:
                #a match is found! since the two have different paths to the root. 
                foundAMatch = True
        except IndexError: #should be except nameerror or somethign...
            #the above throws an error if -2 is out of range, which totally counts
            if self.distance > 50:
                foundAMatch = True
        if foundAMatch:
            #go through all edges in both chains and add up the coordinates.
            matchedCoords = {}
            for el in self.parentChain:
                if el.T == "Edge":
                    for c in el.coords:
                        matchedCoords[c] = True
            for el in other.parentChain:
                if el.T == "Edge":
                    for c in el.coords:
                        matchedCoords[c] = True
            return ("TERMINATED", matchedCoords)

    def keep_it_in_bounds(self, _x, _y, leftwardX=0, upperY=0, rightwardX=1280, lowerY=720):
        """
        todo - not using the bounds above
        """
        _rx = _x
        _ry = _y
        _rx = 0 if _x < 0 else _rx
        _rx = self.W-1 if _x > self.W-1 else _rx
        _ry = 0 if _y < 0 else _ry
        _ry = self.H-1 if _y > self.H-1 else _ry
        # if self.debugging and (_rx != _x or _ry != _y):
        #     inp = (_x, _y)
        #     ret = (_rx, _ry)
        #     print("rewriting coords w/ input of (%d,%d) and return of (%d,%d)" % (inp[0], inp[1], ret[0], ret[1]))
        return (_rx, _ry)

    def get_next_ccw_coord(self, dxdy, radius):
        """
        basically - if left go down, if down go right, if right go up, if up go left. 
        in >
            dxdy: (x, y) - where the last match was
            radius: int -max |dx| or |dy|
        out > 
            next dxdy to look
        """
        left = False
        bottom = False
        right = False
        top = False
        dx = dxdy[0]
        dy = dxdy[1]
        #if left then go down
        if dx == -radius and dy != radius:
            left = True
            dy += 1
        #if top go left
        elif dy == -radius and dx != -radius:
            top = True
            dx -= 1
        #if right go up
        elif dx == radius and dy != -radius:
            right = True
            dy -= 1
        #if bottom then go right
        elif dy == radius and dx != radius:
            down = True
            dx += 1
        return (dx, dy)
        
    def find_cw_neighbour(self, centerCoord, dxdy, matches):
        """
        similar to check_neighbours_recursively except it isn't recursive and checks counterclockwise from starting dxdy, only returning the last val it finds (the most clockwise)
        inputs: 
            (x,y) to look around, 
            dx, dy to check first 
        outputs: new_dxdy
        bug: if both dxdy are 0 this won't go anywhere i think?
        error - this must be returning bad options when going right or up
        """
        c = (neighbour_column, neighbour_row) = (centerCoord[0] + dxdy[0], centerCoord[1] + dxdy[1])
        last_dxdy = dxdy
        new_dxdy = dxdy
        foundAMatch = False
        for i in range(8):
            new_dxdy = self.get_next_ccw_coord(new_dxdy, 1)
            c = (neighbour_column, neighbour_row) = (centerCoord[0] + new_dxdy[0], centerCoord[1] + new_dxdy[1])
            if c != self.keep_it_in_bounds(c[0], c[1]): continue
            if self.edges[neighbour_row][neighbour_column] > 0 and (not c in matches):
                last_dxdy = new_dxdy #just keep rewriting this val, the last ccw coord to match is the most cw coordinate
                foundAMatch = True
        if foundAMatch:
            return last_dxdy
        else: return False

    def find_mult_cw_neighbours(self, centerCoord, dxdy, matches):
        """
        similar to check_neighbours_recursively except it isn't recursive and checks counterclockwise from starting dxdy, only returning the last val it finds (the most clockwise)
        inputs: 
            (x,y) to look around, 
            dx, dy to check first 
        outputs: [new_dxdys] most clockwise coordinate is last so you can  just pop it off.
        bug: if both dxdy are 0 this won't go anywhere i think?
        """
        ret_dxdys = []
        c = (neighbour_column, neighbour_row) = (centerCoord[0] + dxdy[0], centerCoord[1] + dxdy[1])
        last_dxdy = dxdy
        new_dxdy = dxdy
        for i in range(8):
            new_dxdy = self.get_next_ccw_coord(new_dxdy, 1)
            c = (neighbour_column, neighbour_row) = (centerCoord[0] + new_dxdy[0], centerCoord[1] + new_dxdy[1])
            if c != self.keep_it_in_bounds(c[0], c[1]): continue
            if self.edges[neighbour_row][neighbour_column] > 0:
                if c in matches:
                    other = matches[c]
                    self.check_termination(other)
                else:
                    ret_dxdys.append(new_dxdy) #just keep rewriting this val, the last ccw coord to match is the most cw coordinate
                    matches[c] = self #rewritten by the calling function
        return ret_dxdys

    def get_clockwiseness_err(self, centerCoord, currentCoord, dxdy):
        # if self.debugging: print("getting clockwiseness")
        """
        plan - basically treat the top left corner of the east text bbox like the center of a circle, and if the trajectory of the line doesn't go perpendicular cw then return 1
        ex / if we're in the top left of the graphic - then cw-ish is upward or rightward, but i decided to only allow the topright, and neighboring slots to count.
        input:
            >centerCoord - (x, y) the top corner of the textbox we're starting this whole entire program from
            >currentCoord - (x, y) the coordinate we're exploring
            >dxdy - (dx, dy) the relative location of this new pixel from it's original search pixel
        output:
            just 1 if there's an error to add to the running total of errors
            0 if the pixel is in a clockwise-ish place.
        """
        rise = currentCoord[1] - centerCoord[1]
        run = currentCoord[0] - centerCoord[0]
        rise = 1 if rise > 0 else -1
        run = 1 if run > 0 else -1
        if rise < 0 and run < 0:
            #top left of graphic - allow top right coords
            # so not not leftward or downward
            if dxdy[0] == -1 or dxdy[1] == 1: return 1
            else: return 0
        if rise < 0 and run > 0:
            #top right allow downright, so not leftward upward
            if dxdy[0] == -1 or dxdy[1] == -1: return 1
            else: return 0
        if rise > 0 and run > 0:
            #bottom right allow downLeft, so not rightward upward
            if dxdy[0] == 1 or dxdy[1] == -1: return 1
            else: return 0
        if rise > 0 and run < 0:
            #bottom left allow upleft, so not rightward downard
            if dxdy[0] == 1 or dxdy[1] == 1: return 1
            else: return 0

    def display(self, _keys):
        edgeCpy = self.edges.copy()
        if self.debugging: print('displaying')
        if type(_keys) == dict:
            for coord in _keys.keys():
                # if self.debugging: print(coord)
                cv2.rectangle(edgeCpy, coord, coord, 255, 3)
        elif type(_keys) == list:
            for coord in _keys:
                cv2.rectangle(edgeCpy, coord, coord, 255, 3)
        else:
            print("error with keys, please give either list with coordinate tuples or a dictionary with coordinate tuples for the keys")
        cv2.imshow("EdgeExplorer", edgeCpy)
        keyPressed = cv2.waitKey() & 0xFF
        cv2.destroyAllWindows()
        if keyPressed == ord("d"):
            print("d detected - debugging")
            self.allowPdb = True
            self.debugging = True
            import pdb
        elif keyPressed == ord("s"):
            cv2.imwrite(tm + "picANewName.png", edgeCpy)

class Endpoint(EdgeExplorer):
    """
    when an edge ends start this and explore outwards

    problem - what will weight be here.
        every time a weight changes in a parent? this changes. why would parent change? It wouldn't
            edges must be at an endpoint to initialize this
            an endpoints weight at time of discovery is this
    """
    # radius = 1 #always at least 1 since default check is only for neighbours
    # explored = {}
        
    def __init__(self, startingCoord, parent=None, edges=edges, debugging=False):
        """
        startingCoord is supposed to be apoin in the middle of the graphic?
        parent is whatever edge or endpoint that discovered this
        edges is the edge picture from cv2.Canny edge detection
        """
        self.radius = 1
        self.explored = {}
        self.preweight = parent.weight
        self.weight = parent.weight + 200*self.radius
        self.distance = parent.distance
        self.sc = startingCoord
        self.parent = parent #once we match to the original coordinate we can climb this chain.
        self.edges = edges
        self.debugging = debugging
        self.H, self.W = self.edges.shape[:2]
        self.allowPdb = False
        self.T = type(self).__name__
        self.parentChain = [self]
        currentParent = parent
        while True:
            if currentParent == None: break
            else:
                self.parentChain.append(currentParent)
                currentParent = currentParent.parent

    def next(self, matches=global_matches):
        self.radius += 1

        x, y = self.sc
        edges = self.edges
        radius = self.radius

        initialDxdy = (radius, 0)
        new_dxdy = self.get_next_ccw_coord(initialDxdy, radius)
        new_edges = [self]
        
        while True:
            c = (_x, _y) = self.keep_it_in_bounds(x + new_dxdy[0], y + new_dxdy[1])
            if self.debugging: 
                print(c)
                print(new_dxdy)
            self.explored[c] = True
            if edges[_y][_x] > 0:
                if c in matches:
                    #check if we should terminate the algo
                    other = matches[c]
                    term = self.check_termination(other)
                    if type(term) == tuple:
                        if term[0] == "TERMINATED":
                            return term
                else:
                    _edge = Edge(c, exampleOrigin, self.parent.dxdy, self, edges)
                    new_edges.append(_edge)
                    matches[c] = self
            new_dxdy = self.get_next_ccw_coord(new_dxdy, radius)
            if initialDxdy == new_dxdy:
                break
        self.weight = self.preweight + self.radius * 200 #do this at the end so that newly found edges don't get exagerated weight
        self.distance += 1 #should only do if match is found. 
        return new_edges

class Edge(EdgeExplorer):
    # root_sc = 0
    # sc = 0
    # parent = 0
    # weight = 0
    # distance = 0
    # dxdy = 0

    def __init__(self, sc, root_sc, dxdy, parent, edges, debugging = False):
        self.coords = []
        self.sc = sc
        self.root_sc = root_sc
        self.currentCoord = sc
        self.dxdy = dxdy
        self.parent = parent
        self.edges = edges
        self.H, self.W = self.edges.shape[:2]
        self.debugging = debugging
        self.T = type(self).__name__
        
        self.parentChain = [self]
        currentParent = parent
        if parent == None: 
            self.weight = 0
            self.distance = 0
        else: 
            self.weight = parent.weight
            self.distance = parent.distance
            while True:
                if currentParent == None: break
                else:
                    self.parentChain.append(currentParent)
                    currentParent = currentParent.parent
        
    
    def __lt__(self, other):
        return self.weight < other.weight

    def next(self, matches=global_matches):
        # so here, could find branches, add to dict, and if you have mults then add new edges... 
        # return a list of edges to put in heap - 
        hold_dxdy = self.dxdy
        dxdy_list = self.find_mult_cw_neighbours(self.currentCoord, self.dxdy, global_matches)
        if dxdy_list == True: return True #this fires because one of the edges discovered had a different lineage - so it's the end of the algo
        self.dxdy # to do how to handle this. if we have 1 we're returning this edge, if we have a branch, we're returning all new edges
        #adjust weight - 1 for new px, 5 if it's not in the same relative position as the last, and 15 if it's counterclockwise
        if len(dxdy_list) == 0:
            #find_cw_nb returns this when there are no neighbours left to return, thus the calling function must remove this and initiate a new endpoint.
            #Endpoint(self.currentCoord, self, self.edges)
            end = Endpoint(self.currentCoord, self, edges)
            return [end] #todo handle this insta
        elif len(dxdy_list) == 1:
            self.dxdy = dxdy_list[0]
            self.weight += 1 
            self.distance += 1
            if hold_dxdy != self.dxdy:
                self.weight += 50
            self.weight += self.get_clockwiseness_err(self.root_sc, self.currentCoord, self.dxdy) * 150
            self.currentCoord = (self.currentCoord[0] + self.dxdy[0], self.currentCoord[1] + self.dxdy[1])
            matches[self.currentCoord] = self
            self.coords.append(self.currentCoord)
            return([self])
        elif len(dxdy_list) > 1:
            new_edges = []
            for _dxdy in dxdy_list:
                sc = (self.currentCoord[0] + _dxdy[0], self.currentCoord[1] + _dxdy[1])
                matches[sc] = self
                new_edge = Edge(sc, exampleOrigin, _dxdy, self, self.edges)
                new_edges.append(new_edge)
            return new_edges

class DijkstrasContainer(EdgeExplorer):
    wdt = 40
    md = 0
    def __init__(self, edgeList):
        self.edges = edges
        if type(edgeList) == list: 
            heapq.heapify(edgeList)
            self.heap = edgeList
        else: self.heap = [edgeList]
    
    def run_one(self):
        minItem = heapq.heappop(self.heap)
        res = minItem.next()
        if len(res) > 0:
            if res[0] == "TERMINATED": return res
            for edge in res:
                #next returns [self, other_new_items_discovered]
                heapq.heappush(self.heap, edge)
        return ("CONTINUE", minItem)

    def run_mult(self, n):
        for i in range(n):
            minItem = self.run_one()
        self.display(global_matches)
    
    def run_all(self):
        count = 0
        while True:
            count += 1
            potential_booted = d.run_one()
            if type(potential_booted) == tuple:
                if potential_booted[0] == "TERMINATED": 
                    #this is the go. run_one()[0] = TERMINATED
                    print("GOOD WORK!!!!!!!!===============================================================")
                    self.display(potential_booted[1])
                    break

edge = Edge(exampleStartCoord, exampleOrigin, exampleDxdy, None, edges, debugging=False)
## global_matches[exampleStartCoord] = edge
d = DijkstrasContainer(edge)
d.run_all()