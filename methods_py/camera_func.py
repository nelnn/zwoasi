import os
import time
from PIL import Image
import zwoasi as asi
import tkinter as tk
from tabulate import tabulate


'''try to get entry values, if invalid set to default vaules'''
def try_except(entry, default_value):
    try:
        value = int(entry.get())
    except ValueError:
        value = default_value
        entry.delete(0,tk.END)
        entry.insert(-1,value)
    return value

'''Capture Photo'''
def capture(camera, entry1, entry2, entry3, entry4, entry5, img_counter): 
    exposure = try_except(entry2, 3000) # defalut exposure = 3000ms
    interval = try_except(entry1, 10) # defalut interval = 10s
    gain = try_except(entry3, 1) # defalut gain = 1
    MaxBV = try_except(entry4, 1600000000) # default MaxBV = 1600000000
    MinBV = try_except(entry5, 1500000000) # default MinBV = 1500000000
    settings = [["Interval (s)", interval], ["Exposure(s)", exposure/1000000], ["Gain", gain]]
    print("\n------------------------------------------------------------------------------------------------------------\n")
    print(tabulate(settings, headers=["Settings", "Value"]))
    camera.set_control_value(asi.ASI_GAIN, int(gain))
    camera.set_control_value(asi.ASI_EXPOSURE, int(exposure)) # microseconds  
    try:
        # Force any single exposure to be halted
        camera.stop_video_capture()
        camera.stop_exposure()
    except (KeyboardInterrupt, SystemExit):
        raise
    # datetime
    date = time.strftime("%Y-%m-%d")
    date1 = date.replace('-','')
    timehk = time.strftime("%H:%M:%S")
    timehk1 = timehk.replace(':','')
    date_time = date + " " + timehk
    path = "photos/" + date1 # path named by date
    photo_id = date1 + "-" + timehk1
    # Create folder named by date of today if it is not existing.
    if not os.path.exists(path): 
        os.makedirs(path)
    print('\nCapturing a RGB image %s.jpg...\n' %(photo_id))
    camera.capture(filename=(os.path.join(path,str(photo_id)+".jpg")))
    img_counter += 1
    print('Image (%d) saved.\n' %(img_counter))
    return exposure, interval, gain, img_counter, MaxBV, MinBV, path, photo_id, date_time, date, timehk


'''Fixed Setting'''
def fixed_setting(path, photo_id):
    imgopen = Image.open(os.path.join(path,str(photo_id)+".jpg"))
    pixelvalue = imgopen.getdata()
    pixelvaluesum = sum(map(sum, pixelvalue))
    return pixelvaluesum

'''Dynamic Setting: prioritize exposure first then gain'''
def dynamic_setting(entry2, entry3, exposure, gain, MaxBV, MinBV, imgopen):
    reduction_factor = 1
    pixelvalue = imgopen.getdata()
    # for mono image, use sum(pixelvalue)
    # for RGB image, use sum(map(sum, pixelvalue))
    pixelvaluesum = sum(map(sum, pixelvalue))
    imgopen.close()   
    print("Total pixel value sum: "+ str(pixelvaluesum) + "\n")
    if pixelvaluesum>MaxBV:
        if int(gain) < 11:
            gain = 1
            print("Gain approaches to minimum, set to 1")
            reduction_factor=round((MinBV/pixelvaluesum),3)
            new_exposure=int(float(exposure)*reduction_factor)

            if new_exposure <= 100:
                exposure = 100
                reduction_factor = 1
                print("Exposure reaches minimun  at 100 microsecond, reduction_factor reset to 1.\n")
            else:
                exposure = round(new_exposure,5)
                print("The image is too bright. Exposure will be reduced to " + str(new_exposure/1000000)+ " second(s). Factor: " + str(reduction_factor) + "\n")
        else:
            gain = int(gain) - 10
            print("The image is too bright. GAIN will be reduced by 10\n")
        
    if pixelvaluesum < MinBV:
        reduction_factor = round((MaxBV/pixelvaluesum),3)
        new_exposure = int(float(exposure)*reduction_factor)
        if new_exposure > 30000000:
            exposure = 30000000
            reduction_factor = 1
            if gain < 600:
                gain = int(gain) + 10
                print("Exposure reaches maximum(30s), Gain increased by 10, reduction_factor reset to 1.\n")
            else:
                gain = 600
                print("Gain approaches to maximum, set to 600\n")
        else:
            exposure = new_exposure
            print("The image is too dark. Exposure will be increased to " + str(new_exposure/1000000)+ "second(s). Factor:" + str(reduction_factor)+"\n")
        
    # settings = [["New Exposure (s)", exposure/1000000], ["New Gain", gain], ["Factor", reduction_factor]]
    # print(tabulate(settings, headers=["Settings", "Value"]))

    entry2.delete(0,tk.END)
    entry2.insert(-1,exposure)
    entry3.delete(0,tk.END)
    entry3.insert(-1,gain)
    return pixelvaluesum



'''Auto Interval'''
def Auto_interval(entry1, entry2):
    exposure = int(entry2.get())
    if exposure >= 30000000:
        print("EXPOSURE cannot be larger than 30 seconds")
        exposure = 30000000
        interval = 0
        entry1.delete(0,tk.END)
        entry2.delete(0,tk.END)
        entry1.insert(-1,interval)
        entry2.insert(-1,exposure)               
    elif exposure <= 3000000:
        # when exprouse is smaller than 3 seconds, the interval = 5 minutes
        # do not need that many images in day time
        interval = 300
        entry1.delete(0,tk.END)
        entry1.insert(-1,interval)
    else:
        # if 3s < exposure < 30s, the interval = 60 - exposure     
        interval = int(60 - (int(exposure)/1000000))
        entry1.delete(0,tk.END)
        entry1.insert(-1,interval)
    print("Invterval = "+ str(interval) + "s; EXPOSURE = " +str(int(exposure)/1000000)+ "s")
    return interval