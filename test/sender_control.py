import sys, os
import subprocess as sub
import time, sched
import random
import threading
import requests
from termcolor import colored 
from automate import automateChromium, gracefullyCloseChromium, recordVideo, stopRecordVideo


def PrintColored(string, color):
    print(colored(string, color))

#################################################################################
# Useful definitions


stegozoa_src_folder_location = '/home/vagrant/stegozoa/src/'
stegozoa_test_folder_location = '/home/vagrant/stegozoa/test/'
analytics_folder_location = '/home/vagrant/stegozoa/analytics/'

stegozoa_cap_folder = "/home/vagrant/SharedFolder/StegozoaCaps/StegozoaTraffic/"
stegozoa_multisample_cap_folder = "/home/vagrant/SharedFolder/StegozoaCaps/StegozoaMultiSampleTraffic/"
regular_cap_folder = "/home/vagrant/SharedFolder/StegozoaCaps/RegularTraffic/"
regular_multisample_cap_folder = "/home/vagrant/SharedFolder/StegozoaCaps/RegularMultiSampleTraffic/"
video_folder = "/home/vagrant/SharedFolder/VideoBaselines/"

chromium_builds_folder = "/home/vagrant/chromium_builds/"

SRC_IP = "192.168.50.100"
DST_IP = "192.168.51.101"
MIDDLEBOX_IP = "192.168.50.103"
NETWORK_INTERFACE = "enp0s8"


capture_duration = 35
iperf_duration = 25
sync_early = 2
sync_late = 4

#############################################################################
# Choose WebRTC application to test

WEBRTC_APPLICATION = "https://whereby.com/123"
#WEBRTC_APPLICATION = "https://appr.tc/r/"
#WEBRTC_APPLICATION = "https://meet.jit.si/12349876"

#############################################################################

headless_env = dict(os.environ)
headless_env['DISPLAY'] = ':0'


network_conditions = [
    
    #No changes to the network
    #[[None], "regular"],

    #2ms, 5ms, 10ms
    #Variation of RTT between VM1 / VM3
    #[["netem delay 7ms"], "delay_15.delay_15"],
    [["netem delay 25ms"], "delay_50"],
    #[["netem delay 50ms"], "delay_100.delay_15"],

    
    #Set baseline RTT between VM1 / VM3, vary bandwidth conditions (TC)
    [["htb default 12", "htb rate 1500kbit ceil 1500kbit", "netem delay 25ms"], "delay_50-bw_1500"],
    [["htb default 12",   "htb rate 250kbit ceil 250kbit", "netem delay 25ms"], "delay_50-bw_250"],
    [["htb default 12",   "htb rate 750kbit ceil 750kbit", "netem delay 25ms"], "delay_50-bw_750"],
    
    #Set baseline RTT between VM1 / VM3, vary packet loss conditions
    [["netem delay 25ms loss 2%"], "delay_50-loss_2"],
    [["netem delay 25ms loss 10%"], "delay_50-loss_10"],
    [["netem delay 25ms loss 5%"], "delay_50-loss_5"],

]

#################################################################################

def RESTCall(method, args=""):
    url='http://' + DST_IP + ':5005/' + method
    response = ''
    try:
        response = requests.post(url, data=args)
    except requests.exceptions.RequestException as e:
        print e

def RESTCallMiddlebox(method, args=""):
    url='http://' + MIDDLEBOX_IP + ':5005/' + method
    response = ''
    try:
        response = requests.post(url, data=args)
    except requests.exceptions.RequestException as e:
        print e

def CaptureTraffic(sample_name, capture_folder):
    cmd = 'tcpdump ip host ' + SRC_IP + ' -i ' + NETWORK_INTERFACE + ' -G ' + str(capture_duration) + ' -W 1 -w ' + capture_folder + "\"" + sample_name + "\"" + '.pcap'
    p = sub.Popen(cmd, shell=True)
    return p


def StartFFMPEGStream(chat_video):
    args = "ffmpeg -nostats -loglevel quiet -re -i " + "\"" + chat_video + "\"" + " -r 30 \
            -vf scale=1920:1080 -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0"
    sub.Popen(args, shell = True, stdin = open(os.devnull))


def KillFFMPEGStream():
    os.system("pkill -9 -f ffmpeg")


