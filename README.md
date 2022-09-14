# All Sky Camera with Sky Quality Meter Application

## zwoasi_n1.1.py - latest update
This version omits the graphic user interface (gui). Simply click and run. Make sure the hardware is set up properly. You can change the default settings and ip address under ***def \__init__(self)***:
```python
def __init__(self):
    # settings
    sqm_ip = "169.254.247.96" # "192.168.8.148" 
    url = "https://3.39.172.216/allsky/upload"    # upload url path (please edit IP address or domain name)
    token_key = "qC6a_x8GuoqmFpiW8i6duDsFpsqNqluYbb1DGY1u4yE"    # for server authentication
    location = "hkspm" # hkspm / astropark / lmhv
    windows_driver = "ASI_Windows/lib/x64/ASICamera2.dll"
    linux_driver = 'ASI_linux/lib/armv7/libASICamera2.so.1.25'
    MaxBV = 1700000000
    MinBV = 1500000000
    # initial values
    self.gain = 1
    self.max_gain = 600 # max gain
    self.gain_step = 10 # gain increment/decrement
    self.exposure = 100 # microsecound
    self.min_exposure = 10 # min exposure
    self.img_counter = 1
```
### script work flow:
1. keep taking photos to make sure the image is within the pixel range if the exposure is less than 10 seconds.*
2. if the image is within the pixel range, then:
    - measure sqm value
    - add text and logo to image
    - save data to csv
    - upload image to server

3. wait for the next shot. Repeat step 1.
4. If the programme encounters an unexpected error, it will retart in 5-10 sec.*

\*only available in this version 
## zwoasi_n1.0.py - tkinter version
This script has a graphic user interface. The code is not as updated as zwoasi_n1.1.py but still functions properly. All the functions are inside that single script.

There is a *fixed mode* which zwoasi_n1.1py does not have. It asks for the user inputs, i.e. exposure, gain, interval, etc. and takes photos with the same settings. The images won't be decorated and uploaded - just a plain image. The pixel value for each is saved to a csv file (default name is fixed_settings.csv)

## methods_py - tkinter version 2
There are a few py scripts in the folder, where ***zwo_main.py*** is the one to run. The other scripts categarise the features of the project. Original thought was to split the project into parts so the main script is not clutered with bunch of methods and make it easy for future updates and additional implementation. However, this version seems not to be too stable with Raspberry pi (it runs perfectly on Windows), producing ZWO_Capture error or ZWO_General error from time to time with unknown reason.

You can just run ***zwo_main.py*** inside the folder. The camera driver path and other paths have been taken care of.

## if you want to run the old scripts (v11 or older)...
[update] zwoasi_test_v10.py and zwoasi_test_v11.py can now be run directly inside the zwoasi_old_scripts folder.
- move the script to the parent directory, a.k.a the ZWO folder (however, you can run the zwoasi_main.py in the methods_py folder without dragging it out because I have changed the path)
- please change the paths for the following:
    - camera driver. now in ASI_linux / ASI_Windows.
    - the font package and the hkspm logo has been moved to the source folder.
- Some features (e.g. sqm, save to csv) may need to be uncommented for using.


## analysis_py - supported functions
- **hko_visibility_api.py** - return the average visibilty of 4 stations in the last 10 minutes. Data collected by the Hong Kong Observatory.
- **img_to_vid.py** - convert a folder of images to a mp4 video.
- **plot_sqm_value.py** - plot sqm values in data.csv

## Remarks
- You may want to check out the updated version of the camera driver once in a while. [link](https://astronomy-imaging-camera.com/software-drivers) - under the developers tab.
- Check out [setup-raspberry-pi.md](setup-raspberry-pi.md) if you are setting up your pi for this project. It contains instruction on how to install oaCapture, set Python 3 as the default interpreter, and initiate the asi driver in python.
- Check out [git_tutorial.md](git_tutorial.md) if you need it.