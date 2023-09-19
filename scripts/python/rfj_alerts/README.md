# Overview

This model was built utilizing ElasticSearch data that is collected on the Odin org of Pulse. The model answers two questions for the Odin team. 

    1. Is there a significant increase in Pulse traffic regarding a reward offer subject?
    2. If there is a significant increase in Pulse traffic regarding a subject, what is the pontial cause for the reporting about the particular reward offer subject?

To do this, we needed to understand the behavior of these keywords in Odin Pulse then assess the documents during times when the behavior of those keywords is greater than expected.  

## Utilization
This program is deployed on a remote machine managed by TSI Data and Engineering. Each time improvements, fixes, and features are added to the `odin` repository and merged into the master branch, a new image of `odin` and relevant scripts are deployed to this machine. 

The main program for rfj alerts runs with the `rfj_keyword_alerts.py` and has a couple external inputs. From scratch, this script will pull the last 100 days of elastic search with keywords of reward offer subjects in multiple languages. The script will then label each document according to any keywords that are present in the document and aggregated the frequency of those labels for each of the 100 days. This creates the `daily_counts.pkl`. From there, a normal distribution of these labels is assessed while the upper and lower limits of the distribution are logged in a dictionary using a 95% confidence with the label as the key (i.e. {'label_1': (lower_n, upper_n), ... 'label_n': (lower_n, upper_n)}). These limits can then be used in future runs of the script. Given a keyword results in a frequency that is greater than the upper limit, the script will utilize the `kmeans_model.pkl` to cluster the documents into two classifications of documents and output and example with links to each document as potential causes for the increase in Pulse traffic for that keyword (reward offer subject).

This script will run on the odin remote machine daily at 4:00 am and provide an output to the `#rfj-alerts` Slack channel, given there is a keyword that produces a spike in Pulse traffic. 

## Model Process
1. Query ElasticSearch data
2. Assess keyword daily frequencies
   1. Above threshold?
      1. Yes
         1. Log keyword frequencies
         2. Apply clustering model
         3. Message slack channel
            1. Provide examples
      2. No
         1. Log keyword frequencies

## Development

To contribute to this program, identify issues, or help with setup please contact Gabe McBride.  

### Improvements
If you have ideas about improvements please contact Gabe McBride.  

