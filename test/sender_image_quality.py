from sender_control import *



# register psnr and ssim values for how long
duration = 45

WEBRTC_APPLICATION = "https://whereby.com/123"
#WEBRTC_APPLICATION = "https://meet.jit.si/12349876"

def CleanFolders():
    os.system("rm writing/* reading/*")

def SampleRegularImage(sample_index, config, baseline, network_condition, chromium_build):
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
        elif("meet.jit.si" in WEBRTC_APPLICATION):
            webrtc_app = WEBRTC_APPLICATION + network_condition[1] + "_reg"
        elif("whereby.com" in WEBRTC_APPLICATION):
            webrtc_app = WEBRTC_APPLICATION

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

            
        #print "[P] Recording Video call"
        #recordVideo(WEBRTC_APPLICATION)
        
        #Wait
        print "[P] Waiting for the " + str(duration) + " seconds to finish..."
        time.sleep(duration)
        
        #print "[P] Stopping recording Video call"
        #stopRecordVideo(WEBRTC_APPLICATION)

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


def SampleStegozoaImage(sample_index, config, baseline, network_condition, chromium_build):

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
        elif("meet.jit.si" in WEBRTC_APPLICATION):
            webrtc_app = WEBRTC_APPLICATION + network_condition[1] + "_stego"
        elif("whereby.com" in WEBRTC_APPLICATION):
            webrtc_app = WEBRTC_APPLICATION

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

            
        #print "[P] Recording Video call"
        #recordVideo(WEBRTC_APPLICATION)

        
        #Start Stegozoa data transmission after tcpdump
        print "[P] Starting Stegozoa data transmission"
        StegozoaDownloadTest(True)
        RESTCall("downloadTest")
        
        #Wait
        print "[P] Waiting for the " + str(duration) + " seconds to finish..."
        time.sleep(duration)
        
        #print "[P] Stopping recording Video call"
        #stopRecordVideo(WEBRTC_APPLICATION)

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
    network_conditions = [[[None], "regular"]]
    
    """
        #Set baseline RTT between VM1 / VM3, vary bandwidth conditions (TC)
        [["htb default 12", "htb rate 1500kbit ceil 1500kbit", "netem delay 25ms"], "delay_50-bw_1500"],
        [["htb default 12",   "htb rate 250kbit ceil 250kbit", "netem delay 25ms"], "delay_50-bw_250"],
        [["htb default 12",   "htb rate 750kbit ceil 750kbit", "netem delay 25ms"], "delay_50-bw_750"],
        
        #Set baseline RTT between VM1 / VM3, vary packet loss conditions
        [["netem delay 25ms loss 2%"], "delay_50-loss_2"],
        [["netem delay 25ms loss 10%"], "delay_50-loss_10"],
        [["netem delay 25ms loss 5%"], "delay_50-loss_5"],

    ]
    """

    baseline = "Chat"

    chromium_builds = ["stats_no_stegozoa", "stats_stegozoa"]

    ResumeNetworkOperation()
    RESTCall("resumeNetworkOperation")

    for network_condition in network_conditions:
        for i in range(0,246):
            SampleRegularImage(0 + i, regular_cap_folder, baseline, network_condition, chromium_builds[0])
            CleanFolders()
            SampleStegozoaImage(246 + i, stegozoa_cap_folder, baseline, network_condition, chromium_builds[1])
            CleanFolders()


