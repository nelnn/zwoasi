#!/usr/bin/python
# -*- coding: UTF-8 -*-

import zwoasi as asi
import os
import time
import tkinter as tk
from tkinter import simpledialog
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import ephem
import socket

def Auto_interval():
    if Checkbutton1_v1.get()==1:
        if not entry2.get():
            print("PLease input EXPOSURE first")
        else:
            #entry1.delete(0, tk.END)
            #entry1.insert(-1,55) # set to 55 in real appliction
            global EXPOSURE
            global INTERVAL
            EXPOSURE = int(entry2.get())
            #if int(EXPOSURE) >5000000: # when exposure is large then 5 seconds
            if int(EXPOSURE) >= 30000000:
                print("EXPOSURE cannot be larger than 30 seconds")
                entry2.delete(0, tk.END)
                entry2.insert(-1,30000000)
                EXPOSURE = int(entry2.get())
                INTERVAL = 1
                entry1.delete(0, tk.END)
                entry1.insert(-1,INTERVAL)
                    
            else:
                #when exprouse is smaller than 30 seconds, the interval = 60 - (s)      
                INTERVAL = int(60 - (int(EXPOSURE)/1000000)) 
                entry1.delete(0, tk.END)
                entry1.insert(-1,INTERVAL)
            print("Invterval = "+ str(INTERVAL) + "second(s); EXPOSURE = " +str(int(EXPOSURE)/1000000)+ "second(s)")
            #else:
                #INTERVAL = entry1.get()
                #print("Exp is smaller than 5 second. Invterval = "+ str(INTERVAL) + "second(s)")
    if Checkbutton1_v1.get()==0:
        #entry1.delete(0, tk.END)
        print("Please input interval")

#________________________ Below create entry box

root= tk.Tk()

canvas1 = tk.Canvas(root, width = 400, height = 500,  relief = 'raised')
canvas1.pack()

label0 = tk.Label(root, text='All Sky Camera Panel')
label0.config(font=('helvetica', 14))
canvas1.create_window(200, 25, window=label0)

label1 = tk.Label(root, text='Interval before next image (second):')    # text box
label1.config(font=('helvetica', 10))
canvas1.create_window(200, 90, window=label1)
entry1 = tk.Entry (root)    # entry box
canvas1.create_window(200, 110, window=entry1)

Checkbutton1_v1=tk.IntVar()
Checkbutton1 = tk.Checkbutton(root, text='Auto',variable=Checkbutton1_v1, onvalue=1,offvalue=0,command=Auto_interval).place(x = 300, y = 100)

label2 = tk.Label(root, text='Exposure (microsecond):\n 1,000 = 1 millisecond; 1,000,000 = 1 second ')
label2.config(font=('helvetica', 10))
canvas1.create_window(200, 150, window=label2)
entry2 = tk.Entry (root) 
canvas1.create_window(200, 180, window=entry2)
entry2.insert(-1,1000000)

label3 = tk.Label(root, text='Enter Gain (Start from Min=1):')
label3.config(font=('helvetica', 10))
canvas1.create_window(200, 220, window=label3)
entry3 = tk.Entry (root) 
canvas1.create_window(200, 240, window=entry3)
entry3.insert(-1,1)

#maximum value for 8 bits ASI290mm is 541,073,280 = (1936 x 1096 x 255)
label4 = tk.Label(root, text='Maximum Brightness Value:\n Suggested for IMX533: 1,600,000,000')
label4.config(font=('helvetica', 10))
canvas1.create_window(200, 280, window=label4)
entry4 = tk.Entry (root) 
canvas1.create_window(200, 310, window=entry4)
entry4.insert(-1,1600000000)

label5 = tk.Label(root, text='Minimum Brightness Value:\n Suggested for IMX533: 1,500,000,000')
label5.config(font=('helvetica', 10))
canvas1.create_window(200, 350, window=label5)
entry5 = tk.Entry (root) 
canvas1.create_window(200, 380, window=entry5)
entry5.insert(-1,1500000000)

#Load ZWO SDK 

asi.init('ASI_SDK\ASICamera2.dll')

#Get camera information and print them on Shell

num_cameras = asi.get_num_cameras()
if num_cameras == 0:
    raise ValueError('No cameras found')

camera_id = 0  # use first camera from list
cameras_found = asi.list_cameras()
print(cameras_found)
camera = asi.Camera(camera_id)
camera_info = camera.get_camera_property()
print(camera_info)
    
    # Get all of the camera controls
print('')
print('Camera controls:')
controls = camera.get_controls()
for cn in sorted(controls.keys()):
    print('    %s:' % cn)
    for k in sorted(controls[cn].keys()):
        print('        %s: %s' % (k, repr(controls[cn][k])))

    # Use minimum USB bandwidth permitted
camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])
    
    # Set some sensible defaults. They will need adjusting depending upon
    # the sensitivity, lens and lighting conditions used.
camera.disable_dark_subtract()
#------------------------------

reduction_factor = 1
gain_factor = 0
img_counter = 0
print("\nPlease input data in the window and click Start Recording.\n")

