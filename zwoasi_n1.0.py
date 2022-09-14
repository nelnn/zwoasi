import tkinter as tk
from tkinter import ttk
import timeit
from PIL import Image
import os
import sys
import zwoasi as asi
import platform
import socket
from tabulate import tabulate
import time
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageStat
from datetime import datetime
import ephem
import csv
import requests

'''Tkinter Layout'''
class App(tk.Tk):
    # initial values
    img_counter = 0
    MaxBV = 1600000000
    MinBV = 1500000000
    gain = 1
    exposure = 1000000
    interval = 1
    run = True
    def __init__(self):
        super().__init__()
        # configure the root window
        self.title("All Sky Camera")
        self.geometry("320x650")
        # fonts
        font_14 = ("helvetica", 14); font_10 = ("helvetica", 10); font_09 = ("helvetica", 9, "bold")
        # padding
        pady_entry = (0, 10)

        '''Title - self.Label(self, text:str, font:tuple, row:int, column:int, padx:int=1, pady:int=1, sticky=None)'''
        # All Sky Camera Panel
        self.labTitle = self.Label("All Sky Camera Panel", font_14, 0, 2, 50, 20)
        
        '''Entry Box - self.Entry(self, row, column, padx, pady, val='')'''
        # Interval before next image (second)
        self.labInterval = self.Label("Interval before next image (s):", font_10, 1, 2)
        self.e1 = self.Entry(2, 2, 10, pady_entry)
        # Exposure
        self.labExpo = self.Label("Exposure (microsecond): \n 1,000 = 1 millisecond; 1,000,000 = 1 second", font_10, 4, 2)
        self.e2 = self.Entry(5,2,10,pady_entry,self.exposure)
        # Gain
        self.labGain = self.Label("Gain (Min=1):", font_10, 6,2)
        self.e3 = self.Entry(7,2,10,pady_entry,self.gain)
        # Max BV
        self.labMaxbv = self.Label("Maximum Brightness Value:\n Suggested for IMX533: 1,600,000,000", font_10, 8, 2)
        self.e4 = self.Entry(9,2,10,pady_entry,self.MaxBV)
        # Min BV
        self.labMinbv = self.Label("Minimum Brightness Value:\n Suggested for IMX533: 1,500,000,000", font_10, 10, 2)
        self.e5 = self.Entry(11,2,10,pady_entry,self.MinBV)

        '''Buttons'''
        # Start
        self.button1 = tk.Button(text='Start', command=self.on_start, bg='brown', fg='white', font=font_09)
        self.button1.grid(row=17, column=2, sticky=tk.W, padx=80, pady=10)
        # Stop
        self.button2 = tk.Button(text='Stop', command=self.on_stop, bg='brown', fg='white', font=font_09)
        self.button2.grid(row=17, column=2, sticky=tk.E, padx=80, pady=10)

        '''Check Box - self.Checkbox(text:str, onvalue, offvaule, row, column, padx=1, pady=1, command=None, sticky=None)'''
        # Auto interval
        self.tick_int, self.cb_int = self.Checkbox("auto-interval",1,0,2,2, pady=(1,10), sticky=tk.E, command=self.Auto_interval)
        # Upload online
        self.tick_upload, self.cb_online = self.Checkbox("upload online",1,0,13,2, 40, sticky=tk.W)
        # # fixed mode
        self.tick_setting, self.cb_setting = self.Checkbox("fixed mode", 1,0,13,2, 40, sticky=tk.E)

        '''Drop Down List'''
        self.labLoc = self.Label("Location: ", font_10,15,2,50,10,sticky=tk.W)
        self.locOptions = ["hkspm", "astropark", "lmhv"]
        self.locVar = tk.StringVar()
        self.w = ttk.OptionMenu(self, self.locVar,self.locOptions[0],*self.locOptions)
        self.w.grid(row= 15, column=2, padx=70, pady=10, sticky=tk.E)
    
    '''Define Label, Entry, Checkbox methods to reduce redundancy'''
    def Label(self, text:str, font:tuple, row:int, column:int, padx=1, pady=1, sticky=None):
        label = tk.Label(self, text=text)
        label.config(font=font)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
        return label
    def Entry(self, row, column, padx, pady, val=''):
        entry = tk.Entry(self, width=15)
        entry.grid(row=row, column=column, padx=padx, pady=pady)
        entry.insert(-1,val)
        return entry
    def Checkbox(self, text:str, onvalue, offvaule, row, column, padx:int=1, pady:int=1, command=None, sticky=None):
        intvar = tk.IntVar()
        checkbox = tk.Checkbutton(self,text=text,command=command, variable=intvar,onvalue=onvalue,offvalue=offvaule)
        checkbox.grid(row=row,column=column,padx=padx,pady=pady,sticky=sticky)
        return intvar, checkbox
    
    '''Button functions'''
    # start
    def on_start(self):
        self.run = True
        self.start_programme()
    # stop    
    def on_stop(self):
        self.run = False
        print("\n-----Programme Paused-----\n")

    '''The main function'''
    def start_programme(self):
        if self.run and self.tick_setting.get()==0:
            ti = timeit.default_timer() # start timer
            # location
            loc_index = self.locOptions.index(self.locVar.get())
            # Take photo
            full_photo_path, date_time, date, timehk = self.capture(camera)
            # Measure SQM value
            sqm_magnitude = sqm_reader(sqm_connection, sqm_ip)
            # Evaluate camera settings based on exposure and gain
            pixelvaluesum = self.dynamic_setting(full_photo_path)
            # add text to image
            self.text(full_photo_path, sqm_magnitude, date, timehk, loc_index)
            # Save data to csv
            save_csv(self.locVar.get(), date_time, sqm_magnitude, pixelvaluesum, self.exposure, self.gain, self.interval, csv_name="data_n10.csv")
            # Upload to server
            if self.tick_upload.get():
                loc_name = ["hkspm.jpg", "astropark.jpg", "lmhv.jpg"]
                loc = ["hkspm", "astropark", "lmhv"]
                upload_image(url, token_key, loc[loc_index], loc_name[loc_index])           
            tf = timeit.default_timer() # stop timer
            # Auto interval
            self.Auto_interval()
            # Minimize latency
            if self.exposure/1000000 > self.interval:
                self.after(5000, self.start_programme)
            else:
                dt = int((self.interval-(tf-ti))*1000)
                self.after(dt, self.start_programme)
        elif self.run and self.tick_setting: # fixed mode - no text and upload
            full_photo_path, date_time, date, timehk = self.capture(camera)
            pixelvaluesum = self.fixed_setting(full_photo_path)
            save_csv(date_time,self.exposure,self.gain,pixelvaluesum, csv_name="fixed_settings.csv")
            self.after(self.interval*1000, self.start_programme)
    '''Capture Photo'''
    def capture(self, camera): 
        self.exposure = try_except(self.e2, 3000) # defalut exposure = 3000ms
        self.interval = try_except(self.e1, 10) # defalut interval = 10s
        self.gain = try_except(self.e3, 1) # defalut gain = 1
        self.MaxBV = try_except(self.e4, 1600000000) # default MaxBV = 1600000000
        self.MinBV = try_except(self.e5, 1500000000) # default MinBV = 1500000000
        settings = [["Interval (s)", self.interval], ["Exposure(s)", self.exposure/1000000], ["Gain", self.gain]]
        print("\n------------------------------------------------------------------------------------------------------------\n")
        print(tabulate(settings, headers=["Settings", "Value"]))
        camera.set_control_value(asi.ASI_GAIN, int(self.gain))
        camera.set_control_value(asi.ASI_EXPOSURE, int(self.exposure)) # microseconds
        set_control(camera)
        camera.stop_video_capture()
        camera.stop_exposure()
        # datetime
        date = time.strftime("%Y-%m-%d")
        date1 = date.replace('-','')
        timehk = time.strftime("%H:%M:%S")
        timehk1 = timehk.replace(':','')
        date_time = date + " " + timehk
        path = "photos/" + date1 # path named by date
        photo_id = date1 + "-" + timehk1
        full_photo_path = path + "/" + photo_id + ".jpg"
        # Create folder named by date of today if it is not existing.
        if not os.path.exists(path): 
            os.makedirs(path)
        print('\nCapturing a RGB image %s.jpg...\n' %(photo_id))
        camera.capture(filename=(full_photo_path))
        self.img_counter += 1
        print('Image (%d) saved.\n' %(self.img_counter))
        return full_photo_path, date_time, date, timehk

    '''Dynamic Setting: prioritize exposure first then gain'''
    def dynamic_setting(self, full_photo_path):
        img = Image.open(full_photo_path)
        pixelvaluesum = sum(ImageStat.Stat(img).sum)
        img.close()
        print("Total pixel value sum: "+ str(pixelvaluesum) + "\n")
        minbv = int(self.e5.get())
        maxbv = int(self.e4.get())
        avgbv = 0.5*(maxbv+minbv)
        if pixelvaluesum > maxbv:
            if int(self.gain) < 11:
                self.gain = 1
                print("Gain approaches to minimum, set to 1")
                reduction_factor=round((avgbv/pixelvaluesum),3)
                new_exposure=int(float(self.exposure)*reduction_factor)

                if new_exposure <= 100:
                    self.exposure = 100
                    reduction_factor = 1
                    print("Exposure reaches minimun  at 100 microsecond, reduction_factor reset to 1.\n")
                else:
                    self.exposure = round(new_exposure,5)
                    print("The image is too bright. Exposure will be reduced to " + str(new_exposure/1000000)+ " second(s). Factor: " + str(reduction_factor) + "\n")
            else:
                self.gain = int(self.gain) - 10
                print("The image is too bright. GAIN will be reduced by 10\n")
            
        if pixelvaluesum < minbv:
            reduction_factor = round((avgbv/pixelvaluesum),3)
            new_exposure = int(float(self.exposure)*reduction_factor)
            if new_exposure > 30000000:
                self.exposure = 30000000
                reduction_factor = 1
                if self.gain < 600:
                    self.gain = int(self.gain) + 10
                    print("Exposure reaches maximum(30s), Gain increased by 10, reduction_factor reset to 1.\n")
                else:
                    self.gain = 600
                    print("Gain approaches to maximum, set to 600\n")
            else:
                self.exposure = new_exposure
                print("The image is too dark. Exposure will be increased to " + str(new_exposure/1000000)+ "second(s). Factor:" + str(reduction_factor)+"\n")
        self.e2.delete(0,tk.END)
        self.e2.insert(-1,self.exposure)
        self.e3.delete(0,tk.END)
        self.e3.insert(-1,self.gain)
        return pixelvaluesum

    '''Fixed Setting'''
    def fixed_setting(self, photo_path):
        img = Image.open(photo_path)
        pixelvaluesum = sum(ImageStat.Stat(img).sum)
        return pixelvaluesum

    '''Text on image'''
    def text(self, full_photo_path, sqm_magnitude, date, timehk, loc_index):
        img = Image.open(full_photo_path)
        etime=float(self.exposure)/1000000
        if etime<0.01:
            etime="<0.01"
        else:
            etime="{:.2f}".format(etime)
        exposure_time="曝光 Exposure: " + str(etime) +" 秒second(s)"
        gain_value="增益 Gain: " + str(self.gain)
        Date = "日期 Date: " + date
        timehk_plus_exposure = ("時間 Time (UTC+8): " + timehk + "+" + str(etime))
        moonphase="月相 Moon Phase: " + str(round(ephem.Moon(datetime.now()).moon_phase, 2)) #get moon phase in 2 digits
        # open an image and get its size
        width, height = img.size
        # Call draw Method to add 2D graphics in an image
        img_draw = ImageDraw.Draw(img)
        # Assign fixed texts to different variables
        location1_text="地點 Location:\n 尖沙咀香港太空館\nHong Kong Space Museum, Tsim Sha Tsui "
        location2_text="地點 Location:\n 西貢天文公園\nAstropark, Sai Kung"
        location3_text="地點 Location:\n 西貢麥理浩夫人度假村\nLady MacLehose Holiday Village, Sai Kung"
        location = [location1_text,location2_text,location3_text]
        loc_position = ((width-1100, height-320), (width-500, height-320), (width-1050, height-320))
        cardinal_point_E="東 East"
        cardinal_point_S="南 South"
        cardinal_point_W="西 West"
        cardinal_point_N="北 North"
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
        img_draw.text((70, height/2), cardinal_point_E,font=Chinese)
        img_draw.text(((width/2)-100, height-250), cardinal_point_S,font=Chinese)
        img_draw.text((width-290, height/2), cardinal_point_W,font=Chinese)
        img_draw.text(((width/2)-100, 230), cardinal_point_N,font=Chinese)
        # if sqm exists, add to image & save values to csv
        if sqm_magnitude != "Nan":
            sqm_value = "SQM: " + str(sqm_magnitude)
            img_draw.text((width-900, 250), sqm_value,font=Chinese2)
        # add logo on the image
        img_logo = Image.open('source/SpM_Logo_1000.png')
        img.paste(img_logo,(50, height-300),img_logo)        
        img.save(full_photo_path)    
        loc_name = ["hkspm.jpg", "astropark.jpg", "lmhv.jpg"]
        img.save(loc_name[loc_index])
        img.close()

    '''Auto Interval'''
    def Auto_interval(self):
        if self.tick_int.get():
            self.exposure = int(self.e2.get())
            if self.exposure >= 30000000:
                print("Reached max exposure (30s)")
                self.exposure = 30000000
                self.interval = 0
                self.e1.delete(0,tk.END)
                self.e2.delete(0,tk.END)
                self.e1.insert(-1,self.interval)
                self.e2.insert(-1,self.exposure)               
            elif self.exposure <= 3000000:
                # when exprouse is smaller than 3 seconds, the interval = 5 minutes
                # do not need that many images in day time
                self.interval = 300
                self.e1.delete(0,tk.END)
                self.e1.insert(-1,self.interval)
                print("\nExposure < 3s")
            else:
                # if 3s < exposure < 30s, the interval = 60 - exposure     
                self.interval = 60
                self.e1.delete(0,tk.END)
                self.e1.insert(-1,self.interval)
                print("\n3s < Exposure < 30s")
            print("New invterval = "+ str(self.interval) + "s; New exposure = " + str(int(self.exposure)/1000000)+ "s")
        else:
            self.e1.delete(0,tk.END)
            self.e1.insert(-1,self.interval)


