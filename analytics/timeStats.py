import os
import numpy as np
import matplotlib.pyplot as plt


log_folder = "/home/vagrant/SharedFolder/StegozoaCaps/"


def computeTimes(cap_folder):

    log_list = os.listdir(cap_folder)
    Embedding = []
    Encoding = []

    for log_filename in log_list:

        if not log_filename.__contains__("chromium_log"):
            continue

        with open(cap_folder + "/" + log_filename, "rt") as logfile:
            lines = logfile.readlines()

            totalEmbeddingTime = 0.0
            totalEncodingTime = 0.0
            nEmbbed = 0
            nEncode = 0
            for i in range(2000, len(lines)): # delete first 2000 (video call is not in a stable state at the beginning
                words = lines[i].split(" ")

                if len(words) >= 7: # both have 7 or more words

                    if words[2] == "embbedding" and len(words) >= 9:
                        try:
                            time = float(words[8][:-1])
                        except ValueError:
                            continue
                        totalEmbeddingTime += time * 1000
                        nEmbbed += 1
                    elif words[2] == "encoding":
                        try:
                            time = float(words[6])
                        except ValueError:
                            continue
                        totalEncodingTime += time * 1000
                        nEncode += 1
            
            if nEmbbed > 0:
                Embedding += [totalEmbeddingTime / nEmbbed]

            if nEncode > 0:
                Encoding += [totalEncodingTime / nEncode]

    print(cap_folder + str(":"))
    print("Embedding: mean:{}, std:{}".format(np.mean(Embedding), np.std(Embedding)))
    print("Encoding: mean:{}, std:{}".format(np.mean(Encoding), np.std(Encoding)))
    return Embedding, Encoding

def plot(stegoDist, regularDist, savefile):


    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    if not regularDist:
        bp = ax1.boxplot(stegoDist, labels=["Stegozoa"], notch=False, showfliers=False, showmeans=True, meanprops={'markerfacecolor': 'slategray', 'markeredgecolor': 'slategray'})
    else:
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


    if not regularDist:
        plt.ylabel('Embedding times (ms)', fontsize=20)
        #ax1.set(ylim=(0, 10))
        #ax1.yaxis.set_ticks(np.arange(0, 11, 5))
    else:
        plt.ylabel('Encoding times (ms)', fontsize=20)
        #ax1.set(ylim=(0, 90))
        #ax1.yaxis.set_ticks(np.arange(0, 91, 5))
    

    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)

    plt.setp(ax1.get_xticklabels(), fontsize=15)
    plt.setp(ax1.get_yticklabels(), fontsize=15)

    plt.tight_layout()


    fig.savefig(savefile)
    plt.close(fig)


            

if __name__ == "__main__":

    baseline = "Chat"
    network_condition = "delay_50"

    regular_cap_folder = log_folder + "RegularTraffic" + "/" + baseline + "/" + network_condition
    stegozoa_cap_folder = log_folder + "StegozoaTraffic" + "/" + baseline + "/" + network_condition

    stegoEmbedding, stegoEncoding = computeTimes(stegozoa_cap_folder)
    _, regularEncoding = computeTimes(regular_cap_folder)


    plot(stegoEncoding, regularEncoding, "EncodingTimes.pdf")
    plot(stegoEmbedding, [], "EmbeddingTimes.pdf")

    