def StartChromium(create_log, chromium_build, webrtc_app):
    args = chromium_builds_folder + chromium_build + "/chrome --disable-session-crashed-bubbles --disable-infobars --no-sandbox " + webrtc_app
    if(create_log):
        log = open('chromium_log', 'w')
        sub.Popen(args, env = headless_env, shell = True, stdout=log, stderr=log)
    else:
        devnull = open(os.devnull,'wb')
        sub.Popen(args, env = headless_env, shell = True, stdout=devnull, stderr=devnull)


def KillChromium(sample, log_created):
    os.system("pkill -SIGINT -f chrome")
    if(log_created):
        os.system("mv chromium_log " + "\"" + sample + "\"" + "_chromium_log")

def StartStegozoa():
    log = open('stegozoa_log', 'w')
    args = "python3 " + stegozoa_src_folder_location + "stegozoaClient.py 1"
    sub.Popen(args, shell = True, cwd = stegozoa_src_folder_location, stdout=log, stderr=log)

def KillStegozoa(sample, log_created):
    os.system("pkill -SIGINT -f stegozoaClient")
    if(log_created):
        os.system("mv stegozoa_log " + "\"" + sample + "\"" + "_stegozoa_log")

def StegozoaPingTest(create_log):
    args = "python3 " + stegozoa_test_folder_location + "pingSendTest.py"
    if(create_log):
        log = open('ping_log', 'w')
        sub.Popen(args, shell = True, stdout=log, stderr=log)
    else:
        devnull = open(os.devnull, 'wb')
        sub.Popen(args, shell = True, stdout=devnull, stderr=devnull)

def SaveStegozoaPingResult(sample, log_created):
    os.system("pkill -SIGINT -f pingSendTest")
    if(log_created):
        os.system("mv ping_log " + "\"" + sample + "\"" + "_ping_log")


def StegozoaDownloadTest(create_log):
    args = "python3 " + stegozoa_test_folder_location + "downloadTest.py"
    if(create_log):
        log = open('download_log', 'w')
        sub.Popen(args, shell = True, stdout=log, stderr=log)
    else:
        devnull = open(os.devnull, 'wb')
        sub.Popen(args, shell = True, stdout=devnull, stderr=devnull)

def SaveStegozoaDownloadResult(sample, log_created):
    os.system("pkill -SIGINT -f downloadTest")
    if(log_created):
        os.system("mv download_log " + "\"" + sample + "\"" + "_download_log")




def ImpairNetworkOperation(network_condition):
    if(network_condition[0] is not None):
        if(len(network_condition) == 1):
            os.system("sudo tc qdisc add dev " + NETWORK_INTERFACE + " root " + network_condition[0])
            print "[P] Setting network conditions: tc qdisc add dev " + NETWORK_INTERFACE + " root " + network_condition[0]
        elif(len(network_condition) == 3):
            #Combine netem with htb
            os.system("sudo tc qdisc add dev " + NETWORK_INTERFACE + " root handle 1: " + network_condition[0])
            print "[P] Setting network conditions: tc qdisc add dev " + NETWORK_INTERFACE + " root handle 1: " + network_condition[0]

            os.system("sudo tc class add dev " + NETWORK_INTERFACE + " parent 1:1 classid 1:12 " + network_condition[1])
            print "[P] Setting network conditions: tc qdisc add dev " + NETWORK_INTERFACE + " parent 1:1 classid 1:12 " + network_condition[1]

            os.system("sudo tc qdisc add dev " + NETWORK_INTERFACE + " parent 1:12 " + network_condition[2])
            print "[P] Setting network conditions: tc qdisc add dev " + NETWORK_INTERFACE + " parent 1:12 " + network_condition[2]
    else:
        print "[P] Setting network conditions: None"

def ResumeNetworkOperation():
    os.system("sudo tc qdisc del dev " + NETWORK_INTERFACE + " root")

def routeMiddlebox():
    PrintColored("Applying routing through middlebox", 'red')
    os.system("sudo route add default gw " + MIDDLEBOX_IP)

def delRoute():
    PrintColored("Removing routing through middlebox", 'red')
    os.system("sudo route del default")



