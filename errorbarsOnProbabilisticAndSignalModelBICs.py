import sys
import os, glob
import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.optimize import minimize
import math

def strip_new_line_char(string):
    ""
    if "\n" in string:
        return string[:-1]
    return string
           
def bestFitParametersProbabilistic(folder,subject,sensoryStd):
    subjectArray = np.zeros((100,7))
    for iterations in range(1,101):
        file_dev = folder+'results_'+subject+'_'+str(iterations)+'.txt'
        with open(file_dev, 'r') as f:
            filelines = f.readlines()
        fileArray = np.zeros((1,7))
        iline = 0
        while iline < len(filelines):
            if filelines[iline].startswith('[') and filelines[iline].endswith(']\n'):
                lineWithNewLineChar = strip_new_line_char(filelines[iline])
                lineElements = lineWithNewLineChar.split(",")
                temp = np.zeros((1,7))
                temp[:,6] = float(lineElements[6][:-1])
                temp[:,5] = float(lineElements[5][:-2])
                temp[:,4] = float(lineElements[4][:])
                temp[:,3] = float(lineElements[3][:])
                temp[:,2] = float(lineElements[2][:])
                temp[:,1] = float(lineElements[1][:])
                temp[:,0] = float(lineElements[0][8:])
                fileArray = np.append(fileArray,temp,axis=0)
                iline += 1
            else:
                line1WithNewLineChar = strip_new_line_char(filelines[iline])
                lineElementsOfFirstLine = line1WithNewLineChar.split(",")
                line2WithNewLineChar = strip_new_line_char(filelines[iline+1])
                lineElementsOfSecondLine = line2WithNewLineChar.split(",")
                lineElements = lineElementsOfFirstLine[:-1] + lineElementsOfSecondLine
                temp = np.zeros((1,7))
                temp[:,6] = float(lineElements[6][:-1])
                temp[:,5] = float(lineElements[5][:-2])
                temp[:,4] = float(lineElements[4][:])
                temp[:,3] = float(lineElements[3][:])
                temp[:,2] = float(lineElements[2][:])
                temp[:,1] = float(lineElements[1][:])
                temp[:,0] = float(lineElements[0][8:])
                fileArray = np.append(fileArray,temp,axis=0)
                iline += 2 

        fileArraySSConstrained_upperlimit = fileArray[fileArray[:,3]<sensoryStd+0.02]
        fileArraySSConstrained_lowerlimit = fileArraySSConstrained_upperlimit[fileArraySSConstrained_upperlimit[:,3]>sensoryStd-0.02]
        subjectArray[iterations-1,:] = fileArraySSConstrained_lowerlimit[np.argmin(fileArraySSConstrained_lowerlimit[:,-1])]
    return subjectArray

def bestFitParametersSignal(folder,subject,sensoryStd):
    subjectArray = np.zeros((100,6))
    for iterations in range(1,101):
        file_dev = folder+'results_'+subject+'_'+str(iterations)+'.txt'
        with open(file_dev, 'r') as f:
            filelines = f.readlines()
        fileArray = np.zeros((1,6))
        iline = 0
        while iline < len(filelines):
            if filelines[iline].startswith('[') and filelines[iline].endswith(']\n'):
                lineWithNewLineChar = strip_new_line_char(filelines[iline])
                lineElements = lineWithNewLineChar.split(",")
                temp = np.zeros((1,6))
                temp[:,5] = float(lineElements[5][:-1])
                temp[:,4] = float(lineElements[4][:-2])
                temp[:,3] = float(lineElements[3][:])
                temp[:,2] = float(lineElements[2][:])
                temp[:,1] = float(lineElements[1][:])
                temp[:,0] = float(lineElements[0][8:])
                fileArray = np.append(fileArray,temp,axis=0)
                iline += 1
            else:
                line1WithNewLineChar = strip_new_line_char(filelines[iline])
                lineElementsOfFirstLine = line1WithNewLineChar.split(",")
                line2WithNewLineChar = strip_new_line_char(filelines[iline+1])
                lineElementsOfSecondLine = line2WithNewLineChar.split(",")
                lineElements = lineElementsOfFirstLine[:-1] + lineElementsOfSecondLine
                temp = np.zeros((1,6))
                temp[:,5] = float(lineElements[5][:-1])
                temp[:,4] = float(lineElements[4][:-2])
                temp[:,3] = float(lineElements[3][:])
                temp[:,2] = float(lineElements[2][:])
                temp[:,1] = float(lineElements[1][:])
                temp[:,0] = float(lineElements[0][8:])
                fileArray = np.append(fileArray,temp,axis=0)
                iline += 2 

        fileArraySSConstrained_upperlimit = fileArray[fileArray[:,3]<sensoryStd+0.02]
        fileArraySSConstrained_lowerlimit = fileArraySSConstrained_upperlimit[fileArraySSConstrained_upperlimit[:,3]>sensoryStd-0.02]
        subjectArray[iterations-1,:] = fileArraySSConstrained_lowerlimit[np.argmin(fileArraySSConstrained_lowerlimit[:,-1])]
    return subjectArray
            
if __name__ == '__main__':    
        
    """
    Obtaining data for a given subject
    """
    modelType = sys.argv[1]
    folder = sys.argv[2]
    context = sys.argv[3]
    subject = sys.argv[4]
    sensoryStd = float(sys.argv[5])
    
    """
    Errorbars on specific metrics based on the context being studied
    """
    if modelType == 'probabilistic':
        subjectArray = bestFitParametersProbabilistic(folder, subject, sensoryStd)
    elif modelType == 'signal':
        subjectArray = bestFitParametersSignal(folder, subject, sensoryStd)
        
    print("Mean",np.around(np.mean(subjectArray[:],axis=0),decimals=2))
    print("Std",np.around(np.std(subjectArray[:],axis=0),decimals=2))
    if context == 'no':
        print("Median pback",np.around(np.quantile(subjectArray[:,4],q=0.5),decimals=2))
        print("5th quantile pback",np.around(np.quantile(subjectArray[:,4],q=0.05),decimals=2))
        print("95th quantile pback",np.around(np.quantile(subjectArray[:,4],q=0.95),decimals=2))
    else:
        print("Median plow",np.around(np.quantile(subjectArray[:,5],q=0.5),decimals=2))
        print("5th quantile plow",np.around(np.quantile(subjectArray[:,5],q=0.05),decimals=2))
        print("95th quantile plow",np.around(np.quantile(subjectArray[:,5],q=0.95),decimals=2))
    print("Median LL",np.around(np.quantile(subjectArray[:,-1]*6/6,q=0.5),decimals=2))
    print("5th quantile LL",np.around(np.quantile(subjectArray[:,-1]*6/6,q=0.05),decimals=2))
    print("95th quantile LL",np.around(np.quantile(subjectArray[:,-1]*6/6,q=0.95),decimals=2))
    
    
