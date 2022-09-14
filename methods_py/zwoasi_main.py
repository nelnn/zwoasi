import tkinter as tk
from tkinter import ttk
from device_availability import detect_camera, detect_sqm
from camera_func import fixed_setting, capture, dynamic_setting, Auto_interval
from add_text import text
from sqm_reader import sqm_reader, save_csv
from upload_image import upload_image
import timeit
from tabulate import tabulate

'''The paths for resouces are updated, so you can just run it here without moving the scripts to
the parent directory. The main difference of this script is that we break down the whole programmme
into parts so the main scipt does not look overwhelmed. Note this is not the lastest version'''

class App(tk.Tk):
    # initial values
    img_counter = 0
    def __init__(self):
        super().__init__()
        self.run = True
        # configure the root window
        self.title("All Sky Camera")
        self.geometry("320x650")
        # self.minsize(290, 520)
        # self.maxsize(290, 520)

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
        self.e2 = self.Entry(5,2,10,pady_entry,1000000)
        # Gain
        self.labGain = self.Label("Gain (Min=1):", font_10, 6,2)
        self.e3 = self.Entry(7,2,10,pady_entry,1)
        # Max BV
        self.labMaxbv = self.Label("Maximum Brightness Value:\n Suggested for IMX533: 1,600,000,000", font_10, 8, 2)
        self.e4 = self.Entry(9,2,10,pady_entry,1600000000)
        # Min BV
        self.labMinbv = self.Label("Minimum Brightness Value:\n Suggested for IMX533: 1,500,000,000", font_10, 10, 2)
        self.e5 = self.Entry(11,2,10,pady_entry,1500000000)

        '''Buttons'''
        # Start
        self.button1 = tk.Button(text='Start', command=self.on_start, bg='brown', fg='white', font=font_09)
        self.button1.grid(row=17, column=2, sticky=tk.W, padx=80, pady=10)
        # Stop
        self.button2 = tk.Button(text='Stop', command=self.on_stop, bg='brown', fg='white', font=font_09)
        self.button2.grid(row=17, column=2, sticky=tk.E, padx=80, pady=10)

        '''Check Box - self.Checkbox(text:str, onvalue, offvaule, row, column, padx=1, pady=1, command=None, sticky=None)'''
        # Auto interval
        self.tick_int, self.cb_int = self.Checkbox("auto-interval",1,0,2,2, pady=(1,10), sticky=tk.E)
        # Upload online
        self.tick_upload, self.cb_online = self.Checkbox("upload online",1,0,13,2, 40, sticky=tk.W)
        # Disable auto setting
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
    # calibration

    '''The main function'''
    def start_programme(self):
        if self.run:
            ti = timeit.default_timer() # start timer
            # location
            loc_index = self.locOptions.index(self.locVar.get())
            # Take photo
            exposure, interval, gain, self.img_counter, MaxBV, MinBV, path, photo_id, date_time, date, timehk = capture(
                camera, self.e1,self.e2,self.e3,self.e4,self.e5,self.img_counter)
            # Measure SQM value
            sqm_magnitude = sqm_reader(sqm_connection, sqm_ip)
            # Add text & Dynamic setting
            if not self.tick_setting.get():
                # add text to image
                imgopen = text(exposure, gain, sqm_magnitude, path, photo_id, date, timehk, loc_index)
                # Evaluate camera settings based on exposure and gain
                pixelvaluesum = dynamic_setting(self.e2, self.e3,
                    exposure, gain, MaxBV, MinBV, imgopen)
            # Fixed setting
            else:
                pixelvaluesum = fixed_setting(path, photo_id)
            # Save data to csv
            save_csv(self.locVar.get(), date_time, sqm_magnitude, pixelvaluesum, exposure, gain, interval)
            # Upload to server
            if self.tick_upload.get():
                loc_name = ["source/hkspm.jpg", "source/astropark.jpg", "source/lmhv.jpg"]
                loc = ["hkspm", "astropark", "lmhv"]
                upload_image(url, token_key, loc[loc_index], loc_name[loc_index])            
            tf = timeit.default_timer() # stop timer
            # Auto interval
            if self.tick_int.get():
                interval = Auto_interval(self.e1, self.e2)
            
            # Minimize latency
            if exposure/1000000 > interval:
                self.after(1000, self.start_programme)
            else:
                dt = int((interval-(tf-ti))*1000)
                self.after(dt, self.start_programme)


if __name__ == "__main__":
    camera, operating_system, name = detect_camera() # camera, operating system, model name
    '''Check if you enter the correct ip address!!!'''
    sqm_ip = '169.254.184.252' # Either 169.254.184.252 / 169.254.224.228 / 
    msg, sqm_connection = detect_sqm(sqm_ip)
    '''upload to server'''
    url = "https://210.3.170.231/allsky/upload"    # upload url path (please edit IP address or domain name)
    token_key = "qC6a_x8GuoqmFpiW8i6duDsFpsqNqluYbb1DGY1u4yE"    # for server authentication
    device = [["OS", operating_system], ["Camera", name], ["SQM", msg]]
    print(tabulate(device, tablefmt="pretty"))
    app = App()
    app.mainloop()
