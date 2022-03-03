import sys, os
import subprocess as sub
import time, sched
import random
import threading
import requests

protozoa_folder_location = '/home/vagrant/Protozoa/protozoa/'
chromium_src_folder = "/home/vagrant/Chromium/chromium/src/"
chromium_builds_folder = "/home/vagrant/chromium_builds/"


##############################################################################################################
############################################# Vanilla Variations #############################################
##############################################################################################################

def CompileRegularChromium():
    print "Compiling Regular Chromium"
    cmd = protozoa_folder_location + "patch.sh /home/vagrant/Chromium/chromium/src/third_party/webrtc/ macros_vanilla macros_regular.h hooks protozoa_hooks.cpp"
    p = sub.call(cmd, shell=True, cwd = protozoa_folder_location)

    my_env = os.environ.copy()
    my_env["PATH"] = my_env["PATH"] + ":/home/vagrant/Chromium/depot_tools"
    cmd = "autoninja -C out/quick_build/ chrome"
    p = sub.call(cmd, shell=True, cwd = chromium_src_folder, env=my_env)

    cmd = "cp -T -r out/quick_build/ /home/vagrant/chromium_builds/regular_build"
    p = sub.call(cmd, shell=True, cwd = chromium_src_folder, env=my_env)


def CompileProtozoaFullFrameReplacementChromium():
    print "Compiling Protozoa Full Frame Replacement Chromium"
    cmd = protozoa_folder_location + "patch.sh /home/vagrant/Chromium/chromium/src/third_party/webrtc/ macros_replacement macros_protozoa_full_frame_replacement.h hooks protozoa_hooks.cpp"
    p = sub.call(cmd, shell=True, cwd = protozoa_folder_location)

    my_env = os.environ.copy()
    my_env["PATH"] = my_env["PATH"] + ":/home/vagrant/Chromium/depot_tools"
    cmd = "autoninja -C out/quick_build/ chrome"
    p = sub.call(cmd, shell=True, cwd = chromium_src_folder, env=my_env)

    cmd = "cp -T -r out/quick_build/ /home/vagrant/chromium_builds/protozoaReplacementFullFrame_build"
    p = sub.call(cmd, shell=True, cwd = chromium_src_folder, env=my_env)


def CompileProtozoaFullFrameReplacement_ReadOnReassembly_Chromium():
    print "Compiling Protozoa Full Frame Replacement _ReadOnReassembly_ Chromium"
    cmd = protozoa_folder_location + "patch.sh /home/vagrant/Chromium/chromium/src/third_party/webrtc/ macros_replacement macros_protozoa_full_frame_replacement_on_reassembly.h hooks protozoa_hooks.cpp"
    p = sub.call(cmd, shell=True, cwd = protozoa_folder_location)

    my_env = os.environ.copy()
    my_env["PATH"] = my_env["PATH"] + ":/home/vagrant/Chromium/depot_tools"
    cmd = "autoninja -C out/quick_build/ chrome"
    p = sub.call(cmd, shell=True, cwd = chromium_src_folder, env=my_env)

    cmd = "cp -T -r out/quick_build/ /home/vagrant/chromium_builds/protozoaReplacementFullFrame_ReadOnReassembly_build"
    p = sub.call(cmd, shell=True, cwd = chromium_src_folder, env=my_env)


def CompileChromiumVersions(chromium_builds_folder):
    if not os.path.exists(chromium_builds_folder):
        os.makedirs(chromium_builds_folder)

    #CompileRegularChromium()
    CompileProtozoaFullFrameReplacementChromium()
    #CompileProtozoaFullFrameReplacement_ReadOnReassembly_Chromium()
    


if __name__ == "__main__":
    
    CompileChromiumVersions(chromium_builds_folder)
