# Overview

This model was built utilizing ElasticSearch data that is collected on the Odin org of Pulse. The model answers two questions for the Odin team. 

    1. Is there potentially something going on in the information environment regarding a reward offer subject?
    2. What is the pontial cause for the reporting about the particular reward offer subject?

To do this, we needed to understand the behavior of these keywords in Odin Pulse then assess the documents during times when the behavior of those keywords is greater than expected.  

## Utilization
Using this program is relatively simple with a few prerequisites

1. `odin` python analytics tools need to be installed on your machine
2. ElasticSearch credentials are stored locally on your machine where `odin` can load them. (Contact Gabe McBride for further guidance)
3. Airtable credentials are stored where `odin` can load them (Contact Gabe McBride for guidance)
4. The user has trained the clustering portion of the model (Contact Gabe McBride for guidance)

Once all prerequisites are complete, the user can simply run the `rfj_keyword_alerts.py` file and 

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

## How it Works

The model assesses the daily frequency of each keyword in the ElasticSearch query. Days when the frequency is outside the confidence limits of a normal distribution (95%), result in a slack notification to the `rfj_alerts` channel and provide possible causes for the spike in pulse collection.

Once all prerequisites are met, the script will query ElasticSearch data for the most current day as long as the logged data is up-to-date. The script looks at the last day logged and the current date and time, then queries all days in between. If the frequencies for the queried days for each keyword are out of the confidence limits, the result will be a slack message with potential examples for the cause of the spike.  

The script will randomly select a sample of 100 frequencies for each keyword and build the confidence interval. If on the 

## Development

To contribute to this program, identify issues, or help with setup please contact Gabe McBride.  

### Improvements
If you have ideas about improvements please contact Gabe McBride.  

Some potential improvements
1. custom keyword inputs
2. custom slack channel inputs for notifications
