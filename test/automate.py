"""
This file deals with GUI automation to test several WebRTC apps

Screen resolution should be set to 1920x1080

Chromium browser window should be set to maximize
"""
import os
os.environ['DISPLAY'] = ':0'

import pyautogui
import sys
import time


pyautogui.PAUSE = 0.25
pyautogui.FAILSAFE = True


def recordJitsi():
    pyautogui.moveTo(1126, 986)

    time.sleep(1)
    pyautogui.click(1126, 986, button='left')

    time.sleep(1)
    pyautogui.click(1020, 478, button='left')
    
    time.sleep(1)
    pyautogui.click(1016, 548, button='left')

def stopRecordJitsi():
    pyautogui.moveTo(1126, 986)

    time.sleep(1)
    pyautogui.click(1126, 986, button='left')

    time.sleep(1)
    pyautogui.click(1020, 478, button='left')
    
    time.sleep(1)
    pyautogui.click(1036, 409, button='left')
    time.sleep(1)

def stopRecordWhereby():
    pyautogui.moveTo(961, 981)
    time.sleep(2)

    pyautogui.click(961, 926, button='left')

    time.sleep(1)
    pyautogui.click(1646, 425, button='left')
    time.sleep(2)

def recordWhereby():
    pyautogui.click(962, 981, button='left')
    
    time.sleep(1)
    pyautogui.click(962, 767, button='left')

    time.sleep(1)
    pyautogui.click(962, 216, button='left')
    
    time.sleep(1)
    pyautogui.click(1209, 561, button='left')
    

    #time.sleep(1)
    
    #pyautogui.click(1888, 322, button='left')
    
    #time.sleep(0.2)
    #pyautogui.click(1893, 380, button='left')
    
    #time.sleep(1)
    #pyautogui.click(1805, 531, button='left')

def ApprtcAutomation():
    #Appr.tc requires a single "Join Button" to be pressed to join a call

    time.sleep(0.25)
    join_button = (959, 920)
    pyautogui.click(join_button[0], join_button[1], button='left')


def automateChromium(webrtc_application, mode):
    #Print debug info
    #print "Window size: " + str(width) + "x" + str(height)
    print "Mouse position: " + str(pyautogui.position())

    if("whereby" in webrtc_application):
        print "WhereBy Automation: Nothing to do."
    elif("appr.tc" in webrtc_application):
        print "Appr.tc Automation: Started"
        ApprtcAutomation()
    elif("meet.jit.si" in webrtc_application):
        print "Jitsi Automation: Nothing to do."

def gracefullyCloseChromium():
    pyautogui.click(1265, 20, button='left')
    pyautogui.click(1265, 20, button='left')

def recordVideo(webrtc_application):
    print "Mouse position: " + str(pyautogui.position())
    if("whereby" in webrtc_application):
        print "WhereBy Automation: Recording to browser"
        recordWhereby()
    elif("meet.jit.si" in webrtc_application):
        print "Jitsi Automation: Recording to Dropbox."
        recordJitsi()
    
def stopRecordVideo(webrtc_application):
    print "Mouse position: " + str(pyautogui.position())
    if("whereby" in webrtc_application):
        print "WhereBy Automation: Stopping Recording and Saving File"
        stopRecordWhereby()
    elif("meet.jit.si" in webrtc_application):
        print "Jitsi Automation: Stopping Recording to Dropbox."
        stopRecordJitsi()
    


if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print "Input intended application"
        sys.exit(0)

    webrtc_application = sys.argv[1]
    automateChromium(webrtc_application, "callee")
