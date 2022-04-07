#!/usr/bin/python3

# GUI (Graphical User Interface) for ASPEN project
# Author: Camilo Chiang
# Version 1.0
# Release date : 
# Description: A Class (GUI) that work as "orchestrer" for other classes (ROS sensors, GPIO, etc, ML)

## Libraries
# Basic
import pexpect
from threading import Thread
import cv2
import time
import numpy as np
import argparse
import json

# Kivy
import kivy
kivy.require('2.0.0')
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
Config.set('graphics', 'fullscreen', 2)
Config.set('kivy', 'log_level', 'info')
Config.write()

#ROS
import rospy

#ASPEN
#from lib import sensors
from lib import helpers
from lib.yolov5 import detect_ASPEN

### Python sensors
#Altum = sensors.altum_camera(device ='Camera_1', address = "http://192.168.10.254",  path = directory)
#Sony = sensors.sony_camera()

# Main class
class MainApp(App):
    def __init__(self,model,conf_thres, depth_limit,**kwargs):
        super(MainApp,self).__init__(**kwargs)
        self.loading_model_banner_timer = [0,3] # Lets say that it take 3 seconds to load your model
        self.pwd = None
        self.last_frame = None
        # self.default variables
        self.default_distance = depth_limit # In metters
        self.crop = str(model)
        self.conf_thres = float(conf_thres)
        self.default_time_sony = 5
        self.default_time_altum = 5
        self.count = 0
        self.previus_counts = []
        self.previus_dics = [] # This one is list but it will have dictionaries inside!

    def status_toggle(self, _):
        if self.button_status.text == "Recording: \n OFF":
            self.button_status.text = "Recording: \n ON"
            # If you are recording, block all the other buttons
            self.button_distance.disabled = True
            self.sony.disabled = True
            self.altum.disabled = True                        
            self.button_model.disabled = True

            print('Writing to' + self.pwd)
            # Start recording
            # If is possible we should record compressed topics for camara/color and camara/depth, if not , raw will do it
            self.record_bag = pexpect.spawn('rosbag record -o ' +  self.pwd + '/captured/ROS/' + ' /livox/lidar /imu /camera/color/rgb/image_raw/compressed /camera/depth/image_rect_raw/compressed /rosout_agg __name:=my_bag')
            while not self.record_bag.eof():
                strLine = self.record_bag.readline()
                if 'Subscribing to /rosout_agg' in strLine.decode():
                    break
            # Activate cameras (Altum and Sony) and logs
            # Altum
            status_altum = False
            #thread_altum = threading.Thread(target = Altum.capture, args=(lambda: status_altum, self.default_time_altum), daemon = True)
            #thread_altum.start()
            # Sony

            self.status_bar_updater('Recording', 0,0,1,.2)

        else: 
            self.stopper_bag = pexpect.spawn('rosnode kill /my_bag')
            while True:
                strLine = self.stopper_bag.read()
                if 'killed' in strLine.decode():
                    self.stopper_bag.close()
                    break
                time.sleep(0.1)

            self.button_status.text = "Recording: \n OFF"
            self.button_status.color = [.0,0,0,1]            
            self.button_distance.disabled = False
            self.button_model.disabled = False
            self.sony.disabled = False
            self.altum.disabled = False
            self.status_bar_updater('Ready to GO!', 0,1,0,.2)        

    def distance_or_time(self,change, sensor,x_center, y_center):
        direction = +1 if sensor == "distance" else -1

        if sensor == 'distance':
            self.default_distance =  round(self.default_distance + .1*change, 2)
            if self.default_distance < 0.4:
                self.default_distance = 0.4
            value_to_show = self.default_distance
            unit = ' m'
            button = self.button_distance_down
        elif sensor == 'Sony':
            self.default_time_sony = round(self.default_time_sony + .1*change, 2)
            if self.default_time_sony < 1:
                self.default_time_sony = 1
            value_to_show = self.default_time_sony
            unit = ' s'            
        else:
            self.default_time_altum = round(self.default_time_altum +.1*change, 2)
            if self.default_time_altum < 1:
                self.default_time_altum = 1            
            value_to_show = self.default_time_altum
            unit = ' s'
        
        # Update distance/time
        self.rl.remove_widget(self.button_distance_val)

        self.button_distance_val = Label(size_hint =(.05, .1),
                color = [.8,0,0,1],        
                bold = True,     
                pos_hint ={'center_x': x_center, 'center_y': y_center + 0.1*direction},
                text = str(str(value_to_show) + unit))
        with self.button_distance_val.canvas:
            Color(1,1,0,.15)
            Rectangle(pos=(self.button_distance_val.pos_hint['center_x']*800 -22.5,
                self.button_distance_val.pos_hint['center_y']*480 - 22.5), size = (45,45))                
        
        self.rl.add_widget(self.button_distance_val)

    def change_config(self, sensor, x_center, y_center):
        direction = +1 if sensor == "distance" else -1

        if sensor =='distance':
            self.button_distance.open = not self.button_distance.open
            choosed_button = self.button_distance
            value_to_show  = self.default_distance
            unit = ' m'            
        elif sensor == 'Sony':
            self.sony.open = not self.sony.open
            choosed_button = self.sony
            value_to_show = self.default_time_sony
            unit = ' s'            
        else:
            self.altum.open = not self.altum.open
            choosed_button = self.altum
            value_to_show = self.default_time_altum
            unit = ' s'            

        if choosed_button.open:
            self.button_distance_down = Button(size_hint =(.05, .1),
                pos_hint ={'center_x': x_center - 0.05 , 'center_y': y_center + 0.1*direction},
                text ="D",
                bold = True,
                color = [.8,0,0,1],
                background_color = [1,1,0,.2],
                halign = 'center',
                on_press = lambda *args: self.distance_or_time(-1, sensor, x_center, y_center))

            self.button_distance_val = Label(size_hint =(.05, .1),
                pos_hint ={'center_x': x_center, 'center_y': y_center + 0.1*direction},
                color = [.8,0,0,1],
                bold = True,                
                text = str(str(value_to_show) + unit))

            with self.button_distance_val.canvas:
                Color(1,1,0,.15)
                Rectangle(pos=(self.button_distance_val.pos_hint['center_x']*800 -22.5,
                    self.button_distance_val.pos_hint['center_y']*480 - 22.5), size = (45,45))

            self.button_distance_up = Button(size_hint =(.05, .1),
                pos_hint ={'center_x': x_center + 0.05, 'center_y': y_center + 0.1*direction},
                text ="U",
                bold = True,                
                color = [.8,0,0,1],
                background_color = [1,1,0,.2],
                halign = 'center',
                on_press = lambda *args: self.distance_or_time(+1, sensor, x_center, y_center))
        
            self.rl.add_widget(self.button_distance_down)
            self.rl.add_widget(self.button_distance_val)
            self.rl.add_widget(self.button_distance_up)

            # As we use the same function we will block the non used button that use the same function
            if sensor == 'distance':
                self.sony.disabled = True
                self.altum.disabled = True 
                self.button_model.disabled = True
                self.button_counter.disabled = True                
            elif sensor == 'Sony':
                self.button_distance.disabled = True
                self.altum.disabled = True 
                self.button_model.disabled = True
                self.button_counter.disabled = True
            else:
                self.button_distance.disabled = True                
                self.sony.disabled = True
                self.button_model.disabled = True
                self.button_counter.disabled = True

        else:
            self.rl.remove_widget(self.button_distance_down)
            self.rl.remove_widget(self.button_distance_val)
            self.rl.remove_widget(self.button_distance_up)
            self.button_distance.text ='Used ditance: \n' + str(self.default_distance) + 'm'

            self.button_distance.disabled = False
            self.button_model.disabled = False
            self.button_counter.disabled = False            
            self.sony.disabled = False
            self.altum.disabled = False

    def change_model_name(self, new_crop):
        self.crop = new_crop
        self.button_model.text = 'Model: \n' + self.crop

    def change_model(self, x_center, y_center):
        return 1
        ##changemodelinsideapp
        self.button_model.open = not self.button_model.open     

        if self.button_model.open:
            self.button_model_1 = Button(size_hint =(.15, .1),
                pos_hint ={'center_x': x_center , 'center_y': y_center + 0.3},
                text ="Apple/Pear",
                bold = True,
                color = [.8,0,0,1],
                background_color = [1,1,0,.2],
                halign = 'center',
                on_press = lambda *args: self.change_model_name('Apple/Pear'))

            self.button_model_2 = Button(size_hint =(.15, .1),
                pos_hint ={'center_x': x_center, 'center_y': y_center + 0.2},
                text ="Strawberry",
                bold = True,                
                color = [.8,0,0,1],
                background_color = [1,1,0,.2],
                halign = 'center',
                on_press = lambda *args: self.change_model_name('Strawberry'))
            
            self.button_model_3 = Button(size_hint =(.15, .1),
                pos_hint ={'center_x': x_center, 'center_y': y_center + 0.1},
                text ="Tomato",
                bold = True,                
                color = [.8,0,0,1],
                background_color = [1,1,0,.2],
                halign = 'center',
                on_press = lambda *args: self.change_model_name('Tomato'))
        
            self.rl.add_widget(self.button_model_1)
            self.rl.add_widget(self.button_model_2)
            self.rl.add_widget(self.button_model_3)

            self.sony.disabled = True
            self.altum.disabled = True 
            self.button_counter.disabled = True
            self.button_distance.disabled = True
            self.button_status.disabled = True          

        else:
            self.rl.remove_widget(self.button_model_1)
            self.rl.remove_widget(self.button_model_2)
            self.rl.remove_widget(self.button_model_3)

            self.loading_model_label = Label(text='Loading model: ' + str(round(self.loading_model_banner_timer[0],2)) + '%',
                size_hint= (1,1),
                valign = 'bottom',
                halign = 'left',
                size = (800,480),
                pos=(0,0))
            self.loading_model_label.bind(size=self.loading_model_label.setter('text_size')) 
            with self.loading_model_label.canvas:
                Color(1,0,0,.2)
                Rectangle(pos=(0,0), size = self.loading_model_label.size)
            self.rl.add_widget(self.loading_model_label)

            self._clockev = Clock.schedule_interval(self.loading_model_banner, self.loading_model_banner_timer[1]*0.1)


            # We load the model to be use in a diferent thread
            #rospy.signal_shutdown()
            #rospy.init_node('GUI-YOLOv5', anonymous=False)            
            #print(1)
            #self.spin_thread = Thread(target=lambda: rospy.spin(), daemon=True)
            #self.spin_thread.start()            
            #self.model_thread = Thread(target=detected_agroscope.run(), args=(self.crop,), daemon=True)
            #self.model_thread.start()

    def loading_model_banner(self, time_int):
        # Creating banner       
        if self.loading_model_banner_timer[0] < self.loading_model_banner_timer[1]:
            percentage = self.loading_model_banner_timer[0]*100/self.loading_model_banner_timer[1]
            self.loading_model_label.text = 'Loading model: ' + str(round(self.loading_model_banner_timer[0]*100/self.loading_model_banner_timer[1],2)) + '%'
            self.loading_model_banner_timer[0] += time_int
            
        else:
            self.loading_model_banner_timer[0] = 0
            self.rl.remove_widget(self.loading_model_label)            
            self._clockev.cancel()
            
            self.sony.disabled = False
            self.altum.disabled = False             
            self.button_counter.disabled = False
            self.button_distance.disabled = False
            self.button_status.disabled = False 

    def counter_restart(self, _):
        # We save the important stuff
        self.previus_counts.append(self.count)
        self.previus_dics.append(self.YOLOv5.objects_characteristics)

        # We reiniciate all
        self.count = 0        
        self.YOLOv5.objects_characteristics = {'id':[], 'class':[], 'size':[]} # a dictionary of lists
        self.button_counter.text = "Count: \n" + str(self.count)

    def status_bar_updater(self, text, r,g,b,a):
        self.rl.remove_widget(self.status_bar)
        self.status_bar = Label(text=text,
            size_hint= (1,1),
            valign = 'bottom',
            halign = 'left',
            size = (800,20),
            pos=(0,0))
        self.status_bar.bind(size=self.status_bar.setter('text_size')) 
        with self.status_bar.canvas:
            Color(r,g,b,a)
            Rectangle(pos=(0,0), size = self.status_bar.size)        
        self.rl.add_widget(self.status_bar)
    
    def check_up(self, _):
         # Before starting we will run some checkups to be sure that we can proceed
        if self._clockev_ROS_count == 0:
        # We check : CAMERA RGB
            if "/camera/color/rgb/image_raw" in [item for sublist in rospy.get_published_topics() for item in sublist]:
                self.status_bar_updater('RGB compressed topic detected', 0,1,0,.2)
                self._clockev_ROS_count += 1
            else:
                self.status_bar_updater('RGB compressed topic non detected', 1,0,0,.2)
                self._clockev_ROS.cancel()
        elif self._clockev_ROS_count == 1:
        # DEPTH:
            if "/camera/depth/rgb/image_rect_raw/compressed" in [item for sublist in rospy.get_published_topics() for item in sublist]:
                self.status_bar_updater('Depth topic detected', 0,1,0,.2)
                self._clockev_ROS_count += 1                
            else:
                self.status_bar_updater('Depth topic not present',1,0,0,.2)
                self._clockev_ROS.cancel()
        elif self._clockev_ROS_count == 2:
        # IMU:
            if "/imu" in [item for sublist in rospy.get_published_topics() for item in sublist]:
                self.status_bar_updater('Depth topic detected', 0,1,0,.2)
                self._clockev_ROS_count += 1                
            else:
                self.status_bar_updater('Depth topic not present',1,0,0,.2)
                self._clockev_ROS.cancel()
        elif self._clockev_ROS_count == 3:
        # Lidar:
            if "/livox_lidar_publisher" in [item for sublist in rospy.get_published_topics() for item in sublist]:
                self.status_bar_updater('LiDAR topic detected', 0,1,0,.2)
                self._clockev_ROS_count += 1                
            else:
                self.status_bar_updater('LiDAR topic not present',1,0,0,.2)
                self._clockev_ROS.cancel()
        else:
            self.status_bar_updater('Ready to GO!', 0,1,0,.2)
            self._clockev_ROS.cancel()               

    def build(self):
        #GUI
        self.rl = RelativeLayout(size =(800, 480))
        self.img1 = Image()
        #self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/50.0)
        #self.car= Camera(play=True, index=0, resolution=(800,480))
        #print(self.car)
        #self.rl.add_widget(self.car)
        self.rl.add_widget(self.img1)

        # Buttons
        # Normal buttons
        self.button_counter = Button(size_hint =(.1, .1),
            pos_hint ={'center_x':.95, 'center_y':.10},
            text ="Count: \n" + str(self.count),
            halign = 'center',            
            bold = True,
            color = [.8,0,0,1],
            background_color = [1,1,0,.2],
            on_press = self.counter_restart)
        # Button that can open another buttons        
        self.button_distance = helpers.OpenerButton(size_hint =(.15, .1),
            pos_hint ={'center_x':.825, 'center_y':.10},
            text ='Used ditance: \n' + str(self.default_distance) + 'm',
            halign = 'center',
            bold = True,
            color = [.8,0,0,1],
            background_color = [1,1,0,.2],
            on_press = lambda *args: self.change_config("distance", .825, .10))
        # Show model
        self.button_model = helpers.OpenerButton(size_hint =(.15, .1),
            pos_hint ={'center_x':.675, 'center_y':.10},
            text ='Model: \n' + self.crop,
            halign = 'center',
            bold = True,
            color = [.8,0,0,1],
            background_color = [1,1,0,.2],
            on_press = lambda *args: self.change_model(.675, .10))
        # Fadding buttons
        self.button_status = helpers.FadingButton(size_hint =(.1, .1),
            pos_hint ={'center_x':.55, 'center_y':.10},
            text ="Recording: \n OFF",
            halign = 'center',            
            bold = True,
            color = [.0,0,0,1],
            background_color = [1,1,0,.2],
            on_press = self.status_toggle)
        # And Long press buttons
        self.sony = helpers.LongpressButton(status = 1,
            size_hint =(.1, .1),
            pos_hint ={'center_x':0.075, 'center_y':.95},
            sensor_name ="Sony",
            text = 'Sony: \n ON',
            halign = 'center',            
            bold = True,
            color = [.8,0,0,1],
            background_color = [1,1,0,.2],
            on_long_press = lambda *args: self.change_config("Sony", 0.075, .95))
        self.altum = helpers.LongpressButton(status = 1,
            size_hint =(.1, .1),
            pos_hint ={'center_x':.175, 'center_y':.95},
            sensor_name ="Altum",
            text = 'Altum: \n ON',
            halign = 'center',            
            bold = True,
            color = [.8,0,0,1],
            background_color = [1,1,0,.2],
            on_long_press = lambda *args: self.change_config("Altum", .175, .95))
        
        self.rl.add_widget(self.button_status)
        self.rl.add_widget(self.button_model)
        self.rl.add_widget(self.button_distance)
        self.rl.add_widget(self.button_counter)
        self.rl.add_widget(self.sony)
        self.rl.add_widget(self.altum)

        # Status bar
        self.status_bar = Label(text='Running check up',
            size_hint= (1,1),
            valign = 'bottom',
            halign = 'left',
            size = (800,20),
            pos=(0,0))
        self.status_bar.bind(size=self.status_bar.setter('text_size')) 
        with self.status_bar.canvas:
            Color(0,1,0,.2)
            Rectangle(pos=(0,0), size = self.status_bar.size)
        self.rl.add_widget(self.status_bar)
  
        #ROS management
        #rospy.init_node('GUI', anonymous=False)
        
        # Create the YOLOv5 thread
        if self.crop == 'Apple':
            weights = '/home/ubuntu/Agroscope/ASPEN/Software/models/Apple.pt'
            data_yaml = '/home/ubuntu/Agroscope/ASPEN/Software/models/Agroscope_apples.yaml'
        elif self.crop == 'Strawberry':
            weights = '/home/ubuntu/Agroscope/ASPEN/Software/models/Strawberry.pt'
            data_yaml = '/home/ubuntu/Agroscope/ASPEN/Software/models/Agroscope_strawberries.yaml'
        elif self.crop == 'Tomato':
            weights = '/home/ubuntu/Agroscope/ASPEN/Software/models/Tomato.pt'
            data_yaml = '/home/ubuntu/Agroscope/ASPEN/Software/models/Agroscope_tomatoes.yaml'
        else:
            print('Please select a model. Exiting')
            quit()

        self.YOLOv5 = detect_ASPEN.YOLOv5(weights=weights, conf_thres = self.conf_thres, data_yaml = data_yaml, depth_limit = self.default_distance)
        self.yolov5_thread = Thread(target = self.YOLOv5.update, args=(), daemon = True)
        self.yolov5_thread.start()

        #image_reader = rospy.Subscriber("/camera/color/rgb/image_raw", Image_ROS, self.image_callback)
        #imagedepth_reader = rospy.Subscriber("/camera/depth/rgb/image_rect_raw", Image_ROS, self.imagedepth_callback)

        #self.spin_thread = Thread(target=lambda: rospy.spin(), daemon=True)
        #self.spin_thread.start()

        return self.rl

    def on_start(self, **kwargs):
        self._clockev_ROS_count = 0
        self._clockev_ROS = Clock.schedule_interval(self.check_up, 1)
        # We will create a directory everytime that we start the app
        self.pwd = helpers.create_folders()

    def on_close(self):
        #Force the counts to be written
        self.previus_counts.append(self.count)
        self.previus_dics.append(self.YOLOv5.objects_characteristics)
         
        # Save the counts
        file_name = time.strftime(r"%Y%m%d_%H_%M_%S", time.localtime()) + '_counts.txt'
        with open(self.pwd + '/' + file_name, 'w') as f:
            for idx, _ in enumerate(self.previus_counts):
                f.write('Total count:' + str(self.previus_counts[idx]) + '\n')
                f.write(json.dumps(self.previus_dics[idx]) + '\n')
                f.write('\n')            

    def update(self, dt):
        self.last_frame = self.YOLOv5.imDisplayed
        self.last_frame = cv2.resize(self.last_frame, (800,480))
        # convert it to texture
        buf1 = cv2.flip(self.last_frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(self.last_frame.shape[1], self.last_frame.shape[0]), colorfmt='bgr') 
        #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

        # We update the counter
        self.count = len(self.YOLOv5.objects_characteristics['id'])
        self.button_counter.text = "Count: \n" + str(self.count)


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", dest="model")
    parser.add_argument("-c", "--conf_thres", dest="conf_thres")
    parser.add_argument("-d", "--depth_limit", dest="depth_limit")
    args = parser.parse_args()

    app = MainApp(model = args.model, conf_thres = args.conf_thres, depth_limit = args.depth_limit)
    app.run()
    app.on_close()    