def SampleRegularExact(sample_index, config, baseline, network_condition, chromium_build):
    regular_cap_folder = config

    random.seed(a=1)
    sample_list = os.listdir(video_folder + baseline + "/")
    sample_list.sort()
    random.shuffle(sample_list)

    #Create folder for regular traffic
    if not os.path.exists(regular_cap_folder):
        os.makedirs(regular_cap_folder)

    if not os.path.exists(regular_cap_folder + baseline):
        os.makedirs(regular_cap_folder + baseline)

    if not os.path.exists(regular_cap_folder + baseline + "/" + network_condition[1]):
        os.makedirs(regular_cap_folder + baseline + "/" + network_condition[1])

    chat_sample = sample_list[sample_index]

        
    if(chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246) + "_chromium_log" not in os.listdir(regular_cap_folder + baseline + "/" + network_condition[1])):
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print "Network conditions: " + network_condition[1]
        ImpairNetworkOperation(network_condition[0])
        
        if(len(network_condition[0]) == 1):
            RESTCall("impairNetworkOperationWithOpenServer", network_condition[0][0])
        elif(len(network_condition[0]) == 3):
            RESTCall("impairNetworkOperationWithOpenServer", network_condition[0][0] + "|" + network_condition[0][1] + "|" + network_condition[0][2])

        print "Chromium build - " + chromium_build

        #Start FFMPEG in sync
        s = sched.scheduler(time.time, time.sleep)
        now = time.time()
        start_remote_ffmpeg = now + sync_early
        start_local_ffmpeg = now + sync_late
        
        print "[P] Starting remote FFMPEG stream at: " + str(start_remote_ffmpeg)
        RESTCall("startFFMPEGSync", str(start_remote_ffmpeg) + ",|," + video_folder + baseline + "/" + chat_sample)
        
        print "[P] Wait to start local FFMPEG stream at: " + str(start_local_ffmpeg)
        args = (video_folder + baseline + "/" + chat_sample,)
        s.enterabs(start_local_ffmpeg, 0, StartFFMPEGStream, args)                  
        s.run()
        print "[P] Starting local FFMPEG stream: " + baseline + "/" + chat_sample + " - index " + str(sample_index % 246)  
        
        #Start Chromium in sync
        now = time.time()
        start_remote_chromium = now + sync_early
        start_local_chromium = now + sync_late
        
        webrtc_app = WEBRTC_APPLICATION
        if("appr.tc" in WEBRTC_APPLICATION):
            label = network_condition[1].replace(".","-")
            webrtc_app = WEBRTC_APPLICATION + "_reg_" + label + "_" + str(sample_index % 246)

        print "[P] Starting Remote Chromium Browser at: " + str(start_remote_chromium)
        print "[P] Starting WebRTC Application: " + webrtc_app
        RESTCall("startChromium", str(start_remote_chromium) + "," + chromium_build + "," + webrtc_app)
        
        print "[P] Wait to start local Chromium Browser at: " + str(start_local_chromium)
        args = (True, chromium_build, webrtc_app)
        s.enterabs(start_local_chromium, 0, StartChromium, args)
        s.run()
        print "[P] Starting local Chromium Browser"
        
        if("appr.tc" in WEBRTC_APPLICATION):
            time.sleep(20)

            print "[P] Performing local automation task"
            automateChromium(webrtc_app, "caller")

            time.sleep(5)

            print "[P] Performing remote automation task"
            RESTCall("automateApp", webrtc_app)

            time.sleep(20)
        elif("whereby" in WEBRTC_APPLICATION):
            time.sleep(20) #Ten seconds were apparently not enough for starting up Chromium

            print "[P] Performing local automation task"
            automateChromium(webrtc_app, "caller")

            print "[P] Performing remote automation task"
            RESTCall("automateApp", webrtc_app)
        
        elif("meet.jit.si" in WEBRTC_APPLICATION):
            time.sleep(20) #Ten seconds were apparently not enough for starting up Chromium

            print "[P] Performing local automation task"
            automateChromium(webrtc_app, "caller")

            print "[P] Performing remote automation task"
            RESTCall("automateApp", webrtc_app)
        
        time.sleep(20) # ping time
        
        #Start Traffic Capture in sync
        now = time.time()
        start_remote_traffic_capture = now + sync_early
        
        print "[P] Starting Remote Traffic Capture at: " + str(start_remote_traffic_capture)
        print "[P] Capturing " + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4] + "_" + str(sample_index % 246) + ".pcap"
        RESTCallMiddlebox("captureTraffic", str(start_remote_traffic_capture) + "," + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246) + "," + regular_cap_folder + baseline + "/" + network_condition[1] + "/" + "," + str(capture_duration))


        #Wait for tcpdump to finish
        print "[P] Waiting for traffic capture to finish..."
        time.sleep(capture_duration + sync_early)

        # Cleanup
        print "[P] Killing FFMPEG stream"
        KillFFMPEGStream()
        print "[P] Killing remote FFMPEG stream"
        RESTCall("killFFMPEG")

        print "[P] Killing Chromium"
        KillChromium(regular_cap_folder + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246), True)

        print "[P] Killing Remote Chromium Browser"
        RESTCall("killChromium")

        time.sleep(2)
    else:
        print "[P] Already sampled " + baseline + "/" + chat_sample

    ResumeNetworkOperation()
    RESTCall("resumeNetworkOperation")


