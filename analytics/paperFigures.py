#!/usr/bin/env python
import subprocess
import socket
import os
import math
import csv
import numpy as np
import sys
from termcolor import colored

import matplotlib
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica']

colors = ["slategray",  "lightskyblue", "sandybrown" ,"darkseagreen", "palevioletred", "lightsteelblue", "salmon"]




def PerturbationsAUCPerProfile():

    dataset = "StegozoaCaps"
    
    perturbation_configs = [
        [
        "delay_50-bw_1500/" + "RegularTraffic-StegozoaTraffic/",
        "delay_50-bw_750/" + "RegularTraffic-StegozoaTraffic/",
        "delay_50-bw_250/" + "RegularTraffic-StegozoaTraffic/"],
        [
        "delay_50-loss_2/" + "RegularTraffic-StegozoaTraffic/",
        "delay_50-loss_5/" + "RegularTraffic-StegozoaTraffic/",
        "delay_50-loss_10/" + "RegularTraffic-StegozoaTraffic/"],
        [
        "delay_50/" + "RegularTraffic-StegozoaTraffic/"]
    ]
        

    feature_sets = [
        "PL_0_30_246",
        "Stats_0_30_246"
    ]


    for videoProfile in os.listdir("classificationData/" + dataset):
        if (".DS_Store" in videoProfile):
            continue
        for feature_set in feature_sets:

            for perturbation_config in perturbation_configs:
            
                fig = plt.figure(figsize=[6.4, 5.2])
                ax1 = fig.add_subplot(111)
                

                for n, cfg in enumerate(perturbation_config):
                
                    sensitivity = np.load("classificationData/" + dataset + "/" + videoProfile + "/" + cfg + feature_set + "/ROC_10CV_XGBoost_Sensitivity.npy")
                    specificity = np.load("classificationData/" + dataset + "/" + videoProfile + "/" + cfg + feature_set + "/ROC_10CV_XGBoost_Specificity.npy")

                    auc = np.trapz(sensitivity, specificity)
                    print "stats AUC " + cfg + ": " + str(auc)

                    label_text = "AUC"

                    if(cfg.split("/")[0] == "delay_50-bw_1500"):
                        label_text = "bw 1500Kbps " + ' - AUC = %0.2f' % (auc)
                    elif(cfg.split("/")[0] == "delay_50-bw_750"):
                        label_text = "bw 750Kbps " + ' - AUC = %0.2f' % (auc)
                    elif(cfg.split("/")[0] == "delay_50-bw_250"):
                        label_text = "bw 250Kbps " + ' - AUC = %0.2f' % (auc)

                    elif(cfg.split("/")[0] == "delay_50-loss_2"):
                        label_text = "loss 2% " + ' - AUC = %0.2f' % (auc)
                    elif(cfg.split("/")[0] == "delay_50-loss_5"):
                        label_text = "loss 5% " + ' - AUC = %0.2f' % (auc)
                    elif(cfg.split("/")[0] == "delay_50-loss_10"):
                        label_text = "loss 10% " + ' - AUC = %0.2f' % (auc)

                    elif(cfg.split("/")[0] == "delay_50"):
                        label_text = "RTT 50ms " + ' - AUC = %0.2f' % (auc)


                    ax1.plot(specificity, sensitivity, lw=6, color=colors[n], label = label_text)

                ax1.plot([0, 1], [0, 1], 'k--', lw=2, color="0.0", label = 'Random Guess')
                ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
                ax1.spines['right'].set_visible(False)
                ax1.spines['top'].set_visible(False)
                plt.xlabel('False Positive Rate', fontsize=24)
                plt.ylabel('True Positive Rate', fontsize=24)
                plt.legend(loc='lower right', frameon=False, handlelength=1.0, fontsize=14)

                plt.setp(ax1.get_xticklabels(), fontsize=20)
                plt.setp(ax1.get_yticklabels(), fontsize=20)
                ax1.set(xlim=(0, 1), ylim=(0.0, 1))
                

                if not os.path.exists("Figures/PerturbationsAUC/" + dataset + "/" + videoProfile):
                    os.makedirs("Figures/PerturbationsAUC/" + dataset + "/" + videoProfile)
                

                if(cfg.split("/")[0] == "delay_50"):
                    perturbation = "latency"

                if(cfg.split("/")[0] == "delay_50-bw_1500" or cfg.split("/")[0] == "delay_50-bw_750" or cfg.split("/")[0] == "delay_50-bw_250"):
                    perturbation = "bandwidth"
                
                if(cfg.split("/")[0] == "delay_50-loss_2" or cfg.split("/")[0] == "delay_50-loss_5" or cfg.split("/")[0] == "delay_50-loss_10"):
                    perturbation = "loss"


                plt.tight_layout()
                fig.savefig("Figures/PerturbationsAUC/" + dataset + "/" + videoProfile + "/" + perturbation + "_" + feature_set + "_ROC_plot.pdf")   # save the figure to file
                plt.close(fig)



