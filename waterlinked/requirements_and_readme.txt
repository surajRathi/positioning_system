#pip install -r requirements.txt
#run the file externaldepth.py - if you need to use only the waterlinked (C) interface
#run the file SaudiTank.py - if you need to use Planys GUI with image overlayed

#Make changes in config.json (opened in notepad) as required
#line 8: Total (add absolute of x and y coordinates of waterlinked search area rectangle, (xa,ya) and (xb,yb)
#line 10: x = xa, y = ya
# r1_x indicates x coordinate of receiver 1
#direction:
#forword=positive
#backword=negative
#right=positive
#left=negative
#line 11: x1 = r1_x+xa, y1 = r1_y+ya
#line 12: x2 = r2_x+xa, y2 = r2_y+ya
#line 13: x3 = r3_x+xa, y3 = r3_y+ya
#line 14: x4 = r4_x+xa, y4 = r4_y+ya

numpy
pandas
pillow
imutils
opencv-python
matplotlib
websockets
requests
