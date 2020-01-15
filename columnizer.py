import cv2
"""
todo
    - the best test of it being an edge, is the movement mostly wrapping around our first pos. 
    - done in ../graphic_columnizer/graphic_columnizer.py - as a general rule i think at every branch let's just go clockwise and not recurse - todo, i'm just going to bodge it for now
"""

pic = cv2.imread("targetMedia\\picOriginal1.png")
edges = cv2.Canny(pic, 90, 100, L2gradient=True)
x_start = 629 #check to see if x_start and y_start are the current values when crawling - if they are then you can 
y_start = 5 + 30
(H, W) = pic.shape[:2]
glbl_matches_dict = {(x_start, y_start): True, (x_start+10, y_start+10): True}
debugging = True
if True:
# if debugging:
    print(H, W)
    import pdb

def main():
    atLeftBound = False
    # atRightBound = False
    count = 0
    _x = x_start
    _y = y_start
    while not atLeftBound:
        # if debugging: print('checking for edge')
        (_xL, _yL) = keep_it_in_bounds(_x-count, _y)
        if (_xL, _yL) != (_x-count, _y):
            print("at end of pic")
            break
        if edges[_yL][_xL] > 0:
            glbl_matches_dict[(_xL, _yL)] = True
            """ delme
            _ytemp = _yL - 1
            for _dx in range(-1, 2):
                if edges[_ytemp][_xL + _dx] > 0:
                    glbl_matches_dict[(_xL + _dx, _ytemp)] = True
                    #follow it
            # """ #deindent the stuff below to here if i uncomment the matching quotes
            matches = {}
            res = check_neighbours_recursively(_xL, _yL, matches=matches)
            length = len(matches.keys())
            if length > 40:
                print("===================================================")
                print(length)
                print(res)

            if debugging: display()

        count = count + 1
        if count == 800:
            #fix this mechanic- meant to find an edge, follow it and determine if it's straightish - and edge like. 
            atLeftBound = True
            break

def look_for_an_edge(startCoord, dx, dy):
    if debugging: print("looking for edge")

def keep_it_in_bounds(_x, _y, leftwardX=0, upperY=0, rightwardX=W, lowerY=H):
    _rx = _x
    _ry = _y
    _rx = 0 if _x < 0 else _rx
    _rx = W-1 if _x > W-1 else _rx
    _ry = 0 if _y < 0 else _ry
    _ry = H-1 if _y > H-1 else _ry
    # if debugging and (_rx != _x or _ry != _y):
    #     inp = (_x, _y)
    #     ret = (_rx, _ry)
    #     print("rewriting coords w/ input of (%d,%d) and return of (%d,%d)" % (inp[0], inp[1], ret[0], ret[1]))
    return (_rx, _ry)

def get_next_ccw_coord(dxdy, radius):
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
    

def check_neighbours_recursively(centerX, centerY, prev_dx=0, prev_dy=0, limit=50, n_matched=0, matches=glbl_matches_dict):
    centerX, centerY = keep_it_in_bounds(centerX, centerY)
    # if debugging:
    #     if not len(matches.keys())%20:
    #         edgeCpy = edges.copy()
    #         cv2.rectangle(edgeCpy, (centerX, centerY), (centerX, centerY), 200, 10)
    #         cv2.imshow("edgeCpy", edgeCpy)
    #         if cv2.waitKey() & 0xFF == ord("d"):
    #             print("displaying dict")
    #             display()
    #     print('checking neighbours recursively')
    """
    input: 
        centerX, centerY - a search point
        prev_dx, prev_dy - the previous stack frames dx, dy
        limit - how many matches to find
        n_matched - how many matches we've found
        matches - a dict of {(x, y):True ...}
    outputs: list : [crookedness, (x1,y1), (x2,y2)...]
    #"""
    crookedness_errs = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] # since this is recursive we need every possible match to be saved and then sum them all up to return it.
    clockwiseness_errs = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] # since this is recursive we need every possible match to be saved and then sum them all up to return it.
    foundNbr = False
    results = [0, 0]
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            c = (neighbour_column, neighbour_row) = (centerX + dx, centerY + dy)
            #skip this run if it's out of bounds
            if (neighbour_column, neighbour_row) != keep_it_in_bounds(neighbour_column, neighbour_row):
                continue
            #if it's an edge, and not already discovered
            if edges[neighbour_row][neighbour_column] > 0 and (not c in matches or not c in glbl_matches_dict):
                n_matched = n_matched + 1
                matches[c] = True
                glbl_matches_dict[c] = True
                # if debugging: print('coord found, should be in dict: %d, %d' % (c[0], c[1]))
                #if we're at the limit then pop down the stack
                if n_matched > limit-1: #wait... what if both branches hit this block. then the first to run finishes, pops down the stack we get results and ... this is going to reset crookedness each time...
                    return [0, 0, (centerX, centerY)]
                results = check_neighbours_recursively(neighbour_column, neighbour_row, dx, dy, limit, n_matched, matches=matches) #eventually this will not match and we can collapse the stack
                #get crookedness = everytime a match isn't in the same relative place as the last match, then add 1
                # pdb.set_trace()
                crookedness_errs[dy + 1][dx + 1] = results[0] + 1 if (dx, dy) != (prev_dx, prev_dy) else results[0] #[dx + 1] b/c -1 to 1, so get it back to zero indexing.
                clockwiseness_errs[dy + 1][dx + 1] = results[1] + get_clockwiseness_err((x_start, y_start), (centerX, centerY), (dx, dy))
                foundNbr = True
    crookednessTot = sum([sum(row) for row in crookedness_errs])
    clockwisenessTot = sum([sum(row) for row in clockwiseness_errs])
    results[0] = crookednessTot
    results[1] = clockwisenessTot
    if not foundNbr:
        results.append((centerX, centerY))
    return results

def get_clockwiseness_err(centerCoord, currentCoord, dxdy):
    # if debugging: print("getting clockwiseness")
    """
    plan - basically treat the top left corner of the east text bbox like the center of a circle, and if the trajectory of the line we follow opposes that, then add 1. 
        so some basics 
            - clockwise lines will always be perpendicular to the slope of hte line from centerCoord to currentCoord
            - y = mx + b. the slope of perpendicular line is -1/m. 
                > -1/rise/run = rise/run
                > if we treat centerCoord as origin -1/(centery-0)/(centerx-0) is easy to simpify.
                > (-1)*(centerx/centery) = (dy/dx)
            - in reality the line will almost always have some vertical and some horizontal component(except for 4 times), 
                so just round each dx dy to +-1, 
                then take the negative and make sure slope[0], slope[1] isn't == to neg(dx), neg(dy)
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

    #-1/m, first make run negative, then swap rise and run to get 1/m
    run = -run
    hold = run
    run = rise
    rise = hold

    #then for logic we don't want dx or dy to equal not_run or not_rise respectively
    not_run = -run
    not_rise = -rise
    #if either dx or dy is a value it shouldn't be
    if dxdy[0] == not_run or dxdy[1] == not_rise:
        return 1
    else: 
        return 0

def display(_dict=glbl_matches_dict):
    edgeCpy = edges.copy()
    if debugging: print('displaying')
    for coord in _dict.keys():
        # if debugging: print(coord)
        cv2.rectangle(edgeCpy, coord, coord, 255, 10)
    cv2.imshow("edgeCpy", edgeCpy)
    if cv2.waitKey() & 0xFF == ord("q"):
        print("q detected")

main()