'''Load ZWO SDK'''
def detect_camera():
    operating_sys = platform.system()
    if operating_sys == 'Windows':
        print('\nOS: Windows')
        asi.init("ASI_Windows/lib/x64/ASICamera2.dll")
    elif operating_sys == 'Linux':
        print('\nOS: Linux')
        asi.init('ASI_linux/lib/armv7/libASICamera2.so.1.25')
    # Get camera information
    num_cameras = asi.get_num_cameras()
    if num_cameras == 0:
        print('No camera found')
        sys.exit(0)
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

'''Detect if sqm is available'''
def detect_sqm(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip,10001))
        s.settimeout(None)
        s.close
        print("SQM: \u2714")
        print("\nStarting up...\n")
        return True
    except(TimeoutError, OSError):
        print("SQM: \u2718")
        print("\nStarting up...\n")
        return False

'''try to get entry values, if invalid set to default vaules'''
def try_except(entry, default_value):
    try:
        value = int(entry.get())
    except ValueError:
        value = default_value
        entry.delete(0,tk.END)
        entry.insert(-1,value)
    return value

'''Read SQM value'''
def sqm_reader(sqm_connection, ip):
    if sqm_connection == True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,10001))
        s.send('rx'.encode())
        data = s.recv(1024).decode("utf-8")
        sqm_magnitude =data.replace(" ", "").replace("m", "").split(',')[1]
        s.close
        print('SQM: ', sqm_magnitude)
        return sqm_magnitude
    else:
        return "Nan"