def PerturbationsAUCPerAlpha():

    dataset = "StegozoaCaps"
    

    feature_sets = [
        "PL_0_30_246",
        "Stats_0_30_246"
    ]


    for videoProfile in os.listdir("classificationData/" + dataset):
        if (".DS_Store" in videoProfile):
            continue
        for feature_set in feature_sets:

            
           fig = plt.figure()
           ax1 = fig.add_subplot(111)
                

           for n, a in enumerate([4, 2, 1]):
            
                cfg = "delay_50/" + "RegularTraffic-StegozoaTraffic/"
                sensitivity = np.load("width" + str(a) + "Data/" + dataset + "/" + videoProfile + "/" + cfg + feature_set + "/ROC_10CV_XGBoost_Sensitivity.npy")
                specificity = np.load("width" + str(a) + "Data/" + dataset + "/" + videoProfile + "/" + cfg + feature_set + "/ROC_10CV_XGBoost_Specificity.npy")

                auc = np.trapz(sensitivity, specificity)
                print "stats AUC " + cfg + ": " + str(auc)

                label_text = "AUC"
                label_text = '$\\alpha=' + str(1.0 / a) + '$ - AUC = %0.2f' % (auc)



                ax1.plot(specificity, sensitivity, lw=6, color=colors[n], label = label_text)

           ax1.plot([0, 1], [0, 1], 'k--', lw=2, color="0.0", label = 'Random Guess')
           ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
           ax1.spines['right'].set_visible(False)
           ax1.spines['top'].set_visible(False)
           plt.xlabel('False Positive Rate', fontsize=24)
           plt.ylabel('True Positive Rate', fontsize=24)
           plt.legend(loc='lower right', frameon=False, handlelength=1.0, fontsize=14)

           plt.setp(ax1.get_xticklabels(), fontsize=20)
           plt.setp(ax1.get_yticklabels(), fontsize=20)
           ax1.set(xlim=(0, 1), ylim=(0.0, 1))
            

           if not os.path.exists("Figures/PerturbationsAUC/" + dataset + "/" + videoProfile):
               os.makedirs("Figures/PerturbationsAUC/" + dataset + "/" + videoProfile)
            
           perturbation = "none"


           plt.tight_layout()
           fig.savefig("Figures/PerturbationsAUC/" + dataset + "/" + videoProfile + "/" + perturbation + "_" + feature_set + "_ROC_plot.pdf")   # save the figure to file
           plt.close(fig)



def SteganalysisAlpha():

    extractor = "superb"
    app = "whereby"

    fig = plt.figure()#figsize=[5.4, 5.4])
    ax1 = fig.add_subplot(111)

    for n, a in enumerate([4, 2, 1]):
            

        sensitivity = np.load(app + str(a) + "/" + extractor + "/ROC_10CV_XGBoost_Sensitivity.npy")
        specificity = np.load(app + str(a) + "/" + extractor + "/ROC_10CV_XGBoost_Specificity.npy")

        auc = np.trapz(sensitivity, specificity)
        print "stats AUC: " + str(auc)

        label_text = '$\\alpha=' + str(1.0 / a) + '$ - AUC = %0.2f' % (auc)

        ax1.plot(specificity, sensitivity, lw=6, color=colors[n], label = label_text)

    ax1.plot([0, 1], [0, 1], 'k--', lw=2, color="0.0", label = 'Random Guess')
    ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.xlabel('False Positive Rate', fontsize=24)
    plt.ylabel('True Positive Rate', fontsize=24)
    plt.legend(loc='lower right', frameon=False, handlelength=1.0, fontsize=14)

    plt.setp(ax1.get_xticklabels(), fontsize=20)
    plt.setp(ax1.get_yticklabels(), fontsize=20)
    ax1.set(xlim=(0, 1), ylim=(0.0, 1))
    plt.tight_layout()
    
    fig.savefig(extractor + "Steganalysis.pdf")   # save the figure to file
    plt.close(fig)


def SteganalysisPerturbations():

    extractor = "superb"

    fig = plt.figure()#figsize=[5.4, 5.4])
    ax1 = fig.add_subplot(111)

    for n, a in enumerate(["bw_1500", "bw_750", "bw_250", "loss_2", "loss_5", "loss_10"]):
            

        sensitivity = np.load(a + "/" + extractor + "/ROC_10CV_XGBoost_Sensitivity.npy")
        specificity = np.load(a + "/" + extractor + "/ROC_10CV_XGBoost_Specificity.npy")

        auc = np.trapz(sensitivity, specificity)
        print "stats AUC: " + str(auc)

        if(a == "bw_1500"):
            label_text = "bw 1500Kbps " + ' - AUC = %0.2f' % (auc)
        elif(a == "bw_750"):
            label_text = "bw 750Kbps " + ' - AUC = %0.2f' % (auc)
        elif(a == "bw_250"):
            label_text = "bw 250Kbps " + ' - AUC = %0.2f' % (auc)

        elif(a == "loss_2"):
            label_text = "loss 2% " + ' - AUC = %0.2f' % (auc)
        elif(a == "loss_5"):
            label_text = "loss 5% " + ' - AUC = %0.2f' % (auc)
        elif(a == "loss_10"):
            label_text = "loss 10% " + ' - AUC = %0.2f' % (auc)


        ax1.plot(specificity, sensitivity, lw=6, color=colors[n], label = label_text)

    ax1.plot([0, 1], [0, 1], 'k--', lw=2, color="0.0", label = 'Random Guess')
    ax1.yaxis.grid(color='grey', linestyle='dotted', lw=0.2)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.xlabel('False Positive Rate', fontsize=20)
    plt.ylabel('True Positive Rate', fontsize=20)
    plt.legend(loc='lower right', frameon=False, handlelength=1.0, fontsize=14)

    plt.setp(ax1.get_xticklabels(), fontsize=20)
    plt.setp(ax1.get_yticklabels(), fontsize=20)
    ax1.set(xlim=(0, 1), ylim=(0.0, 1))
    plt.tight_layout()
    
    fig.savefig(extractor + "Steganalysis.pdf")   # save the figure to file
    plt.close(fig)






if __name__ == "__main__":
    #PerturbationsAUCPerProfile()

    PerturbationsAUCPerAlpha()
    #SteganalysisAlpha()
    #SteganalysisPerturbations()
