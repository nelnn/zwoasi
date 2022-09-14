import socket
import timeit

ip = "192.168.8.148"
#ip = '169.254.247.96'
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect((ip,10001))
    s.settimeout(None)
    s.send('rx'.encode())
    data = s.recv(1024).decode("utf-8")
    sqm_value =data.replace(" ", "").replace("m", "").split(',')[1]
    s.close()
    print("SQM value:", sqm_value)
    print(data)
except Exception as e:
    print("[Error] ", e)
    print("SQM not found")