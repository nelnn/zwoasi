#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import psutil # show cpu and ram usage
from shutil import move # move file directory 
import os
import sys 
import platform # check computer os
import zwoasi as asi
import socket
import time
from datetime import datetime, timedelta
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageStat
import ephem # moon phase
import csv
import requests 
import traceback # tracks error messages

''' NO GUI, Programme runs upon start'''
class App():
    def __init__(self):
        ######################################################
        # settings
        sqm_ip = "169.254.247.96" # "192.168.8.148" 
        url = "https://3.39.172.216/allsky/upload"    # upload url path (please edit IP address or domain name)
        token_key = "qC6a_x8GuoqmFpiW8i6duDsFpsqNqluYbb1DGY1u4yE"    # for server authentication
        location = "hkspm" # hkspm / astropark / lmhv
        windows_driver = "ASI_Windows/lib/x64/ASICamera2.dll"
        linux_driver = 'ASI_linux/lib/armv7/libASICamera2.so.1.25'
        MaxBV = 1750000000
        MinBV = 1450000000
        ######################################################
        # initial values
        self.MaxBV = MaxBV
        self.MinBV = MinBV
        self.gain = 1
        self.max_gain = 600
        self.gain_step = 10
        self.exposure = 100 # microsecound
        self.min_exposure = 32 # min exposure
        self.max_exposure = 30000000 # max exposure: 30s
        self.interval = 0
        self.img_counter = 1
        self.run = True
        loc_name = ["hkspm", "astropark", "lmhv"]
        loc_index = loc_name.index(location)
        # initialise camera
        camera = detect_camera(windows_driver, linux_driver)
        detect_sqm(sqm_ip)
        print("-------------------------------------------------------------------------------------------------\n")
        while self.run:
            ti = time.time() # start timer
            # Take photo
            t_cap, full_photo_path, date_time, date, timehk, exposureTxt, gainTxt = self.capture(camera)
            # sometimes in day time even min exposure exceeds the pixel sum, we counter this by increasing maxbv
            self.MaxBV = 2000000000 if self.exposure == self.min_exposure else MaxBV
            # Evaluate camera settings based on exposure and gain
            t_set, pixelvaluesum = self.dynamic_setting(full_photo_path)
            # if image is not within pixel range AND exposure < 10s, keep taking until it is
            if self.exposure < 10000000 and pixelvaluesum < self.MinBV or pixelvaluesum > self.MaxBV:
                move(full_photo_path, "source/archive.jpg")
                print("--------------------------------------<<Tuning Brightness>>--------------------------------------\n")
            else:    
                # Measure SQM value
                sqm_value = sqm_reader(sqm_ip)
                # add text to image
                t_text = text(full_photo_path, sqm_value, date, timehk, loc_index, exposureTxt, gainTxt)
                # Save data to csv
                save_csv(location, date_time, sqm_value, pixelvaluesum, self.exposure, self.gain, self.interval, csv_name="data.csv")
                # Upload to server
                t_upld = upload_image(url, token_key, location)
                tf = time.time() # stop timer
                t_all = tf - ti
                
                # if you are interested in the runtime, uncomment the line below
                print("\n[Run time] Capture:{:.4f}s ; Text:{:.4f}s; Tuning Brightness:{:.4f}s ; Upload:{:.4f}s".format(t_cap,t_text,t_set,t_upld))
                # cpu and ram usage
                # print("\n[Usage] CPU: {}% ; RAM: {}%".format(psutil.cpu_percent(),psutil.virtual_memory().percent))
                # Auto interval
                self.Auto_interval()
                # Minimize latency
                dt = max(0,round((self.interval-t_all),2)) # ensure +ve sleep time
                print("[Next Capture Time]", datetime.now()+timedelta(seconds=dt))
                print("-------------------------------------------------------------------------------------------------\n")
                time.sleep(dt)
            

    '''Auto Interval'''
    def Auto_interval(self):
        ''' Interval in this version refers to the time gap of the instances of successive snap shots'''
        if self.exposure >= self.max_exposure:   # 30s
            print("\n[Reached max exposure (30s)]")
            self.exposure = self.max_exposure
            self.interval = 0              
        elif self.exposure <= 3000000:  # 3s
            self.interval = 300
            print("\n[Exposure < 3s]")
        else:                           # i.e. 3s < exposure < 30s   
            self.interval = 60
            print("\n[3s < Exposure < 30s]")
        print("  => Interval: {}s ; Exposure: {}s\n".format(self.interval, self.exposure/1000000))
    '''Capture Photo'''
    def capture(self, camera):
        ti = time.time()
        print("[Settings] Exposure: {}s ; Gain: {}.".format(self.exposure/1000000, self.gain))
        camera.set_control_value(asi.ASI_GAIN, self.gain)
        camera.set_control_value(asi.ASI_EXPOSURE, self.exposure) # microseconds
        set_control(camera)
        # datetime
        date = time.strftime("%Y-%m-%d")
        timehk = time.strftime("%H:%M:%S")
        date_time = date + " " + timehk
        path = "photos/" + date.replace('-','') # path named by date
        photo_id = date.replace('-','') + "-" + timehk.replace(':','')
        full_photo_path = path + "/" + photo_id + ".jpg"
        # Create folder named by date of today if it is not existing.
        if not os.path.exists(path): 
            os.makedirs(path)
        print('\n>> Capturing RGB image %s.jpg...' %(photo_id))
        camera.capture(filename=(full_photo_path))
        print('>> Image (%d) saved.\n' %(self.img_counter))
        self.img_counter += 1
        tf = time.time()
        runtime = tf - ti
        return runtime, full_photo_path, date_time, date, timehk, self.exposure, self.gain

    '''Dynamic Setting: prioritize exposure first then gain'''
    def dynamic_setting(self, full_photo_path):
        ti = time.time()
        img = Image.open(full_photo_path)
        pixelvaluesum = sum(ImageStat.Stat(img).sum)
        print("[Pixel] %s \n" %pixelvaluesum)
        if pixelvaluesum > self.MaxBV:
            self.gain = max(1, self.gain-10) # if gain<0 it returns 1
            print("[Bright] New Gain: {} (min=1)".format(self.gain))
            if self.gain == 1: # if gain is minimum we reduce exposure
                factor = round((0.5*(self.MinBV+self.MaxBV)/pixelvaluesum),3)
                # factor = np.exp(-(((pixelvaluesum-self.MinBV)/pixelvaluesum)/0.5)**2)
                self.exposure = int(max(self.min_exposure, round(self.exposure*factor,5))) # returns 100 if exposure < 100
                print("         New Exposure: {}s (min=0.0001s)".format(self.exposure/1000000))
                print("         Factor: {}".format(factor))
        if pixelvaluesum < self.MinBV:
            factor = round((0.5*(self.MinBV+self.MaxBV)/pixelvaluesum),3)
            # factor = np.exp(0.5*(self.MaxBV-pixelvaluesum)/pixelvaluesum)
            self.exposure = int(min(30000000, round(self.exposure*factor,5)))
            print("[Dark] New Exposure: {}s (max=30s)".format(self.exposure/10000000))
            if self.exposure == 30000000:
                self.gain = min(self.max_gain, self.gain + self.gain_step)
                print('       New Gain: {} (max=600)'.format(self.gain))
            print('       Factor: {}'.format(factor))
        tf = time.time()
        runtime = tf - ti
        return runtime, pixelvaluesum


