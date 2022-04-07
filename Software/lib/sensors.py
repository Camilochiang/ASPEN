#!/usr/bin/python3
# The main goal of this script is to allow comunication with the different sensors
# ---------- Libraries --------------
#from smbus2 import SMBus
import subprocess
import requests
import time
import datetime
import os
import pexpect
import Jetson.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# ---------- Altum-----------------------
class altum_camera():
    def __init__(self, device, address, path):
        self.device = device
        self.address = address
        self.dir_output = path

    def is_alive(self):
        PARAMS = 'status'
        response = requests.get(self.address+'/'+PARAMS)
        try:
            if response.json()['dls_status']=='Ok':
                return True
            else:
                return False
        except:
            return False
        
    def detect_pannel(self):
        #Detect QR pannel
        PARAMS = 'capture'+'?'+'block=true'+'&'+'detect_panel=true'
        response = requests.get(self.address + '/'+ PARAMS)
        PARAMS = 'capture/' + response.json()['id']
        
        a = 0
        while a <20:
            a += 1
            response = requests.get(self.address+'/'+PARAMS)
            if response.json()['status'] == 'pending':
                time.sleep(1)
                status = False
            else:
                status = True
                print('ALTUM : Pannel detected')
                break
        
        return status

    def abort_detect_pannel(self):
        #Abort the pannel detection
        PARAMS = 'detect_panel' + '?' + 'block=true' + '&' + 'abort_detect_panel=true'
        response = requests.get(self.address+'/'+PARAMS)
        PARAMS = 'capture/' + response.json()['id']

    def capture_single(self):
        #Take a single picture without saving any time reference
        PARAMS = 'capture' + '?' + 'block=true'
        response = requests.get(self.address + '/' + PARAMS)
        PARAMS = 'capture/' + response.json()['id']
        
        while True:
            response = requests.get(self.address+'/'+PARAMS)
            if response.json()['status'] == 'pending':
                time.sleep(1)
            else:
                break

    def capture(self, status, interval):
        # Take a series of pictures 
        starting_file = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
        file = open(self.dir_output + '/' + starting_file + '.txt', 'w')
        file.close()

        while True:
            starting_time = datetime.datetime.now()
            PARAMS = 'capture' + '?' + 'block=true'
            
            response = requests.get(self.address + '/' + PARAMS)
            PARAMS = 'capture/' + response.json()['id']
            
            while True:
                response = requests.get(self.address+'/'+PARAMS)
                if response.json()['status'] == 'pending':
                    #time.sleep(0.75)
                    pass
                else:
                    end_time = datetime.datetime.now()
                    file = open(self.dir_output + '/' + starting_file + '.txt', 'a')
                    file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + '\n')
                    file.close()
                    print('ALTUM : picture at ' + end_time.strftime("%Y-%m-%d %H:%M:%S.%f"))                    
                    break
            
            delta_time = end_time - starting_time
            delta_time = interval - delta_time.seconds - delta_time.microseconds/(10**6)
            if delta_time < 0:
                delta_time = 0
            time.sleep(delta_time)

            if status():
                break
    
    def camera_position(self):
        #get GPS information
        PARAMS = 'gps'
        response = requests.get(self.address+'/'+PARAMS)
        response.json()
        print(response.json())
        
    def camera_orientation(self):
        #Get or set camera orientation
        PARAMS = 'orientation'
        response = requests.get(self.address+'/'+PARAMS)
        response.json()
        print(response.json())
    
    def dls_imu(self):
        # Get values from imu, where angles are in radians and accelerometer in ms-2
        PARAMS = 'dls_imu'
        response = requests.get(self.address+'/'+PARAMS)
        response.json()
        print(response.json())

    def camera_status(self):
        #Get or set camera orientation
        PARAMS = 'status'
        response = requests.get(self.address+'/'+PARAMS)
        response.json()
        print(response.json())

    def download(self,download = True, delete = True):
        # This need to iterate to see if there is any folders. Normaly it should correspond to the last folder
        PARAMS = '/files'
        response = requests.get(self.address+'/'+PARAMS)
        sets = [x for x in response.json()['directories'] if "SET" in x]
        sets.sort()
        sets.sort()
        print("Working with the following sets: " + str(sets) +"\n")
        if len(sets)>0:
            for PARAMS_set in sets: 
                # Set
                response_set = requests.get(self.address + '/' + PARAMS + '/' + PARAMS_set)
                set_altum = response_set.json()['directories']
                if len(set_altum)>0:
                    if download == True:
                        print('\n'+ PARAMS_set +' will be download')
                        os.mkdir(PARAMS_set)
                        os.chdir(PARAMS_set)
                    # First we download the pictures
                    for directory in set_altum:
                        response_dir = requests.get(self.address + '/' + PARAMS + '/' + PARAMS_set + '/' + directory)
                        if len(response_dir.json()['files'])>0:
                            # Download the pictures
                            for file in range(0,len(response_dir.json()['files'])):
                                #Download the file
                                PARAMS_file = response_dir.json()['files'][file]['name']
                                if download == True:
                                    print('Downloading ' + PARAMS_file)
                                    response_file = requests.get(self.address + '/' + PARAMS + '/' + PARAMS_set + '/' + directory +'/'+PARAMS_file, stream = True)
                                    with open(str(PARAMS_file), 'wb') as out_file:
                                        out_file.write(response_file.content)
                                    del response_file
                                #Remove it
                                if delete == True:
                                    response_file = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set + '/' + directory +'/'+PARAMS_file)
                                    time.sleep(0.1)
                            if delete == True:
                                delete_empy_dir = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set + '/' + directory)                
                                time.sleep(0.1)
                        else:
                            delete_empy_dir = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set + '/' + directory)
                            time.sleep(0.1)
                    # Then the dat files
                    response_set_files = requests.get(self.address + '/' + PARAMS + '/' + PARAMS_set)
                    set_altum_files = response_set.json()['files']
                    
                    for a in set_altum_files:
                        if download == True:
                            response_file_dat = requests.get(self.address + '/' + PARAMS + '/' + PARAMS_set + '/' + a['name'], stream = True)
                            with open(str(a['name']), 'wb') as out_file:
                                out_file.write(response_file_dat.content)
                        if delete == True:
                            print('Deleting set ' + str(a['name']))
                            delete_file = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set + '/' + a['name'])
                            time.sleep(0.1)
                            
                    if delete == True:
                        delete_set = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set)
                        time.sleep(0.1)

                    os.chdir('..')
                else:
                    # It can happend that the GPS create files without pictures. In that case we can delete all without problem
                    set_altum_files = response_set.json()['files']
                    for a in set_altum_files:
                        delete_file = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set + '/' + a['name'])
                        time.sleep(0.1)
                    delete_set = requests.get(self.address + '/' + 'deletefile' + '/' + PARAMS_set)
                    time.sleep(0.1)
    
    def camera_power_down(self, mode='post'):
        # See if the camera is ready to go down or we can set it to be ready.
        PARAMS = 'powerdownready'
        if mode == 'get':
            response = requests.get(self.address+'/'+PARAMS)
            return(response.json())
        elif mode=='post':
            response = requests.post(self.address+'/'+PARAMS, data={"power_down":"true"})
            return(response.json())
        else:
            return('Mode non accepted')

