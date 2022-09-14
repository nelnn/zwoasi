import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import ephem
from pathlib import Path

def text(exposure, gain, sqm_magnitude, path, photo_id, date, timehk, loc_index):
    imgopen = Image.open(os.path.join(path,str(photo_id)+".jpg"))
    #get exposure, gain from ZWOASI.py
    etime=float(exposure)/1000000 # etime is given by ZWOASI programme
    if etime<0.01:
        etime="<0.01"
    else:
        etime="{:.2f}".format(etime)
    exposure_time="曝光 Exposure: " + str(etime) +" 秒second(s)"
    gain_value="增益 Gain: " + str(gain)
    Date = "日期 Date: " + date
    timehk_plus_exposure = ("時間 Time (UTC+8): " + timehk + "+" + str(etime))
    moonphase="月相 Moon Phase: " + str(round(ephem.Moon(datetime.now()).moon_phase, 2)) #get moon phase in 2 digits


    # open an image and get its size
    width, height = imgopen.size

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(imgopen)

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
    Chinese=ImageFont.truetype(str(Path("device_availiability.py").parent.absolute()/'source/NotoSansHK-Thin.otf'),55)
    Chinese2=ImageFont.truetype(str(Path("device_availiability.py").parent.absolute()/'source/NotoSansHK-Thin.otf'),60)

    # Add Text to an image at a position
    I1.text((50, 50), Date,font=Chinese2)
    I1.text((50, 150), timehk_plus_exposure,font=Chinese2)
    I1.text((50, 250), moonphase,font=Chinese2)
    I1.text((width-900, 50), exposure_time,font=Chinese2)
    I1.text((width-900, 150), gain_value,font=Chinese2)
    I1.text(loc_position[loc_index], location[loc_index],font=Chinese, align="right")

    # position of four cardinal points
    I1.text((70, height/2), cardinal_point_E,font=Chinese)
    I1.text(((width/2)-100, height-250), cardinal_point_S,font=Chinese)
    I1.text((width-290, height/2), cardinal_point_W,font=Chinese)
    I1.text(((width/2)-100, 230), cardinal_point_N,font=Chinese)

    # if sqm exists, add to image & save values to csv
    if sqm_magnitude != "Nan":
        sqm_value = "SQM: " + str(sqm_magnitude)
        I1.text((width-900, 250), sqm_value,font=Chinese2)


    # add logo on the image
    I2 = Image.open(str(Path("device_availiability.py").parent.absolute()/'source/SpM_Logo_1000.png'))
    imgopen.paste(I2,(50, height-300),I2)

    ''' Uncomment below to save the original images'''
    #path_e = path + "e" # e stands for edited
    # if not os.path.exists(path_m):
    #     os.mkdir(path_m)
    #imgopen.save(os.path.join(path_e,str(photo_id)+".jpg"))
    
    imgopen.save(os.path.join(path,str(photo_id)+".jpg")) 
    
    loc_name = ["hkspm.jpg", "astropark.jpg", "lmhv.jpg"]
    imgopen.save("source/"+loc_name[loc_index])
    return imgopen