def SampleStegozoaExact(sample_index, config, baseline, network_condition, chromium_build):

    stegozoa_cap_folder = config

    random.seed(a=1)
    sample_list = os.listdir(video_folder + baseline)
    sample_list.sort()
    random.shuffle(sample_list)

    #Create folder for stegozoa traffic
    if not os.path.exists(stegozoa_cap_folder):
        os.makedirs(stegozoa_cap_folder)

    if not os.path.exists(stegozoa_cap_folder + baseline):
        os.makedirs(stegozoa_cap_folder + baseline)

    if not os.path.exists(stegozoa_cap_folder + baseline + "/" + network_condition[1]):
        os.makedirs(stegozoa_cap_folder + baseline + "/" + network_condition[1])

    chat_sample = sample_list[sample_index]

    #Check sample existence by checking whether chromium log is saved
    if(chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246) + "_chromium_log" not in os.listdir(stegozoa_cap_folder + baseline + "/" + network_condition[1])):
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        ImpairNetworkOperation(network_condition[0])
        
        if(len(network_condition[0]) == 1):
            RESTCall("impairNetworkOperationWithOpenServer", network_condition[0][0])
        elif(len(network_condition[0]) == 3):
            RESTCall("impairNetworkOperationWithOpenServer", network_condition[0][0] + "|" + network_condition[0][1] + "|" + network_condition[0][2])

        
        print "Chromium build - " + chromium_build

        #Start Stegozoa
        print "[P] Starting Remote Stegozoa"
        RESTCall("startStegozoa")
        print "[P] Starting Stegozoa"
        StartStegozoa()

        #Start FFMPEG in sync
        s = sched.scheduler(time.time, time.sleep)
        now = time.time()
        start_remote_ffmpeg = now + sync_early
        start_local_ffmpeg = now + sync_late
        
        print "[P] Starting remote FFMPEG stream at: " + str(start_remote_ffmpeg)
        RESTCall("startFFMPEGSync", str(start_remote_ffmpeg) + ",|," + video_folder + baseline + "/" + chat_sample)
        
        print "[P] Wait to start local FFMPEG stream at: " + str(start_local_ffmpeg)
        args = (video_folder + baseline + "/" + chat_sample,)
        s.enterabs(start_local_ffmpeg, 0, StartFFMPEGStream, args)                  
        s.run()
        print "[P] Starting local FFMPEG stream: " + baseline + "/" + chat_sample + " - index " + str(sample_index % 246)  
        
        #Start Chromium in sync
        now = time.time()
        start_remote_chromium = now + sync_early
        start_local_chromium = now + sync_late
        

        webrtc_app = WEBRTC_APPLICATION
        if("appr.tc" in WEBRTC_APPLICATION):
            label = network_condition[1].replace(".","-")
            webrtc_app = WEBRTC_APPLICATION + "_stego_" + label + "_" + str(sample_index % 246)

        print "[P] Starting Remote Chromium Browser at: " + str(start_remote_chromium)
        RESTCall("startChromium", str(start_remote_chromium) + "," + chromium_build + "," + webrtc_app)
        
        print "[P] Wait to start local Chromium Browser at: " + str(start_local_chromium)
        args = (True, chromium_build, webrtc_app)
        s.enterabs(start_local_chromium, 0, StartChromium, args)
        s.run()
        print "[P] Starting local Chromium Browser"
        
        if("appr.tc" in WEBRTC_APPLICATION):
            time.sleep(20)

            print "[P] Performing local automation task"
            automateChromium(webrtc_app, "caller")

            time.sleep(5)

            print "[P] Performing remote automation task"
            RESTCall("automateApp", webrtc_app)

            time.sleep(20)
        elif("whereby" in WEBRTC_APPLICATION):
            time.sleep(20) #Ten seconds were apparently not enough for starting up Chromium

            print "[P] Performing local automation task"
            automateChromium(webrtc_app, "caller")

            print "[P] Performing remote automation task"
            RESTCall("automateApp", webrtc_app)
        elif("meet.jit.si" in WEBRTC_APPLICATION):
            time.sleep(20) #Ten seconds were apparently not enough for starting up Chromium

            print "[P] Performing local automation task"
            automateChromium(webrtc_app, "caller")

            print "[P] Performing remote automation task"
            RESTCall("automateApp", webrtc_app)

        #Ping test first, without traffic capture
        
        print "[P] Performing Ping Test"
        RESTCall("pingTest")
        StegozoaPingTest(True)
        time.sleep(20) # ping time
        SaveStegozoaPingResult(stegozoa_cap_folder + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246), True)
        RESTCall("killPingTest")

        #Start Traffic Capture in sync
        now = time.time()
        start_remote_traffic_capture = now + sync_early
        
        print "[P] Starting Remote Traffic Capture at: " + str(start_remote_traffic_capture)
        print "[P] Capturing " + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4] + "_" + str(sample_index % 246) + ".pcap"
        RESTCallMiddlebox("captureTraffic", str(start_remote_traffic_capture) + "," + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246) + "," + stegozoa_cap_folder + baseline + "/" + network_condition[1] + "/" + "," + str(capture_duration))

        
        #Start Stegozoa data transmission after tcpdump start
        print "[P] Starting Stegozoa data transmission"
        StegozoaDownloadTest(True)
        RESTCall("downloadTest")
        
        #Wait for tcpdump to finish
        print "[P] Waiting for traffic capture to finish..."
        time.sleep(capture_duration + sync_early)

        # Cleanup
        print "[P] Killing FFMPEG stream"
        KillFFMPEGStream()
        print "[P] Killing remote FFMPEG stream"
        RESTCall("killFFMPEG")

        print "[P] Killing Chromium"
        KillChromium(stegozoa_cap_folder + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246), True)

        print "[P] Killing Remote Chromium Browser"
        RESTCall("killChromium")

        print "[P] saving local results for Stegozoa transmission"
        SaveStegozoaDownloadResult(stegozoa_cap_folder + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246), True)

        print "[P] Killing Remote Download Test"
        RESTCall("killDownloadTest")

        print "[P] Killing Stegozoa"
        KillStegozoa(stegozoa_cap_folder + baseline + "/" + network_condition[1] + "/" + chat_sample[:-4].replace(" ", "") + "_" + str(sample_index % 246), True)
        print "[P] Killing Remote Stegozoa instance"
        RESTCall("killStegozoa")
        time.sleep(2)
    else:
        print "[P] Already sampled " + baseline + "/" + chat_sample.replace(" ", "")

    ResumeNetworkOperation()
    RESTCall("resumeNetworkOperation")


if __name__ == "__main__":

    #Sample Regular and Stegozoa flows in an interleaved fashion

    baseline = "Chat"

    chromium_builds = ["no_stegozoa_build", "regular_build"]

    ResumeNetworkOperation()
    RESTCall("resumeNetworkOperation")

    RESTCall("routeMiddlebox")
    routeMiddlebox()

    for network_condition in network_conditions:
        for i in range(0,246):
            SampleRegularExact(0 + i, regular_cap_folder, baseline, network_condition, chromium_builds[0])
            SampleStegozoaExact(246 + i, stegozoa_cap_folder, baseline, network_condition, chromium_builds[1])


    RESTCall("delRoute")
    delRoute()