def Confirmdata ():
    global INTERVAL
    INTERVAL = entry1.get()  # get value from entry box
    try:
        INTERVAL=int(INTERVAL)  # if wrong input, default 10sec
    except ValueError:
        INTERVAL=10
        pass
 
    EXPOSURE = entry2.get()
    try:
        EXPOSURE=int(EXPOSURE)  # if wrong input, default 3000ms
    except ValueError:
        EXPOSURE=3000
        pass
    
    GAIN = entry3.get()
    try:
        GAIN=int(GAIN)  # if wrong input, default 200
    except ValueError:
        GAIN=200
        pass
    print("Setting: Interval= %d second(s); Exposure= %.6f second(s); Gain= %d. Only integer is allowed.\n" %(INTERVAL, EXPOSURE/1000000, GAIN))

#________________________Below Camera take photos
def getPhotos ():
    

    global reduction_factor
    global EXPOSURE
    global INTERVAL
    EXPOSURE = entry2.get()
    try:
        EXPOSURE=int(EXPOSURE)  # if wrong input, default 3000ms
    except ValueError:
        EXPOSURE=3000
        pass
    
    #Auto_interval()
    INTERVAL = entry1.get()  # get value from entry box
    try:
        INTERVAL=int(INTERVAL)  # if wrong input, default 10sec
    except ValueError:
        INTERVAL=10
        pass    
    
    global GAIN
    GAIN = entry3.get()
    try:
        GAIN=int(GAIN)  # if wrong input, default 200
    except ValueError:
        GAIN=200
        pass
    
    MaxBV = entry4.get()
    try:
        MaxBV=int(MaxBV)  # if wrong input, default 1600000000
    except ValueError:
        MaxBV=1600000000
        pass
    
    MinBV = entry5.get()
    try:
        MinBV=int(MinBV)  # if wrong input, default 1500000000
    except ValueError:
        MinBV=1500000000
        pass
    
    print("Setting: Interval= %d second(s); Exposure= %.6f second(s); Gain= %d. Only integer is allowed.\n" %(INTERVAL, EXPOSURE/1000000, GAIN))
  
    camera.set_control_value(asi.ASI_GAIN, int(GAIN))
    camera.set_control_value(asi.ASI_EXPOSURE, int(EXPOSURE)) # microseconds
    #camera.set_control_value(asi.ASI_EXPOSURE, 3000) # microseconds
    camera.set_control_value(asi.ASI_WB_B, 99)
    camera.set_control_value(asi.ASI_WB_R, 50)
    camera.set_control_value(asi.ASI_GAMMA, 50)
    camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
    camera.set_control_value(asi.ASI_FLIP, 0)
    camera.set_image_type(asi.ASI_IMG_RGB24) #RAW8=bit; RAW16=16bit; RGB24=color
    
    try:
        # Force any single exposure to be halted
        camera.stop_video_capture()
        camera.stop_exposure()
    except (KeyboardInterrupt, SystemExit):
        raise


    if root.run:
        path=time.strftime("%Y%m%d") #path named by date
        global name
        name=time.strftime("%Y%m%d-%Hh%Mm%Ss")     
        if not os.path.exists(path): # Create folder named by date of today if it is not existing.
           os.mkdir(path)
        print('Capturing a RGB24 image %s.jpg...Exposure time = %s second(s)\n' %(name, EXPOSURE/1000000))
        camera.capture (filename=(os.path.join(path,str(name)+".jpg"))) ########### CAPTURE ############




        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect(('169.254.184.252',10001))
        # s.send('rx'.encode())
        # data = s.recv(1024).decode("utf-8")
        # if data == '':
        #     raise RuntimeError
        #     "socket connection broken"
        # global sqm
        # sqm = data.replace(" ", "").replace("m", "").split(',')[1]
        # s.close 






        global img_counter
        img_counter += 1
        print('Image (%d) saved.\n' %(img_counter))
        # open the image and calculate the pixel value
        global imgopen
        imgopen = Image.open(os.path.join(path,str(name)+".jpg"))
        pixelvalue = imgopen.getdata()
        # for mono image, use sum(pixelvalue)
        # for RGB image, use sum(map(sum, pixelvalue))
        pixelvaluesum = sum(map(sum, pixelvalue))   
        print("Total pixel value sum is: "+ str(pixelvaluesum))
        EXPOSURE = entry2.get()
        if pixelvaluesum>MaxBV:
            if int(GAIN)<11:
                entry3.delete(0, tk.END)
                entry3.insert(-1,1)
                print("Gain approaches to minimum, set to 1")
                reduction_factor=round((MinBV/pixelvaluesum),3)
                new_exposure=int(float(EXPOSURE)*reduction_factor)
                if new_exposure <=100: # if exprosure time is smaller than 100 microseconds
                   #reduction_factor=round(reduction_factor/(MaxBV/pixelvaluesum),3)
                   entry2.delete(0, tk.END)
                   entry2.insert(-1,100)
                   reduction_factor=1
                   EXPOSURE = entry2.get()
                   print("Exposure reaches minimun  at 100 microsecond, reduction_factor reset to 1.\n")
                else:
                   entry2.delete(0, tk.END)
                   entry2.insert(-1,round(new_exposure,5))
                   print("The image is too bright. Exposure will be reduced by a factor of " + str(reduction_factor))
                   print("Next Exposure time: " + str(new_exposure)+" microsecond(s) or " + str(new_exposure/1000000)+ "second(s)")
            else:
                entry3.delete(0, tk.END)
                entry3.insert(-1,int(GAIN)-10)
                print("The image is too bright. GAIN will be reduced by 10")
        if pixelvaluesum<MinBV:
            reduction_factor=round((MaxBV/pixelvaluesum),3)
            new_exposure=int(float(EXPOSURE)*reduction_factor)
            if new_exposure >=30000000: # if exprosure time is larger than 30 seconds
               entry2.delete(0, tk.END)
               entry2.insert(-1,30000000)
               reduction_factor=1
               EXPOSURE = entry2.get()
               if GAIN<600:
                  #global gain_factor
                  #gain_factor=gain_factor+10
                  entry3.delete(0, tk.END)
                  entry3.insert(-1,int(GAIN)+10)
                  print("Exposure reaches maximum(30s), Gain increased by 10, reduction_factor reset to 1.\n")
               else:
                  GAIN=600
                  print("Gain approaches to maximum, set to 600\n")
            else:
                entry2.delete(0, tk.END)
                entry2.insert(-1,new_exposure)
                print("The image is too dark. Exposure will be increased by a factor of " + str(reduction_factor))
                print("Next Exposure time: " + str(new_exposure)+" microsecond(s)\n")
        Auto_interval()
        root.after(INTERVAL*1000, getPhotos)
        print('Again after %s seconds...(press stop to stop)\n' %(INTERVAL))
        # run the text() function to draw test on image
        text()
        print('Text added')

    else:
         print('Recording Stopped.')   

