import numpy as np
import cv2
import pytesseract as pyT
from pytesseract import Output
pyT.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
photos = ["picOriginal1.png","picOriginal2.png","picOriginal3.png","picOriginal4.png","picOriginal5.png","picOriginal6.png","picOriginal7.png","picOriginal8.png","picOriginal9.png","picOriginal10.png","picOriginal11.png","picOriginal12.png","picOriginal13.png","picOriginal14.png","picOriginal15.png","picOriginal16.png","picOriginal17.png","picOriginal18.png","picOriginal19.png","picOriginal20.png","picOriginal21.png","picOriginal22.png","picOriginal23.png","picOriginal24.png","picOriginal25.png","picOriginal26.png","picOriginal27.png","picOriginal28.png","picOriginal29.png","picOriginal30.png","picOriginal31.png","picOriginal32.png","picOriginal33.png","picOriginal34.png","picOriginal35.png","picOriginal36.png","picOriginal37.png","picOriginal38.png","picOriginal39.png","picOriginal40.png","picOriginal41.png","picOriginal42.png","picOriginal43.png","picOriginal44.png","picOriginal45.png","picOriginal46.png","picOriginal47.png","picOriginal48.png","picOriginal49.png","picOriginal50.png","picOriginal51.png","picOriginal52.png","picOriginal53.png","picOriginal54.png","picOriginal55.png","picOriginal56.png","picOriginal57.png","picOriginal58.png","picOriginal59.png","picOriginal60.png","picOriginal61.png","picOriginal62.png","picOriginal63.png","picOriginal64.png","picOriginal65.png","picOriginal66.png","picOriginal67.png","picOriginal68.png","picOriginal69.png","picOriginal70.png","picOriginal71.png","picOriginal72.png"]

def parseTesseractBoundingBoxes(boxes):
    """"
    takes string of boxes
    returns a list of lists [x1, y1, x2, y2]

    plan - 
        split on newline
        split again on whitespace and talke last 4, then parse int. 
    
    """
    chars = boxes.split("\n")
    for i, char in enumerate(chars):
        chars[i] = char.split()[-5:-1]
        for i2, coordinate in enumerate(chars[i]):
            chars[i][i2] = int(coordinate)
    return chars

def findMyContainer(charbox, edges):
    """
    not finished

    takes 
        a list of 4 numbers - x1, y1, x2, y2 that tell where a character is
        the [[]] of edges
    returns xy coordinates and a map of what to keep... nasty. 

    thought notes
    1. move up the pic until "an" edge is found
    2. look right and follow, it until it ends - if it's shorter than 50 px's break fn and continue up
    3. nothing :: at top of photo? move within width by 10 pxs and try again,

    4. if a match is found the loop will be broken and move to the "follow boundary protocol"
    5. it will just follow the line, and search if it loses - i'm going to assume they're typically straight. but for now let's just go with it
    basic structure
    for every 10 pxs of width:
        look up and find edge - follow right if ends in < 50px return, else follow edge
    """
    #1. start at the location specified and move up until you find an edge. 
    x1 = charbox[0]
    y1 = charbox[1]
    noEdge = True
    count = 0
    for width_index in range(charbox[2]//10):
        x1_offset = width_index * 10
        print(x1_offset)

    while noEdge:
        # I think up is actually minus 1
        px = edges[y1-count][x1]
        count+=1
        if px > 0:
            print("found edge at %d, and %d" %(x1, y1-count))

            noEdge = False

mediaDir = "targetMedia\\"

for i, img in enumerate(photos):
    # photos[i] = mediaDir + img
    picLocation = mediaDir + img
    # getting info from pic => https://stackoverflow.com/questions/20831612/getting-the-bounding-box-of-the-recognized-words-using-python-tesseract
    img = cv2.imread(picLocation)
    d = pyT.image_to_data(img, output_type=Output.DICT)
    dataString = pyT.image_to_string(img)
    print(dataString)
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 2)
        # findMyContainer((x, y, w, h), edges)
    cv2.rectangle(img, (50, 50), (250, 650), (0, 255, 0), 5)
    cv2.imshow('img', img)
    cv2.waitKey(0)
    if n_boxes > 0:
        pic = cv2.imread(picLocation)
        edges = cv2.Canny(pic, 2, 4)
        cv2.imshow("edges", edges)
        cv2.waitKey() #needed for showing imgs
        for i in range(n_boxes):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            findMyContainer((x, y, w, h), edges)
        """
        pic is 1280 by 720
        """

        # """
    input("=======================press key to see next=================================")


#so the plan... 
"""
    1. get images
    2. tesseract get boxes
    3. if text then do edge detection
    4. on edge search for a line that binds the text - get a rectangle and ensure text is within that box
    5. rinse repeat
"""