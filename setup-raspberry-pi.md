## 1. OS Installation
If you want to install oaCapture, you'll need to install **Raspberry Pi OS (Legacy)**.

## 2. Set Python3 as default in Raspberry pi (must do)
```console
$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
```
## 3. oaCapture 
Step 1:

Go to their [website](https://www.openastroproject.org/downloads/) and copy the address for [oacapture_1.8.0-1_armhf.deb](http://www.openastroproject.org/wp-content/uploads/2020/12/raspbian-10/oacapture_1.8.0-1_armhf.deb) under **32-bit Raspain 10**. Run the following in the terminal (assuming the url is still valid, you need to check yourself):
```console
$ wget http://www.openastroproject.org/wp-content/uploads/2020/12/raspbian-10/oacapture_1.8.0-1_armhf.deb
```
```console
$ sudo dpkg -i oacapture_1.8.0-1_armhf.deb
```

Step 2: 

Install the missing packages:
```console
$ sudo apt install libcfitsio7 libqt4-network libqtcore4 libqtgui4 libraw19
```
Fix broken install:
```console
$ sudo apt --fix-broken install
```
oaCapture should be installed by now under *education*. Repeat the same steps to install the asi camera driver [libasicamera_1.16-0_armhf.deb](http://www.openastroproject.org/wp-content/uploads/2020/12/raspbian-10/libasicamera_1.16-0_armhf.deb). Reconnect the camera if you pluged it in.


## 4. To initiate asi camera in python..
Go to the driver directory (It might be different for you)
```console
$ cd /home/pi/Desktop/ZWO/ASI_linux/lib
```
You should see the asi.rule file in the directory. Now run
```console
$ sudo install asi.rules /lib/udev/rules.d
```
or
```console
$ sudo install asi.rules /etc/udev/rules.d
```
and reconnect camera, then the camera can be opened without root.

Run 
```console
$ cat /sys/module/usbcore/parameters/usbfs_memory_mb
```
 to make sure the result is 200.

 ## 5. VScode (optional)
```console
$ sudo apt update
$ sudo apt install code
```