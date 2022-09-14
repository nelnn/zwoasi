import cv2
import numpy as np
import glob
 
img_array = []
folder_path = 'C:/Users/hkspm.yp/Desktop/all sky images/Eastdam23072022/*.jpg'
for filename in glob.glob(folder_path):
    img = cv2.imread(str(filename))
    height, width, channels = img.shape
    size = (width, height)
    img_array.append(img)

video_name = r'C:\Users\hkspm.yp\Desktop\all sky images\time lapse video\Eastdam23072022.mp4'
out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 10, size) # 10 fps
 
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()
