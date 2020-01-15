import cv2
debugging = True


pic = cv2.imread("targetMedia\\picOriginal1.png")

#canny is an edge finding algorithm, the result is 2D matrix of 0's and 255's
edges = cv2.Canny(pic, 90, 100)
x_start = 629 #check to see if x_start and y_start are the current values when crawling - if they are then you can 
y_start = 20
(H, W) = pic.shape[:2]
matches_dict = {} #{(x, y): True, (otherX, otherY): True}

def litmus_test(argX, argY, argdX, argdY, distanceForMatch=50, pxsPerError=10):
    # look for 50 w/ only 1 error every 10
    """
    inputs: 
        argx, y are coordinates where an edge was found
        argdx, dy are where to look in adjacent blocks
            dx - 1 means right, -1 means left
            dy - 1 means down, -1 means up
    outputs: boolean
    #"""
    matches = 0
    errors = 0
    onEdge = True
    _x = argX
    _y = argY
    while onEdge:
        edCpy = edges.copy()
        cv2.rectangle(edCpy, (_x, _y), (_x, _y), 255, 5)
        cv2.imshow("edCpy", edCpy)
        if cv2.waitKey() & 0xFF == ord("q"):
            print("q detected")
        _x = _x + argdX
        _y = _y + argdY
        px = edges[_y][_x]
        if px > 0:
            matches_dict[(_x, _y)]:True
            matches = matches + 1
            continue
        else:
            #move the coordinates back to the last match
            _x = _x - argdX
            _y = _y - argdY
            nbs = check_neighbours(_x, _y, matches_dict)
            if len(nbs) == 0 or len(nbs) > 0:
                print("end of the line")
                print("matches: %d" %matches)
                if(matches>distanceForMatch): return True
                onEdge = False
                break
            else:
                (xM, yM) = nbs[0]
                argdX = xM - _x
                argdY = yM - _y
                _x = xM
                _y = yM
                errors = errors + 1


            """
            plan:
            _x = _x - argdX
            _y = _y - argdY
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    neighbour_row = centerY + dy 
                    neighbour_column = centerX + dx
                    npx = edges[neighbour_row][neighbour_column]
                    #if it's an edge, and not already a match
                    c = (neighbour_column, neighbour_row)
                    #if it's an edge, and not already discovered
                    # print(matches_dict) #{629, 5} only 1 point.
                    if npx > 0 and (dx != 0 and dy != 0) and (dx != argdX*-1 and dy != argdY*-1):
                        matchedCoordinates.append(c)
            #"""
    

            
                
                

def check_neighbours(centerX, centerY, matches): # delme
    if debugging:
        print('checking neighbours at the following pos: ')
    """
    input: a dictionary of matches so that pxs found can be "looked up" and added to the dictionary AND returned to the caller
    outputs: 
        -matches - a list of "[(X, Y)]" and it updates dictionary of matches
    #"""
    if debugging:
        print(centerX)
        print(centerY)
    px = edges[centerY][centerX]
    matchedCoordinates = [] # [(x, y)] - used by follow_edge to start explore_multiples if len > 1
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            neighbour_row = centerY + dy
            neighbour_column = centerX + dx
            npx = edges[neighbour_row][neighbour_column]
            #if it's an edge, and not already a match
            c = (neighbour_column, neighbour_row)
            #if it's an edge, and not already discovered
            # print(matches_dict) #{629, 5} only 1 point.
            if npx > 0 and not str(c) in matches:
                matchedCoordinates.append(c)
    return matchedCoordinates


#go up, left, right and down and explore both directions
#go up 
matched = False
xUpwards = x_start
yUpwards = y_start
count = 0
while not matched:
    count = count + 1
    yUpwards = yUpwards - 1
    if(yUpwards < 0): 
        print("out of loop 3:40pm by reaching top of pic")
        break
    px = edges[yUpwards][xUpwards]
    if px > 0:
        print("an edge found at %d, %d"%(xUpwards, yUpwards))
        litmus_test(xUpwards, yUpwards, 1, 0)
print(count)
cv2.rectangle(edges, (x_start, y_start), (x_start, y_start), 255, 4)
cv2.imshow("edges", edges)
if cv2.waitKey() & 0xFF == ord("q"):
    print("q detected")
