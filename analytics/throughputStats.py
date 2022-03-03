import os
import numpy as np
import matplotlib.pyplot as plt


log_folder = "/home/vagrant/SharedFolder/StegozoaCaps/"


def computeThroughput(cap_folder):

    log_list = os.listdir(cap_folder)
    Speed = []

    for log_filename in log_list:

        if not log_filename.__contains__("download_log"):
            continue

        with open(cap_folder + "/" + log_filename, "rt") as logfile:
            lines = logfile.readlines()

            for line in lines:
                words = line.split(" ")

                if len(words) == 2:

                    if words[0] == "Throughput(bits/s):":
                        try:
                            speed = float(words[1]) / 1000
                        except ValueError:
                            break
                        Speed += [speed]

    print(cap_folder + str(":"))
    print("mean:{}, std:{}".format(np.mean(Speed), np.std(Speed)))

    return Speed

def plot(dist, savefile, label):

    fig = plt.figure()
    ax1 = fig.add_subplot(111)


    bp = ax1.boxplot(dist, labels=[label], notch=False, showfliers=False, showmeans=True, meanprops={'markerfacecolor': 'slategray', 'markeredgecolor': 'slategray'})

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

    #ax1.set(ylim=(0,15000))
    #ax1.yaxis.set_ticks(np.arange(0, 15001, 1500))
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
    plt.ylabel('Stegozoa Throughput (kbps)', fontsize=20)

    plt.setp(ax1.get_xticklabels(), fontsize=15)
    plt.setp(ax1.get_yticklabels(), fontsize=15)

    plt.tight_layout()


    fig.savefig(savefile)
    plt.close(fig)


def plot3(dists, savefile, labels):

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    bp = ax1.boxplot(dists, labels=labels, notch=False, showfliers=False, showmeans=True, meanprops={'markerfacecolor': 'slategray', 'markeredgecolor': 'slategray'})

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


    #ax1.set(ylim=(0,15000))
    #ax1.yaxis.set_ticks(np.arange(0, 15001, 1500))
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
    plt.ylabel('Stegozoa Throughput (kbps)', fontsize=20)

    plt.setp(ax1.get_xticklabels(), fontsize=15)
    plt.setp(ax1.get_yticklabels(), fontsize=15)

    plt.tight_layout()


    fig.savefig(savefile)
    plt.close(fig)

            

if __name__ == "__main__":

    baseline = "Chat"

    network_condition = "delay_50"
    stegozoa_cap_folder = log_folder + "StegozoaTraffic" + "/" + baseline + "/" + network_condition
    throughput = computeThroughput(stegozoa_cap_folder)
    #plot(throughput, "Throughput.pdf", "meet.jit.si")
    plot(throughput, "Throughput.pdf", "whereby.com")


    network_conditions = ["delay_50-bw_1500", "delay_50-bw_750", "delay_50-bw_250"]
    labels = ["1500Kbps", "750Kbps", "250Kbps"]
    throughputs = []
    for network_condition in network_conditions:
        stegozoa_cap_folder = log_folder + "StegozoaTraffic" + "/" + baseline + "/" + network_condition
        throughput = computeThroughput(stegozoa_cap_folder)
        throughputs += [throughput]
    plot3(throughputs, "Throughput_bw.pdf", labels)

    network_conditions = ["delay_50-loss_2", "delay_50-loss_5", "delay_50-loss_10"]
    labels = ["2% loss", "5% loss", "10% loss"]
    throughputs = []
    for network_condition in network_conditions:
        stegozoa_cap_folder = log_folder + "StegozoaTraffic" + "/" + baseline + "/" + network_condition
        throughput = computeThroughput(stegozoa_cap_folder)
        throughputs += [throughput]
    plot3(throughputs, "Throughput_loss.pdf", labels)
    
