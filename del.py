import numpy as np
import cv2

frame = np.zeros((500, 500), dtype=np.uint8)

picDir = "targetMedia\\picOriginal1.png"

pic = cv2.imread(picDir)
print(pic.shape)
# print(pic.shape) #w, h, channels


# slicing to see how it works
"""
# lesson - 
    #apparently pic[y:y+h, x:x+w]
crp = pic[50:500, 50:900] 
cv2.imshow("pic", pic)
cv2.imshow("crp", crp)
if cv2.waitKey() & 0xFF == ord("q"):
    print("used q")
print("out of check")
# """
# drawing a rectangle to see how coordinates work: i,j is top left
"""
cv2.rectangle(frame, (50, 50), (100, 500), (255, 255, 255), 5)
    #reason for this - increasing a y val is down. 0,0 is top left. and everything in the pic is positive. we're in quadrant 3 with absolute vals

cv2.imshow("frame", frame)
cv2.waitKey()
# """