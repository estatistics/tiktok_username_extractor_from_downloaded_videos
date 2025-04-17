# step 0 
# you need the training dataset 'frozen_east_text_detection.pb'

# step 1 extract last frame
# warn: if audio is shorter/bigger than video then incorrect frame may produced
# for vids in *.mp4; do ffmpeg -sseof -1 -i "$vids" -vsync 0 -q:v 1 -update true "$vids".jpg; done

# step 2 manipulate extracted frame
# you cant merge these two commands. 
# crop frame / resize / sharpen for better results
# for file in *.jpg; do convert "$file" -crop 100%x15%+0+500  -quality 100  "/mnt/ssd1/tiktok_vids/""$(basename "$file")" ; done;
# for file in *.jpg; do convert "$file" -resize 200% -sharpen 0x10 -quality 100  "/mnt/ssd1/tiktok_vids/""$(basename "$file")" ; done;

# step 3, try the following code to a sample of images in a sample dir, 
# to check if works properly

# All print commands exists for debbuging

import os
import cv2
import re
import pytesseract
import colorsys
import numpy as np
from PIL import Image
from matplotlib.image import imread
# from imutils.object_detection import non_max_suppression

# tesseract config / whitelisting the allowed characters in tiktok username
cfg = '--psm 6 --oem 1  -c load_system_dawg=false -c load_freq_dawg=false -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ_.'

# PLEASE set the path that your tiktok videos are placed
pth0 = '/mnt/ssd1/tiktok_vids/'
pth_for_frozen_east_text_detection = '/mnt/ssd1/tiktok_vids/frozen_east_text_detection.pb'
pth_detector = pth_for_frozen_east_text_detection

matches=[]
# print(len(matches))
for root, dirnames, filenames in os.walk(pth0):
        for filename in filenames:
            if filename.endswith(".jpg"):
                matches.append(os.path.join(root, filename))
                #print(filename)


for match in matches:
    #print(match)
    img_ok = cv2.imread(match)
    
    # Reading the image for manipulation
    image = cv2.imread(match)

    eighth = image.size // 8
    orig = image.copy()
    (H, W) = image.shape[:2]

    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (newW, newH) = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)

    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]


    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"]

    # load the pre-trained EAST text detector
    # print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet(pth_detector)

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
            (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)


    # grab the number of rows & columns from the scores volume, then
    # initialize our set of bounding box rectangles & corresponding confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
            # extract the scores (probabilities), followed by the geometrical
            # data used to derive potential bounding box coordinates that surround text
            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]

            # loop over the number of columns
            for x in range(0, numCols):
                    # if our score does not have sufficient probability, ignore it
                    if scoresData[x] < 0.999:
                            continue

                    # compute the offset factor as our resulting feature maps will
                    # be 4x smaller than the input image
                    (offsetX, offsetY) = (x * 4.0, y * 4.0)

                    # extract rotation angle for the prediction and then compute sin & cosine
                    angle = anglesData[x]
                    cos = np.cos(angle)
                    sin = np.sin(angle)

                    # use geometry volume to derive width and height of the bounding box
                    h = xData0[x] + xData2[x]
                    w = xData1[x] + xData3[x]

                    # compute both starting & ending (x, y)-coordinates for
                    # the text prediction bounding box
                    endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                    endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                    startX = int(endX - w)
                    startY = int(endY - h)

                    # add box coordinates & probability score to respective lists
                    rects.append((startX, startY, endX, endY))
                    confidences.append(scoresData[x])                
                    
                    # apply non-maxima suppression to suppress weak, overlapping bounding
                    # boxes = non_max_suppression(np.array(rects), probs=confidences)
                    # print(boxes)
                    
    # some checks that there was detected indeed text in the image                
    if len(rects) == 0:
        print("--- no text found --- sample_path inserted in the txt")
        new_txt = "sample"
        path = os.path.join(pth0, 'sample') 
        fs = open(os.path.join(pth0 + "0mv_file.txt"), "a")
        fs.write("mkdir"+" "+'"'+str(path)+'"'+";"+'\n')
        fs.write("mv"+" "+'"'+str(match)+'"'+" "+'"'+path+'"'+";"+'\n')
        fs.close()
        
        # print("NO TEXT WAS FOUND ON IMAGE")
        # print(match)
        # print(len(rects))
    elif len(rects) > 0:
        # print("Get the best rects values based on max confidence")
        max_conf = max(confidences) 
        pos_max_conf=confidences.index(max_conf)
        rects_best = []
        rects_best.append(rects[pos_max_conf])
        # print(max_conf)
        # print(rects_best)

        # loop over the bounding boxes
        for (startX, startY, endX, endY) in rects_best:
                box = [[[]]]
                # scale the bounding box coordinates based on the respective ratios
                startX = int(startX * rW)
                startY = int(startY * rH)
                endX = int(endX * rW)
                endY = int(endY * rH)
                new_startY = (startY)

                # if negative, zero it
                if (startY < 0):  startY = 0
                if (endY < 0):    endY =   0
                if (startX < 0):  startX = 0
                if (endX < 0):    endX =   0

                #print(startX)
                #print(startY)
                #print(endX)
                #print(endY)
                #print(rW)
                #print(rH)

                # manipulating manually the dimensions of crop
                new_startY = (startY)
                if (new_startY < 0):         # if negative, replace it
                    new_startY = startY
                
                new_endY = (endY+5)
                if (new_endY < 0):         # if negative, replace it
                    new_endY = endY
                    
                new_startX = (startX-100)
                if (new_startX < 0):         # if negative, replace it
                    new_startX = startX
                    
                new_endX = (endX + 170)
                if (new_endX < 0):         # if negative, replace it
                    new_endX = endX
                
                # Cropping the image
                # print(img_ok.shape)
                height, width = img_ok.shape[:2]
                # print("width %s" % width)
                # print("height %s" % height)
                # print(new_startX)
                # print(new_startY)
                # print("old" + str(startY))
                # print(new_endX)
                # print(new_endY)
                
                crop_image = img_ok[(new_startY):(new_endY), (new_startX):(new_endX)]
                #print(new_startY, new_endY, new_startX, new_endX)
                
                # Extract the text from the cropped image
                txt = pytesseract.image_to_string(crop_image, config=cfg)             

                # text cleaning / join multiliners & spaces / drop all chars after space
                sep = ' '
                stripped_txt = txt.split(sep, 1)[0]
                new_txt = re.sub(r"\s+", "", stripped_txt)
                
                # if text is shorter than 3 chars then replace it with 'sample'
                if len(new_txt) < 3:
                    new_txt = "sample"
                print(new_txt)

                # print(os.path.join(match + ".txt")) 
                # write extracted text on a txt file
                f = open( os.path.join(match + ".txt"), "w")
                f.write(new_txt)
                f.close()
                
                # Save cropped image ?
                #cv2.imwrite(os.path.join( match + "_cropped.jpg"), crop_image)
            
                # show cropped image ?
                #cv2.imshow("crop", crop_image)
                #cv2.waitKey()

                path = os.path.join(pth0, new_txt) 
                # print(path)
                
                f2 = open( os.path.join(pth0 + "0mv_file.txt"), "a")
                f2.write("mkdir"+" "+'"'+str(path)+'"'+";"+'\n')
                f2.write("mv"+" "+'"'+str(match)+'"'+" "+'"'+path+'"'+";"+'\n')
                f2.close()



