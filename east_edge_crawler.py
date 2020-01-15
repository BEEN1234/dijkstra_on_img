from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
import sys
# load the input image and grab the image dimensions

def get_text_boxes(image):
    orig = image.copy()
    (H, W) = image.shape[:2]

    # """
    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (newW, newH) = (320, 320) # just needs to be a multiple of 32
    # (newW, newH) = (W/2, H/2)
    rW = W / float(newW)
    rH = H / float(newH)

    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]
    # """

    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]
    # load the pre-trained EAST text detector
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet("frozen_east_text_detection.pb")
    
    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
        (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()

    # show timing information on text prediction
    print("[INFO] text detection took {:.6f} seconds".format(end - start))

    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < 0.5:
                continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)
            
            # add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)
    newBoxes = []
    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # scale the bounding box coordinates based on the respective
        # ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        newBoxes.append((startX, startY, endX, endY))
        # draw the bounding box on the image
        # cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)
    
    # show the output image
    # cv2.imshow("Text Detection", orig)
    # cv2.waitKey(0)
    return newBoxes

imgDir = "targetMedia\\picOriginal1.png"
image = cv2.imread(imgDir)
boxes = get_text_boxes(image)
edges = cv2.Canny(image, 50, 100)
(H, W) = image.shape[:2]

"""
plan:
    1. iterate through text boxes and run "find_upper_edge"
        a) if you find an edge follow to the right for 50 px
        b) if you don't move 10 px right on text box and look again
    2. if you find one follow it
        - find slope
        if you lose it: follow slope 10px, if you loose it again search clockwise
    3. once you're at the starting point a match has been found. paint a mask
#"""

topEdgeMatch = 50 #search 50px to the right to decide if it's the top edge of a graphic, how about 50 | int(1.5 * height)
followTragectory = 10 #once an edge is found if you lose it try following the current slow for 10 px, if you lose it again search clockwise
    #todo - graphics may not always have edges curl clockwise - fix it so it can look any direction, but for now just search 90deg clockward
noMatchMoveRight = 10

def edge_crawler(edges, x, y):
    """
    inputs:
        edges - cv2.Canny() - it's a matrix of 0's and 255's of where edges exist
        x, y - the point that i believe the outer edge lives on
    outputs: v1 -> just coordinates for the graphic
    
    steps:
        1. follow the line and find slope
        2. follow by followTragectory if you lose it
        3. if you lose it and tried following look in a 90 deg clockward arc

    #"""
    leftX = W #rewrite with lower X values
    upperY = y #since the outer algo finds the top edge
    rightX = 0 #rewrite with every value higher
    lowerY = 0

    currentXOffset = 0
    currentYOffset = 0
    #starts out going right, so rise of zero, run of 1 = slope0
    rise = 0
    run = 1
    rightward = True #direction of movement, for any +/- slope which way are you moving along the line
    downward = False #slope would be infinite so use this instead
    upward = False

    path = [] #[(startingX, startingY, endingX, endingY)] - connect all these lines to find the graphic

    completed = False

    def search_for_line():
        #search
        

    while not completed:
        # rise/run = slope you want both rise and run, but you could pic any value for either, so always run by lowest value that get's whole number coordinates? so i guess keep rise and run as actual numbers that i discover.
        currentXOffset = currentXOffset + run
        currentYOffset = currentYOffset + rise
        _x = x + currentXOffset
        _y = y + currentYOffset
        if edges[_y][_x] == 0:
            print("edge lost at %d, %d" %(_x, _y))
            #edge lost - continue in same direction but look in a 5px swath
                #in search we'll check if the trajectory has changed. 
            #currently let's just keep looking in the same direction but wider - add on the non-zero value of run | rise and look up and down too
            searchX = currentXOffset
            searchY = currentYOffset
            searchVertical = False
            searchHorizontal = False
            swathRadius = 2
            newMatch = False
            while not newMatch:
                if run > 0:
                    searchX = searchX + run
                    searchHorizontal = True
                if rise > 0:
                    searchY = searchY + rise
                    searchVertical = True
                # for each extra val of the above:
                if searchHorizontal:
                    for expandSearch in range(swathRadius)
                        if edges[searchY+expandSearch][searchX] > 0:
                            print("edge found down")
                            #follow the same direction to see if it just jogged a bit
                            # if not then try perpindicular. 
                        if edges[searchY-expandSearch][searchX] > 0:
                            print("edge found up")
                            #follow the same direction to see if it just jogged a bit
                if searchVertical:
                    for expandSearch in range(swathRadius)
                        if edges[searchY][searchX+expandSearch] > 0:
                            print("edge found right")
                        if edges[searchY][searchX+expandSearch] > 0:
                            print("edge found left")
            break
        showme = edges.copy()
        y2 = _y + 50
        cv2.rectangle(showme, (x, y), (_x, y2), 255, 5)
        cv2.imshow("showme", showme)
        if cv2.waitKey() & 0xFF == ord("q"):
            print("q detected, kill app")
            sys.exit()

def follow_the_line():


#1
for (sx, sy, ex, ey) in boxes:
    movedUp = 0
    edgeFound = False
    while (sy - movedUp > 0):
        #if edge is found, then follow right
        currentRow = sy - movedUp
        if currentRow < 0:
            print("out of bounds w of ", currentRow) # out of bounds with a negative y val
            break
        if edges[currentRow][sx] > 0:
            #follow right for "topEdgeMatch" distance to prove a match
            movedRight = 0
            #1a - run the while loop and if movedRight gets to topEdgeMatch value, then i'm confident this is an outer bound, follow it
            while(movedRight < topEdgeMatch):
                currentColumn = sx + movedRight
                if edges[currentRow][currentColumn] == 0 or currentColumn > W:
                    #1b - break this loop and continue looking up
                    break
                movedRight = movedRight + 1
            if movedRight >= topEdgeMatch:
                #a match is found, follow it
                print("matching top edge at %d, %d" %(currentColumn, currentRow))
                edge_crawler(edges, currentColumn, currentRow)
                break
        movedUp = movedUp + 1