'''Save data'''
def save_csv(*argv, csv_name:str): # you can save arbitrary number of data
    data = list(argv)
    with open(csv_name, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

'''Upload to web server'''
def upload_image(upload_url:str, auth_token_key:str, location_name: str, image_path: str):
    try:
        # Disable 'requests' warnings
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        # Request to upload image
        with open(image_path, "rb") as image_file:
            response = requests.post(upload_url, headers={'Authorization': 'Bearer ' + auth_token_key}, data={"location": location_name}, files={"image": image_file}, timeout=5, verify=False)
        # Response status from server
        if response.status_code == 200:
            print("[File upload] Uploaded Successful")
        elif response.status_code == 401:
            print("[File upload] Unauthorized, please check the auth_token_key")
        else:
            print("[File upload] Failed")
      
    except requests.Timeout:
        print("[File Upload] Timeout")
    except requests.ConnectionError:
        print("[File Upload] Connection Error")
    except Exception as e:
        print("[File Upload] Unknown Error", e)








if __name__ == "__main__":
    camera = detect_camera() # camera

    '''Check if you enter the correct ip address!!!'''
    sqm_ip = '169.254.184.252' # Either 169.254.184.252 / 169.254.224.228 / 
    sqm_connection = detect_sqm(sqm_ip)

    '''upload to server'''
    url = "https://210.3.170.231/allsky/upload"    # upload url path (please edit IP address or domain name)
    token_key = "qC6a_x8GuoqmFpiW8i6duDsFpsqNqluYbb1DGY1u4yE"    # for server authentication

    app = App()
    app.mainloop()