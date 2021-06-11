import re
import numpy as np
import cv2
from copy import deepcopy
from PIL import Image
import pytesseract as tess
import sys
import imutils
from imutils.video import VideoStream
from imutils.video import FPS
import time
from sen_mail import sndMail

with open ("blacklist.csv") as f:
    content=f.readlines()
content = [x.strip() for x in content]
print(content)
print(type(content))

img1=""

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,50)
fontScale              = 1
fontColor              = (255,255,255)
redFontColor         = (0,0,255)
lineType               = 2

def preprocess(img):
    imgBlurred = cv2.GaussianBlur(img, (5,5), 0)
    gray = cv2.cvtColor(imgBlurred, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray,cv2.CV_8U,1,0,ksize=3)
    ret2,threshold_img = cv2.threshold(sobelx,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return threshold_img

def cleanPlate(plate):
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if contours:
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        max_cnt = contours[max_index]
        max_cntArea = areas[max_index]
        x,y,w,h = cv2.boundingRect(max_cnt)
        img1=plate

        if not ratioCheck(max_cntArea,w,h):
            return plate,None

        cleaned_final = thresh[y:y+h, x:x+w]
        return img1,[x,y,w,h]

    else:
        return plate,None


def extract_contours(threshold_img):
    element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
    morph_img_threshold = threshold_img.copy()
    cv2.morphologyEx(src=threshold_img, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)

    contours, hierarchy= cv2.findContours(morph_img_threshold,mode=cv2.RETR_EXTERNAL,method=cv2.CHAIN_APPROX_SIMPLE)
    return contours


def ratioCheck(area, width, height):
    ratio = float(width) / float(height)
    if ratio < 1:
        ratio = 1 / ratio

    aspect = 4.7272
    min = 10*aspect*10
    max = 125*aspect*125  # maximum area

    rmin = 3
    rmax = 6
    if (area < min or area > max) or (ratio < rmin or ratio > rmax):
                return False
    return True

def isMaxWhite(plate):
    avg = np.mean(plate)
    if(avg>=95):
        return True
    else:
        return False

def validateRotationAndRatio(rect):
    (x, y), (width, height), rect_angle = rect

    if(width>height):
        angle = -rect_angle
    else:
        angle = 90 + rect_angle

    if angle>15:
        return False

    if height == 0 or width == 0:
        return False

    area = height*width
    if not ratioCheck(area,width,height):
        return False
    else:
        return True



def cleanAndRead(img,contours):
    global last_no
    for i,cnt in enumerate(contours):
        min_rect = cv2.minAreaRect(cnt)

        if validateRotationAndRatio(min_rect):

            x,y,w,h = cv2.boundingRect(cnt)
            plate_img = img[y:y+h,x:x+w]

            if(isMaxWhite(plate_img)):
                               
                clean_plate, rect = cleanPlate(plate_img)

                if rect:
                    x1,y1,w1,h1 = rect
                    x,y,w,h = x+x1,y+y1,w1,h1
                    plate_im = Image.fromarray(clean_plate)
                    plate_img = img[y:y+h,x:x+w]
                    cv2.imwrite("abc.jpg",plate_img)
                    climg = cv2.imread("abc.jpg")
                    clean_plate = cv2.resize(climg, None, fx=3.5, fy=3.5, interpolation=cv2.INTER_CUBIC)
                    config = ('--tessdata-dir "." -l eng --oem 1 --psm 3')
                    text = tess.image_to_string(Image.open('abc.jpg'),config=config)
                    regex = re.compile('[^a-zA-Z0-9]')
                    text = regex.sub('', text)
                    #print(text)
                    if(len(text)==10):
                        if(text not in content):
                            print(text)
                            print("Black")
                            cv2.imwrite("abc1.jpg",frame)
                            cv2.putText(img,text,(x,(y-10)),font,fontScale,redFontColor,lineType)
                            img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
                            if(last_no!=text):
                                last_no=text
                                sndMail(text)
                        else:
                            cv2.putText(img,text,(x,(y-10)),font,fontScale,fontColor,lineType)
                            img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    
    return img




if __name__ == '__main__':
        vs = VideoStream(src=0).start()
        time.sleep(2.0)
        fps = FPS().start()
        last_no=""

        while True:
                frame = vs.read()
                frame = imutils.resize(frame, width=500)
                threshold_img = preprocess(frame)
                contours= extract_contours(threshold_img)
                img = cleanAndRead(frame,contours)
                cv2.imshow("Frame", img)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                        break


