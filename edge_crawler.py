import cv2
debugging = True


pic = cv2.imread("targetMedia\\picOriginal1.png")

#canny is an edge finding algorithm, the result is 2D matrix of 0's and 255's
edges = cv2.Canny(pic, 90, 100)
x_start = 629 #check to see if x_start and y_start are the current values when crawling - if they are then you can 
y_start = 5
(H, W) = pic.shape[:2]
matches_dict = {}

"""
if debugging:
    print(H) #720
    print(W) #1280
cv2.imshow("edges", edges)
if cv2.waitKey() & 0xFF == ord("q"):
    print("q detected")
cv2.rectangle(edges, (444, 20), (563, 6), 255, 5)
cv2.imshow("edges", edges)
if cv2.waitKey() & 0xFF == ord("q"):
    print("q detected")
#"""

def main(x, y):
    if debugging:
        print("in main")
    #going to be the whole function, calling follow_edge, then checking if it's done, and calling search or follow the edge appropriately. 
    #the weird thing is "search" is always going to just get the best edge anyways. so it'll just be follow the edge, then search until a match is found. 
    firstCoordinate = (x, y)
    firstCoordinate = str(firstCoordinate)
    matches_dict[firstCoordinate] = True
    # print(firstCoordinate)
    (x1, y1, x2, y2, straightness, matches) = follow_edge(x, y, 0, 0, matches_dict)
    # endpoints = search(x2, y2)
    # explore_multiples(endpoints, )doesn't work like this


def search(x, y):
    if debugging:
        print("in search")
    """
    inputs - edges matrix, coordinates to center the 40 by 40 search field around
    outputs - a list of endpoints for explore multiples
    """
    #work your way around the lost point until an edge is found... let's just try looking 40 by 40 - easy - could definitely improve algo for search space
    # variables:
    searchOut = 20
    upperY = y - searchOut
    lowerY = y + searchOut
    leftwardX = x - searchOut
    rightwardX = x + searchOut
    upperY = 0 if upperY < 0 else upperY
    lowerY = H if lowerY > H else lowerY
    leftwardX = 0 if leftwardX < 0 else leftwardX
    rightwardX = W if rightwardX > W else rightwardX

    """
    cv2.rectangle(edges, (leftwardX, upperY), (rightwardX, lowerY), 255, 4)
    cv2.imshow("edges", edges)
    if cv2.waitKey() & 0xFF == ord("q"):
        print("q detected")
    #"""
    potentialEdgeEndpoints = [] #: (x, y)
    _matches_dict = {}
    
    #find potential edges - greedy algorithm. go through each row and find an edge, then look at immediate neighbours and continue searching that line
    #redo every single edge as many times as it must be done, and then filter out duplicates in the end. 
    for row in range(upperY, lowerY+1):
        for column in range(leftwardX, rightwardX+1):
            px = edges[row][column]
            pxCoord = (column, row)
            pxCoord = str(pxCoord)
            if px > 0 and not pxCoord in _matches_dict:
                res_list = check_neighbours_recursively(column, row, _matches_dict, leftwardX, upperY, rightwardX, lowerY)
                if debugging:
                    print("done recursive search: ")
                    print(res_list)
            # then run chase_the_edge() i guess precedence goes to longer and straighter

def check_neighbours_recursively(centerX, centerY, matches, leftwardX, upperY, rightwardX, lowerY):
    if debugging:
        print('chekcing neighbours recursively')
    """
    input: 
        x, y - a search point
        matches - a dict of {"(x, y)":True ...}
    outputs: results - a list of "[(X, Y)]" that are "endpoints"
    #"""
    px = edges[centerX][centerY]
    lastX = 0
    lastY = 0
    noMatches = True
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            neighbour_row = centerY + dy
            neighbour_column = centerX + dx
            #skip this run if it's out of bounds
            if neighbour_row > lowerY or neighbour_row < upperY or neighbour_column > rightwardX or neighbour_column < leftwardX:
                continue
            results = check_neighbours_recursively(neighbour_column, neighbour_row, matches) #eventually this will not match and we can collapse the stack
            npx = edges[neighbour_row][neighbour_column]
            #if it's an edge, and not already a match
            c = (neighbour_column, neighbour_row)
            #if it's an edge, and not already discovered
            if npx > 0 and not str(c) in matches:
                noMatches = False
                lastX = neighbour_column
                lastY = neighbour_row
                coord = (neighbour_column, neighbour_row)
                coord = str(coord)
                matches[coord] = True
    if noMatches:
        return results + (lastX, lastY) #ideally a list of endpoints in recursive searches. 