#________________________Below draw text on image
def text():

    #get exposure, gain from ZWOASI.py
    etime=float(EXPOSURE)/1000000 # etime is given by ZWOASI programme
    if etime<0.01:
        etime="<0.01"
    else:
        etime="{:.2f}".format(etime)
    exposure_time="曝光 Exposure: "+ str(etime) +" 秒second(s)"
    gain_value="增益 Gain: "+ str(GAIN)
    sqm_value = "SQM: "+str(sqm)

    # get date, time and moon phase
    date=time.strftime("日期 Date: %Y.%m.%d")
    timehk=time.strftime("時間 Time (UTC+8): %H:%M:%S+" + str(etime))
    moonphase="月相 Moon Phase: " + str(round(ephem.Moon(datetime.now()).moon_phase, 2)) #get moon phase in 2 digits


    # open an image and get its size
    #img = Image.open('allsky.png')
    width, height = imgopen.size

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(imgopen)

    # Assign fixed texts to different variables
    location1_text="地點 Location:\n 尖沙咀香港太空館\nHong Kong Space Museum, Tsim Sha Tsui "
    location2_text="地點 Location:\n 西貢天文公園 Astropark, Sai Kung"
    location3_text="地點 Location:\n 西貢麥理浩夫人度假村 Lady MacLehose Holiday Village, Sai Kung"
    cardinal_point_E="東 East"
    cardinal_point_S="南 South"
    cardinal_point_W="西 West"
    cardinal_point_N="北 North"

    # Custom font style and font size
    Chinese=ImageFont.truetype('font/NotoSansHK-Thin.otf',55)
    Chinese2=ImageFont.truetype('font/NotoSansHK-Thin.otf',60)

    # Add Text to an image at a position
    I1.text((50, 50), date,font=Chinese2)
    I1.text((50, 150), timehk,font=Chinese2)
    I1.text((50, 250), moonphase,font=Chinese2)
    I1.text((width-900, 50), exposure_time,font=Chinese2)
    I1.text((width-900, 150), gain_value,font=Chinese2)
   
   
   
    I1.text((width-900, 250), sqm_value,font=Chinese2)




    I1.text((width-1100, height-320), location1_text,font=Chinese, align="right")

    # position of four cardinal points
    I1.text((70, height/2), cardinal_point_E,font=Chinese)
    I1.text(((width/2)-100, height-250), cardinal_point_S,font=Chinese)
    I1.text((width-290, height/2), cardinal_point_W,font=Chinese)
    I1.text(((width/2)-100, 230), cardinal_point_N,font=Chinese)

    # add logo on the image
    I2 = Image.open('SpM_Logo_1000.png')
    imgopen.paste(I2,(50, height-300),I2)

    # Display edited image
    #imgopen.show()
     
    # Save the edited image
    imgopen.save("allsky2"+str(name)+".jpg")
    imgopen.close()

def stop ():
    root.run=False
    print('Stopping...please wait')
    global reduction_factor
    reduction_factor = 1
    global gain_factor
    gain_factor=0
    
def load ():
    root.run=True
  
button1 = tk.Button(text='Confirm data', command=Confirmdata, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(200, 420, window=button1)

button1 = tk.Button(text='Start Recording', command=lambda:[load(),getPhotos()], bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(100, 470, window=button1)

button1 = tk.Button(text='Stop', command=stop, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(300, 470, window=button1)


root.mainloop()







