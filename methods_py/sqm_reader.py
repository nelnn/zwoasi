import socket
import csv

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

def save_csv(location, date_time, sqm_magnitude, *argv):
    data = [location, date_time, sqm_magnitude]
    data.extend(list(argv))
    with open('data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

