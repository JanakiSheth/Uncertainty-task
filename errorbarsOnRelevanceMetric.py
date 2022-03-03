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

def gaussian(x, mean, sigma):
    return np.exp(-(x-mean)**2/(2*sigma**2))

def Tones3dgrid(latentTones, sigma):    
    
    input_array_0 = np.expand_dims(gaussian(log_freq_percept, latentTones[0], sigma), axis = 1)
    input_array_1 = np.expand_dims(gaussian(log_freq_percept, latentTones[1], sigma), axis = 1)
    input_array_2 = np.expand_dims(gaussian(log_freq_percept, latentTones[2], sigma), axis = 1)
    s0 = 1/np.sum(input_array_0); s1 = 1/np.sum(input_array_1); s2 = 1/np.sum(input_array_2)
    input_array_0 *= s0; input_array_1 *= s1; input_array_2 *= s2; 
    
    input_array_mat = np.expand_dims(input_array_0@input_array_1.T,axis=2)@(input_array_2.T) #p(T1,T2..|H)     
    
    return input_array_mat

def posterior_array(freq_input, n_tones, p_back, p_low, log_prior):
    """
    Arguments: 
    freq_input - range of all possible frequencies (percepts?)
    p_back - prob of background
    p_low - prob of low condition
    log_prior - list of prior parameters
    """
    
    log_prior_low_mean = log_prior[0]; log_prior_low_sigma = log_prior[2];
    log_prior_high_mean = log_prior[1]; log_prior_high_sigma = log_prior[2];
    prior_low = gaussian(x=freq_input, mean=log_prior_low_mean, sigma=log_prior_low_sigma)
    prior_high = gaussian(x=freq_input, mean=log_prior_high_mean, sigma=log_prior_high_sigma)
    prior_dist_mixed_high = p_back*(1/len(freq_input)) + (1-p_back)*prior_high \
    #mixture model with p(T|B) = 1/no. of possible freqs
    prior_dist_mixed_high /= prior_dist_mixed_high.sum() #normalizing
    prior_dist_mixed_high = np.expand_dims(prior_dist_mixed_high, axis = 1)
    prior_dist_mixed_low = p_back*(1/len(freq_input)) + (1-p_back)*prior_low \
    #mixture model with p(T|B) = 1/no. of possible freqs
    prior_dist_mixed_low /= prior_dist_mixed_low.sum() #normalizing
    prior_dist_mixed_low = np.expand_dims(prior_dist_mixed_low, axis = 1)
        
    if n_tones == 3:
        prior_tones_low = np.expand_dims(prior_dist_mixed_low@np.transpose\
                                         (prior_dist_mixed_low),axis=2)@np.transpose(prior_dist_mixed_low) \
        #p(T1,T2..|L) 
        prior_tones_high = np.expand_dims(prior_dist_mixed_high@np.transpose\
                                          (prior_dist_mixed_high),axis=2)@np.transpose(prior_dist_mixed_high) \
        #p(T1,T2..|H) 
    elif n_tones == 1:
        prior_tones_low = prior_dist_mixed_low
        prior_tones_high = prior_dist_mixed_high
        
    normalizer = (1-p_low)*prior_tones_high + p_low*prior_tones_low #p(H)*p(T1,T2..|H) + p(L)*p(T1,T2..|L)
    posterior = prior_tones_high*(1-p_low)/normalizer
    # posterior /= np.sum(posterior)
    
    return prior_dist_mixed_high, prior_dist_mixed_low, prior_tones_high, prior_tones_low, normalizer, posterior                     
def posteriorAgainstPercept(expt_Params):
    [_,_,mle_LikelihoodLatentTonegivenHigh,
    mle_LikelihoodLatentTonegivenLow,_,mle_posterior] = posterior_array(freq_input=log_freq_percept,
                                                                        n_tones=3,p_back=expt_Params[4],
                                                                        p_low=expt_Params[5],
                                                                        log_prior=expt_Params[:3]) 
    
    
    mle_LikelihoodPerceptgivenHigh = np.zeros((len(log_freq_percept),
                                               len(log_freq_percept),len(log_freq_percept)))
    mle_LikelihoodPerceptgivenLow = np.zeros((len(log_freq_percept),
                                              len(log_freq_percept),len(log_freq_percept)))

    for itrue1 in range(len(log_freq_percept)):
        for itrue2 in range(len(log_freq_percept)):
            for itrue3 in range(len(log_freq_percept)):
                mle_probPerceptgivenLatentTones = Tones3dgrid([log_freq_percept[itrue1],
                                                               log_freq_percept[itrue2],
                                                               log_freq_percept[itrue3]],
                                                               sigma=expt_Params[3])
                mle_LikelihoodPerceptgivenHigh \
                += mle_probPerceptgivenLatentTones * mle_LikelihoodLatentTonegivenHigh[itrue1,itrue2,itrue3]
                mle_LikelihoodPerceptgivenLow \
                += mle_probPerceptgivenLatentTones * mle_LikelihoodLatentTonegivenLow[itrue1,itrue2,itrue3]
    mle_probHighgivenPercept = mle_LikelihoodPerceptgivenHigh*(1-expt_Params[5])/\
    (mle_LikelihoodPerceptgivenHigh*(1-expt_Params[5]) + mle_LikelihoodPerceptgivenLow*expt_Params[5])
    return mle_probHighgivenPercept
            