# ---------- Battery ----------------
class battery_handler():
    def __init__(self,i2caddress, bus):
        self.i2caddress = i2caddress
        #self.i2cbus = SMBus(bus)

    def is_alive(self):
        #if self.i2cbus == True:
        return True
        #else:
        #    return False
    
    # Main functions from the datasheet
    def get_temperature():
        return(i2cbus.read_word_data(self.i2caddress,0x08)/10-273.15)
   
    def get_voltage():
        return(i2cbus.read_word_data(self.i2caddress,0x09)/1000)

    def get_current():
        return(i2cbus.read_word_data(self.i2caddress,0x0a))

    def get_current_average():
        return(i2cbus.read_word_data(self.i2caddress,0x0b))

    def get_charge_in_percentage():
        return(i2cbus.read_word_data(self.i2caddress,0x0d))

    def get_charge_remining_time():
        return(i2cbus.read_word_data(self.i2caddress,0x11))


# ---------- Sony camera ---------------
class sony_camera():
    def __init__(self, gpio_focus, gpio_image, gpio_detector):
        self.focus = gpio_focus
        self.image = gpio_image
        self.detector = gpio_detector
        self.running = True
        self.image_counter = 0

        GPIO.setup(self.focus, GPIO.OUT, initial = GPIO.HIGH)
        GPIO.setup(self.image, GPIO.OUT, initial = GPIO.HIGH)
        GPIO.setup(self.detector, GPIO.IN)

        GPIO.add_event_detect(self.detector, GPIO.FALLING, callback=self.write_time)

    def is_alive(self):
        #ToDO
        return True
    
    def capture_start(self, time_s, time_file_path):
        self.file = open(time_file_path, "a")
        while True and self.running:
            GPIO.output(self.focus, GPIO.LOW)
            GPIO.output(self.image, GPIO.LOW)
            time.sleep(1)
            self.image_counter += 1
            GPIO.output(self.focus, GPIO.HIGH)
            GPIO.output(self.image, GPIO.HIGH)
            time.sleep(time_s - 1)

    def capture_stop(self):
        self.running = False        
        self.file.close()

    def write_time(self):
        self.file.write(str(self.image_counter) + "\t" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))