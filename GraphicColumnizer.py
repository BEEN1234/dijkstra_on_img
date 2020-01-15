import cv2
"""
copied from ../graphicsPull/columnizer and changed
todo
    - clean up search for edges
    - the best test of it being an edge, is the movement mostly wrapping around our first pos. 
    - at branches go cw
        -feed get nbrs a dx,dy val, check it, and if nothing then get stack of ccw neighbours. last entry is most cw
"""

class EdgesFinder:
    def __init__(self, path, debugging=False):
        self.debugging = debugging
        self.path = path
        self.pic = cv2.imread(path)
        self.H, self.W = self.pic.shape[:2]
        self.edges = cv2.Canny(self.pic, 90, 100, L2gradient=True)

    def search_for_edges(self, startCoord, dxdy, matches):
        """
        in 
            >startCoord: (x, y) - image coordinates
            >dxdy: (dx, dy) - (-1) for left or up, and 1 for right or down
            >matches: dictionary of (x, y): True's for matches
        out: a list of data for each edge found
            >[[startCoord, length, crookedness, clockwiseness, count]...]
                >length - up to 49: how many adjacent edge pxs found
                >crookedness - if the next px is in a different relative place than the previous, example - if the previous px was above, and the next pixel is right, that's +1 to crookedness
                >clockwiseness - from the "text box" of the image if changes in dxdy seam to wrap around the text box in a clockwise way = 0, else 1
                >count - how many times dxdy changed the coords
        """
        if self.debugging: print("looking for edge")
        count = 0
        retList = []
        (_xHold, _yHold) = startCoord
        while True:
            (_x, _y) = self.keep_it_in_bounds(_xHold+dxdy[0], _yHold+dxdy[1], rightwardX=self.W, lowerY=self.H)
            if (_x, _y) != (_xHold+dxdy[0], _yHold+dxdy[1]):
                if self.debugging: print("at end of pic")
                break
            (_xHold, _yHold) = (_x, _y)
            retC = (_retX, _retY) = (_x, _y)
            if self.edges[_y][_x] > 0 and not (_x, _y) in matches:
                matches[(_x, _y)] = True
                crookedness = 0
                clockwiseness_err = 0
                nb_dxdy = (-1, 0)
                currentCoord = (_x, _y)
                for _len in range(50):
                    ret_dxdy = self.find_cw_neighbour(currentCoord, nb_dxdy, matches)
                    if ret_dxdy == False: #find_cw_neighbour returns False if it searches out of bounds. 
                        if self.debugging: print("breaking main for loop b/c no match")
                        break
                    if ret_dxdy != nb_dxdy: 
                        crookedness += 1
                        nb_dxdy = ret_dxdy
                    clockwiseness_err += self.get_clockwiseness_err((629, 35), currentCoord, nb_dxdy)
                    currentCoord = (currentCoord[0]+nb_dxdy[0], currentCoord[1]+nb_dxdy[1])
                    matches[currentCoord] = True
                    if currentCoord != self.keep_it_in_bounds(currentCoord[0], currentCoord[1]):
                        if self.debugging: print("edge of pic, breaking loop in main")
                        break
                ret = [retC, _len, crookedness, clockwiseness_err, count]
                if self.debugging: print(ret)
                retList.append(ret)
                if self.debugging: display(matches)
            count = count+1
        return retList

    def keep_it_in_bounds(self, _x, _y, leftwardX=0, upperY=0, rightwardX=1280, lowerY=720):
        _rx = _x
        _ry = _y
        _rx = 0 if _x < 0 else _rx
        _rx = rightwardX-1 if _x > rightwardX-1 else _rx
        _ry = 0 if _y < 0 else _ry
        _ry = lowerY-1 if _y > lowerY-1 else _ry
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
        """
        c = (neighbour_column, neighbour_row) = (centerCoord[0] + dxdy[0], centerCoord[1] + dxdy[1])
        last_dxdy = dxdy
        new_dxdy = dxdy
        foundAMatch = False
        for i in range(8):
            new_dxdy = self.get_next_ccw_coord(new_dxdy, 1)
            c = (neighbour_column, neighbour_row) = (centerCoord[0] + new_dxdy[0], centerCoord[1] + new_dxdy[1])
            if self.edges[neighbour_row][neighbour_column] > 0 and (not c in matches):
                last_dxdy = new_dxdy #just keep rewriting this val, the last ccw coord to match is the most cw coordinate
                foundAMatch = True
        if foundAMatch:
            return last_dxdy
        else: return False

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

    def display(self, _dict):
        edgeCpy = self.edges.copy()
        if self.debugging: print('displaying')
        for coord in _dict.keys():
            # if self.debugging: print(coord)
            cv2.rectangle(edgeCpy, coord, coord, 255, 10)
        cv2.imshow("edgeCpy", edgeCpy)
        if cv2.waitKey() & 0xFF == ord("q"):
            print("q detected")