if __name__ == '__main__':
    
    """
    Parameters
    """
    expt_tones = np.arange(90,3000,1) #array of possible true tones
    log_freq_seq_array = np.arange(0.6,4.7,0.1)
    log_freq_percept = np.arange(0.6,4.7,0.1) # array of possible perceptual tones    
        
    """
    Obtaining data for a given subject
    """
    subject = sys.argv[1]
    context = sys.argv[2]
    
    if context == 'no':
        folder = "auditory_categorization_prolific_online_data/preprocess_results/90-3000_100%_logPerceptAndLogLatent_GoFrom-InfToInf/results_from_cluster/resultsProlificData/errorbarsOnRelevanceMetric/"
    elif context == 'low':
        folder = "auditory_categorization_lc_online_data/preprocess_results/results_from_cluster/resultsProlificData/errorbarsOnRelevanceMetric/"
    else:
        folder = "auditory_categorization_Hc_online_data/preprocess_results/results_from_cluster/resultsProlificData/errorbarsOnRelevanceMetric/"
    
    fileRelevance = folder+"relevanceMetric_"+subject+'.txt'
    fileParameters = folder+subject+'.txt'
    
    with open(fileRelevance, 'r') as fr:
        filelinesRelevance = fr.readlines()
    with open(fileParameters, 'r') as fm:
        filelinesMetrics = fm.readlines()
        
    """
    Only read from the cluster files or are we also testing the metric values locally? 
    """
    readOnly = int(sys.argv[3])
    
    if readOnly:
        relevanceMetric = np.zeros((100,))
        for iMetric in range(len(filelinesRelevance)):
            relevanceMetric[iMetric] = float(filelinesRelevance[iMetric].strip('\n'))
            if np.isnan(relevanceMetric[iMetric]):
                print("Bad parameter values for computation of metric:", filelinesMetrics[iMetric])
                
        #print("Relevance metric values",np.sort(relevanceMetric))   
        print("Median relevance metric",np.around(np.quantile(relevanceMetric[~np.isnan(relevanceMetric)],q=0.5),decimals=2))
        print("5th quantile relevance metric",np.around(np.quantile(relevanceMetric[~np.isnan(relevanceMetric)],q=0.05),decimals=2))
        print("95th quantile relevance metric",np.around(np.quantile(relevanceMetric[~np.isnan(relevanceMetric)],q=0.95),decimals=2))
    
    else:
        norm = np.zeros((100,))
        print("Values of relevance metric using parameter sets obtained from the 100 bootstrapped datasets")
        
        for bootstraps in range(len(filelinesMetrics)):
            if filelinesMetrics[bootstraps].startswith('[') and filelinesMetrics[bootstraps].endswith(']\n'):
                lineWithNewLineChar = strip_new_line_char(filelinesMetrics[bootstraps])
                lineElements = lineWithNewLineChar.split(" ")
            params = np.zeros((6,))
            params[0] = float(lineElements[0][1:])
            ecnt = 1
            for element in lineElements[1:]:
                if '.' in element:
                    if element.endswith(']'):
                        params[ecnt] = float(element[:-1])
                    else:
                        params[ecnt] = float(element)
                    ecnt += 1
        
            minMLE_probHighgivenPercept = posteriorAgainstPercept(params)
            tone1_prob_behaviour = np.zeros((len(log_freq_percept)))
            tone2_prob_behaviour = np.zeros((len(log_freq_percept)))
            tone3_prob_behaviour = np.zeros((len(log_freq_percept)))

            for i_tone in range(len(log_freq_percept)):
                tone1_prob_behaviour[i_tone] = np.mean(minMLE_probHighgivenPercept[i_tone,:,:])
                tone2_prob_behaviour[i_tone] = np.mean(minMLE_probHighgivenPercept[:,i_tone,:])
                tone3_prob_behaviour[i_tone] = np.mean(minMLE_probHighgivenPercept[:,:,i_tone])

            posteriorProbabilities = (tone1_prob_behaviour+tone2_prob_behaviour+tone3_prob_behaviour)/3
            posteriorProbabilities = posteriorProbabilities - (posteriorProbabilities[0]+
                                                               posteriorProbabilities[-1])/2
            norm[bootstraps] = (sum(np.abs(posteriorProbabilities[:17]))+
                    sum(np.abs(posteriorProbabilities[-15:])))/sum(np.abs(posteriorProbabilities))

            print(norm[bootstraps])