'''Text on image'''
def text(full_photo_path, sqm_value, date, timehk, loc_index, exposure, gain):
    ti = time.time()
    img = Image.open(full_photo_path)
    etime=float(exposure)/1000000
    etime = "<0.01" if etime < 0.01 else "{:.2f}".format(etime)
    exposure_time="曝光 Exposure: " + str(etime) +" 秒second(s)"
    gain_value="增益 Gain: " + str(gain)
    Date = "日期 Date: " + date
    timehk_plus_exposure = ("時間 Time (UTC+8): " + timehk + "+" + str(etime))
    moonphase="月相 Moon Phase: " + str(round(ephem.Moon(datetime.now()).moon_phase, 2)) #get moon phase in 2 digits
    # open an image and get its size
    width, height = img.size
    # Call draw Method to add 2D graphics in an image
    img_draw = ImageDraw.Draw(img)
    # Assign fixed texts to different variables
    location1_text="地點 Location:\n 尖沙咀香港太空館\nHong Kong Space Museum, Tsim Sha Tsui"
    location2_text="地點 Location:\n 西貢天文公園\nAstropark, Sai Kung"
    location3_text="地點 Location:\n 西貢麥理浩夫人度假村\nLady MacLehose Holiday Village, Sai Kung"
    location = [location1_text,location2_text,location3_text]
    loc_position = ((width-1100, height-320), (width-500, height-320), (width-1050, height-320))
    # Custom font style and font size
    Chinese=ImageFont.truetype('source/NotoSansHK-Thin.otf',55)
    Chinese2=ImageFont.truetype('source/NotoSansHK-Thin.otf',60)
    # Add Text to an image at a position
    img_draw.text((50, 50), Date,font=Chinese2)
    img_draw.text((50, 150), timehk_plus_exposure,font=Chinese2)
    img_draw.text((50, 250), moonphase,font=Chinese2)
    img_draw.text((width-900, 50), exposure_time,font=Chinese2)
    img_draw.text((width-900, 150), gain_value,font=Chinese2)
    img_draw.text(loc_position[loc_index], location[loc_index],font=Chinese, align="right")
    # position of four cardinal points
    img_draw.text((70, height/2), "東 East",font=Chinese)
    img_draw.text(((width/2)-100, height-250), "南 South",font=Chinese)
    img_draw.text((width-290, height/2), "西 West",font=Chinese)
    img_draw.text(((width/2)-100, 230), "北 North",font=Chinese)
    # if sqm exists, add to image
    if sqm_value != "NaN" and sqm_value != "00.00":
        sqm_text = "夜空光度數值 SQM: " + str(sqm_value)
    else:
        sqm_text = "夜空光度數值 SQM: N/A"
    img_draw.text((width-900, 250), sqm_text,font=Chinese2)
    # add logo on the image
    img_logo = Image.open('source/SpM_Logo_1000.png')
    img.paste(img_logo,(50, height-300),img_logo)        
    img.save(full_photo_path)    
    loc_name = ["hkspm.jpg", "astropark.jpg", "lmhv.jpg"]
    img.save("source/" + loc_name[loc_index])
    img.close()
    tf = time.time()
    runtime = tf - ti
    return runtime


