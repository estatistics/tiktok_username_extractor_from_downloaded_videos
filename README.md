# tiktok OCR username extractor from downloaded videos

This is a tiktok username extractor from videos that you have downloaded directly from tiktok\
It MUST include as last frame a black frame with the logo of Tiktok and the username\
at the center of the frame. 

Part of code was adopted from [the github of diewland](https://github.com/diewland/text-detection-opencv-east/blob/master/opencv_ocr_image.py)
Note that by trial and error frozen_east_text_detection is better for detecting the tiktok username text than tesseract. 

## Why this extractor ? 
The extractor used on 9000+ downloaded tiktok videos containing or not in the final frame the tiktok username.\
Results were not perfect, but very good especially, if you have many videos of the same user. \
Let's say that you have `50 vids from user A`, `70 from user B` and `60 vids without` containing the specific last frame with username.\
The python script will place these videos, respectively, under Folder userA & userb, and it will place all the rest unrecognized ones under `SAMPLE folder`.

## Requirements
- python3
- tesseract
- auto detetion for shapes (free on web) -> frozen_east_text_detection.pb\
  you may place it in the same folder as this python script
`wget https://github.com/oyyd/frozen_east_text_detection.pb/blob/master/frozen_east_text_detection.pb`

## python 3 packages
- cv2: `sudo apt-get install python3-opencv`
- pytesseract
- numpy 
- pillow
- matplotlib
#### WARNING - This may ruin your system 
#### Instead you may follow the official way creating an virtual python env
`sudo pip3 install --break-system-packages  pytesseract numpy pillow matplotlib`

## Explaining tesseract options
This line configure pytesseract (please refer to tesseract manual/help pages for more)
`cfg = '--psm 6 --oem 1  -c load_system_dawg=false -c load_freq_dawg=false -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ_.'`

- psm - what mode of ocr to use
- oem - what language machine to use
-load_system_dawg=false load_freq_dawg=false
 disable the word mode as usernames are not "words" but letters/digits/underscore
- whitelisting (allow) these characters for OCR as
  official tiktok page says that are allowed as characters in username
  `tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ_.'`

## Precautions
- Dont use this script on unbacked tiktok videos
- Copy some downloaded tiktok videos to a temporary folder to test if this code is working well
- Check that paths were set correctly inside py script from you
- The character "@" in OCR found as "G" or "2". I havent tried to whitelist "@".
   
## Variables to set / manipulate
### path sets
- you must set pth0 in py script - the path that your videos will be procceed
- you must set pth_for_frozen_east_text_detection in py script where the pb file exists

- new_startY, new_endY, new_startX, new_endX are the dimensions in pixel of the box drawn over the recognized text area 
  eg. 100 150 200 250 will create a box at these pixels by joining these pixel dots
  - These vars has some extra weights in order to produce better results. You may change them as you wish
- the original code produced multiple confidence levels for the box pixels over the detected text
  - only the highest (best) confidence level is used here. A cut off score of 0.999 exists.
- uncommenting both `cv2.imshow` and `cv2.waitKey()` you can see the picture/s with username produced
- You may uncomment `cv2.imwrite(os.path.join( match + "_cropped.jpg"), crop_image), crop_image)`
   - if you like to save the cropped image with the detected text area.
- You may change the detected picture format from ".jpg" to something else that cv2 supports


## What the script does ?
In the specified folder, check all files ".jpg" under the path that you provided inside the scipt.\
They are saved in a variable "matches". Then image is proccessed as numpy area code. \
Then the code try to detect the text area using 




