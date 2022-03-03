import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


log_folder = "/home/vagrant/SharedFolder/StegozoaCaps/"

def customFunc(series):
    return series.apply(lambda x: str(len(x)) + x)

def getRes(w, h):
    w = w[2:]
    h = h[2:-1]
    return w + "x" + h

def computePsnrSsim(cap_folder):

    log_list = os.listdir(cap_folder)
    psnrList = []
    ssimList = []

    resDict = {}

    for log_filename in log_list:
        
        if not log_filename.__contains__("chromium_log"):
            continue

        with open(cap_folder + "/" + log_filename, "rt") as logfile:
            lines = logfile.readlines()

            totalPsnr = 0
            totalSsim = 0
            n = 0
            for i in range(1000, len(lines)): # delete first 1000 (video call is not in a stable state at the beginning
                words = lines[i].split(" ")
                if len(words) == 6 and words[0] == "Frame:":
                    try:
                        psnr = float(words[3][:-1])
                        ssim = float(words[5])
                    except:
                        continue
                    if psnr != 100 and ssim != 1:
                        totalPsnr += psnr
                        totalSsim += ssim
                        n += 1

                elif len(words) == 5 and words[1] == "Resolution":
                    try:
                        res = getRes(words[3], words[4])
                    except:
                        continue

                    if res not in resDict:
                        resDict[res] = 1
                    else:
                        resDict[res] += 1

            
            if n > 0:

                psnrList += [totalPsnr / n]
                ssimList += [totalSsim / n]

                
    return psnrList, ssimList, resDict

def plot(stegoDist, regularDist, savefile, ylabel):


    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    bp = ax1.boxplot([stegoDist, regularDist], labels=["Stegozoa", "Regular"], notch=False, showfliers=False, showmeans=True, meanprops={'markerfacecolor': 'slategray', 'markeredgecolor': 'slategray'})


    for box in bp['boxes']:
        # change outline color
        box.set(color="black", linewidth=2)#, edgecolor="black")

    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='black', linewidth=2)

    ## change color and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color='black', linewidth=2)

    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color='red', linewidth=2)

    ## change marker of the arithmetic means
    for mean in bp['means']:
        mean.set(marker='o')


    #if label = "PSNR":
    #    ax1.set(ylim=(30,60))
    #    ax1.yaxis.set_ticks(np.arange(30, 61, 5))
    #else:
    #    ax1.set(ylim=(0.99,1))
    #    ax1.yaxis.set_ticks(np.arange(0.99, 1.01, 0.001))

    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
    plt.ylabel(ylabel, fontsize=20)

    plt.setp(ax1.get_xticklabels(), fontsize=15)
    plt.setp(ax1.get_yticklabels(), fontsize=15)

    plt.tight_layout()
    fig.savefig(savefile)
    plt.close(fig)

def barChart(resDict, savefile):

    fig = plt.figure()

    df = pd.DataFrame(resDict.items(), columns=['res', 'count'])
    df = df.sort_values('res', key=customFunc)
    df = df[df['count'] >= 100]
    total = df['count'].sum()
    df['count'] = (df['count'] / total)
    print(df)
    
    plt.bar(df['res'], df['count'] * 100)
    plt.ylabel("Relative frequency (%)", fontsize=20)
    plt.xlabel("Resolutions", fontsize=20)

    fig.savefig(savefile)
    plt.close(fig)


            

if __name__ == "__main__":

    baseline = "Chat"
    network_condition = "regular.regular"

    regular_cap_folder = log_folder + "RegularTraffic" + "/" + baseline + "/" + network_condition
    stegozoa_cap_folder = log_folder + "StegozoaTraffic" + "/" + baseline + "/" + network_condition

    stegoPsnrs, stegoSsims, stegoRes = computePsnrSsim(stegozoa_cap_folder)
    regularPsnrs, regularSsims, regularRes = computePsnrSsim(regular_cap_folder)


    #plot(stegoPsnrs, regularPsnrs, "PSNR.pdf", "PSNR")
    #plot(stegoSsims, regularSsims, "SSIM.pdf", "SSIM")
    barChart(stegoRes, "stegoRes.pdf")
    barChart(regularRes, "regularRes.pdf")
    
