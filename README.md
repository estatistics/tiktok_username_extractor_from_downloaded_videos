# tiktok OCR username extractor from downloaded videos

This is a tiktok username extractor from videos that you have downloaded directly from tiktok\
It MUST include as last frame a black frame with the logo of Tiktok and the username\
at the center of the frame. 

Part of code was adopted from [the github of diewland](https://github.com/diewland/text-detection-opencv-east/blob/master/opencv_ocr_image.py)
Note that by trial and error `frozen_east_text_detection` is better for detecting the tiktok username text than tesseract. 

## Why this extractor ? 
The extractor used on 9000+ downloaded tiktok videos containing or not in the final frame the tiktok username.\
Results were not perfect, but very good especially, if you have many videos of the same user. \
Let's say that you have `50 vids from user A`, `70 from user B` and `60 vids without` containing the specific last frame with username.\
The python script will place these videos, respectively, under Folder userA & userb, and it will place all the rest unrecognized ones under `SAMPLE folder`.

## Requirements
- python3
- tesseract
- auto detetion for shapes (free on web) -> frozen_east_text_detection.pb\
  you may place it in the same folder as this python script\
`wget https://github.com/oyyd/frozen_east_text_detection.pb/blob/master/frozen_east_text_detection.pb`
- ffmpeg (for image manipulation)
- im6 (magick for image manipulation)

## python 3 packages
- cv2: `sudo apt-get install python3-opencv`
- pytesseract
- numpy 
- pillow
- matplotlib
#### WARNING - The following code may ruin your system. Instead you may follow the official way creating an virtual python env
#### FINAL WARNING - DONT RUN IT if you dont know what it does
`sudo pip3 install --break-system-packages  pytesseract numpy pillow matplotlib`

## Explaining tesseract options
This line configure pytesseract (please refer to tesseract manual/help pages for more)\
`cfg = '--psm 6 --oem 1  -c load_system_dawg=false -c load_freq_dawg=false -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ_.`

- psm - what mode of ocr to use
- oem - what language machine to use
- `load_system_dawg=false load_freq_dawg=false`\
 disable the word mode as usernames are not "words" but letters/digits/underscore
- whitelisting (allow) these characters for OCR as\
  official tiktok page says that are allowed as characters in username\
  `tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIKLMNOPQRSTUVWXYZ_.'`

## Precautions
- Dont use this script on unbacked tiktok videos
- Copy some downloaded tiktok videos to a temporary folder to test if this code is working well
- The character "@" in OCR found as "G" or "2". I havent tried to whitelist "@".
- Check that paths were set correctly inside py script from you
- This script must be manipulated in a text editor eg. geany or a code environment like visual studio before execution.
- Folders produced from username with start character "." may are treated as hidden folders from your system.
    - You must enable hidden folder view. 

## Variables to set / manipulate
### set paths 
- you must set `pth0` in py script - the path that your videos will be procceed
- you must set `pth_for_frozen_east_text_detection` in py script where the pb file exists

### other vars
- `new_startY, new_endY, new_startX, new_endX` are the dimensions in pixel of the box drawn over the recognized text area 
  eg. `100 150 200 250` will create a boxby joining these pixel dots
  - These vars has some extra weights in order to produce better results. You may change them as you wish
- The original code produced multiple confidence levels (multiple dimensions of boxes) over the detected text
  - only the highest (best) confidence level is used here. A cut off score of `0.999` exists as preliminary check.
- You may change the detected picture format from `".jpg"` to something else that cv2 supports
- If Text was not detected, it may print `print("NO TEXT WAS FOUND ON IMAGE")`.
  - Then the name of `"sample"` folder will be given in order to move all unrecognized tiktok videos under it.
  - The same will happen if the recognized text is shorter than 3 characters. It will be replaced with `'sample'` text.

### Debugging ?
- Uncommenting both `cv2.imshow` and `cv2.waitKey()` you can see the picture/s with username produced.
- All print commands exists in this script for debbuging reasons, feel free to tried them if you like to check what happens per step.

### What files this script produces ?
- You may uncomment `cv2.imwrite(os.path.join( match + "_cropped.jpg"), crop_image), crop_image)`
   - if you like to save the cropped image with the detected text area.
- You may comment these lines if you dont want the recognized username to be saved in a `"your_tiktok_video_filename".jpg.txt` file.
```
                f = open( os.path.join(match + ".txt"), "w")
                f.write(new_txt)
                f.close()
```

#### THE ESSENTIAL PART OF THE SCRIPT 
- You may comment these lines if you dont want to produce a single file `0mv_file.txt` that contains commands to
- Create directories (all in doublequotes) based on the recognized tiktok username 
- Dont worry - no illegal - characters but WARNING  - "." - is legal". It may treated as hidden folders if it is the 1st char. 
- and then transfer all downloaded tiktok files under their respective `username_folder`.

This is done by producing lines like:\
` mkdir "pth/username_folder"; (next line) mv "pth/downloaded_video_tiktok pth/username_folder/"; `
- Then, this txt file may be renamed as ".sh" and give permisions to executed, in order to run "mkdir" and "mv" commands. 
  
- File is opened as "append". For every run ADD lines in the file.
- You must do this manually `delete 0mv_file.txt`, if you would like, after each run
- Otherwise you may have multiple duplicated lines after each run. 
    
                f2 = open( os.path.join(pth0 + "0mv_file.txt"), "a")
                f2.write("mkdir"+" "+'"'+str(path)+'"'+";"+'\n')
                f2.write("mv"+" "+'"'+str(match)+'"'+" "+'"'+path+'"'+";"+'\n')
                f2.close()
                
## What the script does ?
In the specified folder, check all files ".jpg" under the path that you provided inside the scipt.\
They are saved in a variable "matches". Then image is proccessed as numpy area code. \
Then the code try to detect the text area using frozen_east_text_detection.\
Then using best confidence, extract the final dimension of the best box\
that will be used to crop the detected text area. \

Finally, the code, will provide you with a file name "0mv_file.txt" that it will\
contains commands to create folders according to detected username text, and \
then commands to move downloaded tiktok video files under them, respectively. 


## STEPS to do it
STEP 1 - extract the last frame from each downloaded tiktok video that\
it may contain the tiktok username centered in the image together with\
the tiktok logo in a black screen as background.

Warning: if audio is shorter/bigger than video then incorrect frame may produced\
`for vids in *.mp4; do ffmpeg -sseof -1 -i "$vids" -vsync 0 -q:v 1 -update true "$vids".jpg; done`

STEP 2 - manipulate extracted frame
- you cant merge these two commands due to crop/resize are handled differently (???)
- and it is confused - it process the same multiple times (bug?)
- crop frame / resize / sharpen for better results\
1st comman: `for file in *.jpg; do convert "$file" -crop 100%x15%+0+500  -quality 100  "/mnt/sdd1/tiktok_videos/""$(basename "$file")" ; done;`\
2nd command: `for file in *.jpg; do convert "$file" -resize 200% -sharpen 0x10 -quality 100  "/mnt/sdd1/tiktok_videos/""$(basename "$file")" ; done;`

STEP 3 - Running the scipt\
After changing the `path` variables and change whatever other\
variables you would like to change,\
run the python code.

STEP 4 - Execution of produced file\
Execute the produced `0mv_file.txt` as script to produce folders based on the detected tiktok username,
and move `"JPG"` files in the respective `username_folders`. This is as precaution.\
You must open `0mv_file.txt` and remove ".jpg" extension in order to move `mp4` files\
in these folders instead of the respective extracted frames. 

## Contribution
Feel free to contribute or comment or share lists with tiktok videos.

                