def follow_edge(x, y, rise, run, matches, already_explored_dict=matches_dict):
    """
    this function handles branches
    inputs - 
        x, y which are cv2 cooridinates, y increases downward and x rightward
        rise => postive one means looking upward, negative one downward
        run => postive one means rightward, negative one means leftward
        mathces => the dictionary of matches, if called from explore-multiples it needs to be a newly created dictionary that this will update, if called in the case we know it's for real it needs global matches to update.
    outputs - 
        [x1, y1, x2, y2, straightness, matches]
            x1y1 - starting
            x2y2 - ending
            straightness - number of times rise, run didn't predict the pixel
            matches - just used by explore_multiples() to update hte main dict with
    #"""
    if debugging:
        print("in follow the edge")
    # return values
    x1 = x 
    y1 = y 
    x2 = 0
    y2 = 0
    straightness = 0

    while True:
        neighbours = check_neighbours(x, y, matches)
        n_neighbours = len(neighbours)
        if n_neighbours > 1:
            if debugging:
                print("running multiples")
            matchCpy = matches.copy()
            edge_coordinates = explore_multiples(neighbours, (x, y), matchCpy) #does edge this algorithm again, but on multiple possible edges, 
            if(len(edge_coordinates) > 0):
                [_x1, _y1, _x2, _y2, _straightness, _matched_dict] = edge_coordinates
            else:
                print("not enough args, breaking the loop because follow_edge returned nothing")
                break
            x = _x2
            y = _y2
            keys = _matched_dict.keys()
            for key in keys:
                matches[key] = True
                """
                shme = edges.copy()
                cv2.rectangle(shme, (x, y), (x, y), 255, 5) #why isn't this printing at my first fork.
                cv2.imshow("shme", shme)
                if cv2.waitKey() & 0xFF == ord("q"):
                    print("q from key write")
                    print(key)
                    print("x, y")
                    print(x, y)
                #returning the best match in the same format as this fn, and an additional param - dict of that edges matches to update global matches_dict with
                # """
        elif n_neighbours == 1:
            (_x, _y) = neighbours[0] #only 1 (x,y) pair is returned so we can just pull it
            x = _x
            y = _y
            if debugging: 
                print("1 match --> X, Y = %d, %d" %(x, y))
            matchedCoordinates = (x, y)
            matchedCoordinates = str(matchedCoordinates)
            matches[matchedCoordinates] = True
            #delme
            """
            shme = edges.copy()
            cv2.rectangle(shme, (x, y), (x, y), 255, 5)
            cv2.imshow("shme", shme)
            if cv2.waitKey() & 0xFF == ord("q"):
                print("1 match at %d, %d" %(x, y))
            # """
        elif n_neighbours == 0:
            x2 = x
            y2 = y
            break

    return (x1, y1, x2, y2, 0, matches) #TODO straightness... how to find that w/ this algo?

def check_neighbours(centerX, centerY, matches):
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
            if npx > 0 and not str(c) in matches and not str(c) in matches_dict:
                matchedCoordinates.append(c)
    return matchedCoordinates

def explore_multiples(coordinates_to_explore, root_coordinates, matches, return_all = False):
    if debugging:
        print("exploring_multiples")
    for args in coordinates_to_explore:
        matches[args] = True
    results = []
    most_matched = [] #args for addition to the main matches_dict
    most_matched_distance = 0
    for args in coordinates_to_explore:
        if debugging:
            print("bout to 'nit follow_edge")
        #args - edges, x, y, matches, rise, run
        #x, y are given, rise = 0, run = 0, matches = {str(root_coordinates):True}
        #TODO resumeHere: need to make arguments for follow_edge = x, y, rise, run, matches :: ...coordtoexplore, 0, 0, newlycreatedmatches(coordToExplore, and xy)
        _matches_dict = {}
        res = follow_edge(args[0], args[1], 0, 0, _matches_dict, matchesCpy) #thinking - will update matches_dict as it goes. also returns it's dict.
        if debugging: 
            print("1 possible res from explore multiples: ")
            print(res)
        results.append(res)
    if return_all:
        return results
    #TODO here is a good place to produce the best algo
    for res in results:
        #res = [x1, y1, x2, y2, straightness]
        """
        plan:
            -the most matched will be for now length - between x1, y1, x2, y2, TODO in the future give weighted values to:
                -length, straightness, distance from the center of the text box. 
        #"""
        distance = abs(res[0] - res[2]) + abs(res[1] - res[3])
        if distance > most_matched_distance:
            most_matched_distance = distance
            most_matched = res
    return most_matched #single most matched follow_edges() return => (x1, y1, x2, y2, straightness=0, matches)
        # why is this 0... it's causing an error. if all the things were already discovered

def parse_coord_tuple(tupStr):
    li = tupStr.split(",")
    x = int(li[0][1:])
    y = int(li[1][1:-1])
    tup = (x, y)
    print(tup)
    return tup

main(x_start, y_start)

"""
plan:
keys = matches_dict.keys()
for key in keys:
    tup = parse_coord_tuple(key)
    edCpy = edges.copy()
    cv2.rectangle(edCpy, tup, tup, 255, 4)
    cv2.imshow("edCpy", edCpy)
    if cv2.waitKey() & 0xFF == ord("q"):
        print("q detected")
#"""

"""
problemArea = (563, 6) # 445, 20 > 444, 20
edges[6][563] = 100
newImg = edges[0:12, 560:566]
newImg = cv2.resize(newImg, (500, 500))
cv2.imshow("newImg", newImg)
if cv2.waitKey() & 0xFF == ord("q"):
    print("q detected")
print(check_neighbours(problemArea[0], problemArea[1], matches_dict))
#"""