'''Load ZWO SDK'''
def detect_camera(windows_driver, linux_driver):
    operating_sys = platform.system()
    if operating_sys == 'Windows':
        print('\nOS: Windows')
        asi.init(windows_driver)
    elif operating_sys == 'Linux':
        print('\nOS: Linux')
        asi.init(linux_driver)
    # Get camera information
    num_cameras = asi.get_num_cameras()
    if num_cameras == 0:
        raise ValueError('Camera not found.')
    camera_id = 0  # use first camera from list
    cameras_found = asi.list_cameras()[0]
    print("Camera Model:", cameras_found)
    camera = asi.Camera(camera_id)
    return camera

'''camera control'''
def set_control(camera):
    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD,
                            camera.get_controls()['BandWidth']['MinValue'])
    camera.set_control_value(asi.ASI_WB_B, 99)
    camera.set_control_value(asi.ASI_WB_R, 50)
    camera.set_control_value(asi.ASI_GAMMA, 50)
    camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
    camera.set_control_value(asi.ASI_FLIP, 0)
    camera.set_image_type(asi.ASI_IMG_RGB24) #RAW8=bit; RAW16=16bit; RGB24=color
    camera.disable_dark_subtract()
    camera.stop_video_capture()
    camera.stop_exposure()

'''Detect if sqm is available'''
def detect_sqm(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip,10001))
        s.settimeout(None)
        s.close
        print("SQM: \u2714")
    except(TimeoutError, OSError):
        print("SQM: \u2718")


'''Read SQM value'''
def sqm_reader(ip):
    if datetime.now().hour >= 18 or datetime.now().hour < 7:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect((ip,10001))
            s.settimeout(None)
            s.send('rx'.encode())
            s.close
            data = s.recv(1024).decode("utf-8")
            sqm_value = data.replace(" ", "").replace("m", "").split(',')[1]
            print("[SQM] {} \n".format(sqm_value))
        except Exception as e:
            print("[SQM Error] {} \n".format(repr(e)))
            sqm_value = "NaN"
    else:
        sqm_value = "NaN"
        print("[SQM] Timeout from 7am-6pm\n")
    return sqm_value
    

'''Save data'''
def save_csv(*argv, csv_name:str): # you can save arbitrary number of data
    data = list(argv)
    with open(csv_name, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

'''Upload to web server'''
def upload_image(upload_url, auth_token_key, location_name):
    ti = time.time()
    try:
        image_path = "source/" + location_name + ".jpg"
        # Disable 'requests' warnings
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        # Request to upload image
        with open(image_path, "rb") as image_file:
            response = requests.post(upload_url, headers={'Authorization': 'Bearer ' + auth_token_key}, data={"location": location_name}, files={"image": image_file}, timeout=5, verify=False)
        # Response status from server
        if response.status_code == 200:
            print("[File upload] Successful")
        elif response.status_code == 401:
            print("[File upload] Unauthorized, please check the auth_token_key")
        else:
            print("[File upload] Failed")
    except Exception as e:
        print("[File Upload] Unknown Error", e)
    tf = time.time()
    runtime = tf -ti
    return runtime


if __name__ == "__main__":
    try:
        app = App()
    except Exception as e:
        traceback.print_exc()
        with open("errorLog.txt", "a") as text_file:
            text_file.write("\n")
            text_file.write(str(datetime.now()))
            text_file.write("\n")
            text_file.write(traceback.format_exc())
        print('\n<< Programme restarts in 10 sec >>\n')
        sys.stdout.flush() # flush the buffers
        time.sleep(10)
        os.execv(sys.executable, ['python'] + sys.argv)