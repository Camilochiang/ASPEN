#!/usr/bin/python3
import os
import re

from kivy.clock import Clock
from kivy.factory import Factory
import numpy as np
import time
from threading import Thread

#Notes:
#20210425 The touch screen is detecting two touchs, So i had to change this file with small time.sleeps and disabling the buttons during that time

class Button(Factory.Button):
    __events__ = ('on_press', )

    status = Factory.BooleanProperty(0)
    disabled = Factory.BooleanProperty(0)    

    def __init__(self,**kwargs):
        super(Button,self).__init__(**kwargs)

    def on_press(self, *largs):
        self.thread = Thread(target=self.block_button, daemon=True)
        self.thread.start()

    def block_button(self):
        self.disabled = True
        time.sleep(0.5)
        self.disabled = False

class OpenerButton(Factory.Button):
    __events__ = ('on_press', )

    status = Factory.BooleanProperty(0)
    open = Factory.BooleanProperty(0)    

    def __init__(self,**kwargs):
        super(OpenerButton,self).__init__(**kwargs)

    def on_press(self, *largs):
        self.thread = Thread(target=self.block_button, daemon=True)
        self.thread.start()

    def block_button(self):
        self.disabled = True
        time.sleep(0.5)
        self.disabled = False

class FadingButton(Factory.Button):
    __events__ = ('on_press', )

    status = Factory.BooleanProperty(0)
    background_color = Factory.ColorProperty(None)    
    clock_interval = 0.1
    val = 0
    color_range = [*np.arange(0,1, clock_interval), *np.arange(1,0,-clock_interval)]

    def __init__(self,**kwargs):
        super(FadingButton,self).__init__(**kwargs)
    
    def on_release(self):
        self.status = not self.status
        if self.status == True:
            self._clockev = Clock.schedule_interval(self.color_fading, self.clock_interval)
        else:
            self.color = [.0,0,0,1]
            self.val = 0
            self._clockev.cancel()            
    
    def color_fading(self, time):
        if self.val < (1.9/self.clock_interval):
            self.val += 1
        else:
             self.val = 0
        self.color = [.8,0,0,1*self.color_range[self.val]]

    def on_press(self, *largs):
        self.thread = Thread(target=self.block_button, daemon=True)
        self.thread.start()

    def block_button(self):
        self.disabled = True
        time.sleep(0.5)
        self.disabled = False

class LongpressButton(Factory.Button):
    __events__ = ('on_press','on_long_press', )

    long_press_time = Factory.NumericProperty(1)

    sensor_name = Factory.StringProperty(None)
    text = Factory.StringProperty(None)
    status = Factory.BooleanProperty(1)
    open = Factory.BooleanProperty(0)
    color = Factory.ColorProperty(None)
    background_color = Factory.ColorProperty(None)
    
    def __init__(self,**kwargs):
        super(LongpressButton,self).__init__(**kwargs)

    def on_state(self, instance, value):
        if value == 'down':
            self.time_start = time.time()
    
    def on_release(self):
        self.time_end = time.time()
        if (self.time_end - self.time_start) > self.long_press_time: # Click longer than 1 second
            self._clockev = Clock.schedule_once(self._do_long_press)            
        else:
            try:
                self._clockev.cancel()
            except:
                pass

            self.status = not self.status
            if self.status:
                self.text = self.sensor_name + ': \n ON'
                self.color = [.8,0,0,1]
                self.background_color = [1,1,0,.2]

            else:
                self.text = self.sensor_name + ': \n OFF'
                self.color = [.0,0,0,1]
                self.background_color = [1,1,0,.2]

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        self.thread = Thread(target=self.block_button, daemon=True)
        self.thread.start()
        pass

    def on_press(self, *largs):
        self.thread = Thread(target=self.block_button, daemon=True)
        self.thread.start()
        pass

    def block_button(self):
        self.disabled = True
        time.sleep(1)
        self.disabled = False

def create_folders():
    # Create new folder structure for next project
    output_path = os.path.dirname(os.path.dirname(os.getcwd()))
    folders = os.listdir(output_path)
    max_folder = 1

    # First we need to get the last SET/folder number.
    for x in sorted(folders):
        try:
            if bool(re.match('SET_',x)):
                if int(x[(len(x)-3):(len(x))]) > max_folder:
                    max_folder = int(x[(len(x)-3):(len(x))])
                elif int(x[(len(x)-3):(len(x))]) == max_folder:
                    max_folder = max_folder + 1
        except:
            pass

    max_folder = str(max_folder)
    zeros = (['0']*(4-len(max_folder)))
    zeros.append(max_folder)
    max_folder= ''.join(zeros)

    directory = output_path + '/SET_' + str(max_folder)
    os.mkdir(directory)
    os.mkdir(directory + '/captured')
    os.mkdir(directory + '/captured/altum')
    os.mkdir(directory + '/captured/ROS')
    os.mkdir(directory + '/captured/pictures')
    print('[MAIN   ]: Creating ' + directory)
    
    return directory