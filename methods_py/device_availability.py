
import zwoasi as asi
import socket
import platform
from pathlib import Path
'''Load ZWO SDK'''
def detect_camera():
    os = platform.system()
    if os == 'Windows':
        asi.init(str(Path("device_availiability.py").parent.absolute()/"ASI_Windows/lib/x64/ASICamera2.dll"))
    elif os == 'Linux':
        #print('OS: Linux')
        asi.init(str(Path("device_availiability.py").parent.absolute()/"ASI_linux/lib/armv7/libASICamera2.so.1.25"))
    # Get camera information
    num_cameras = asi.get_num_cameras()
    if num_cameras == 0:
        raise ValueError('No cameras found')
    camera_id = 0  # use first camera from list
    cameras_found = asi.list_cameras()[0]
    #print("Camera Model:", cameras_found[0])
    camera = asi.Camera(camera_id)
    camera_info = camera.get_camera_property()
    controls = camera.get_controls()
    # Use minimum USB bandwidth permitted
    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD,
                            camera.get_controls()['BandWidth']['MinValue'])
    camera.set_control_value(asi.ASI_WB_B, 99)
    camera.set_control_value(asi.ASI_WB_R, 50)
    camera.set_control_value(asi.ASI_GAMMA, 50)
    camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
    camera.set_control_value(asi.ASI_FLIP, 0)
    camera.set_image_type(asi.ASI_IMG_RGB24) #RAW8=bit; RAW16=16bit; RGB24=color

    # Set some sensible defaults. They will need adjusting depending upon
    # the sensitivity, lens and lighting conditions used.
    camera.disable_dark_subtract()

    # Get camera information
    num_cameras = asi.get_num_cameras()
    if num_cameras == 0:
        raise ValueError('No cameras found')
    else:
        return camera, os, cameras_found


'''Detect if sqm is available'''
def detect_sqm(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip,10001))
        s.settimeout(None)
        s.close
        #print("\nSQM connected")
        #print("\nStarting up...\n")
        msg = "\u2714"
        return msg, True
    except(TimeoutError, OSError):
        msg = "\u2718"
        return msg, False

