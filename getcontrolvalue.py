import zwoasi as asi
import platform
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
        print("Camera not found.")
        raise ImportError
    camera_id = 0  # use first camera from list
    cameras_found = asi.list_cameras()[0]
    print("Camera Model:", cameras_found)
    camera = asi.Camera(camera_id)
    return camera

cam = detect_camera("ASI_Windows/lib/x64/ASICamera2.dll",'ASI_linux/lib/armv7/libASICamera2.so.1.25')
# cam.set_control_value(asi.ASI_EXPOSURE, 1)
# print(cam.get_control_value(asi.ASI_EXPOSURE))
# print(cam.get_control_value(asi.ASI_TEMPERATURE))
# print(cam.get_controls())
cam.set_control_value(asi.ASI_FAN_ON,1)
print(cam.get_control_value(asi.ASI_FAN_ON))