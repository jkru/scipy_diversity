#!/usr/bin/env python

import sys
import argparse
import math
import scipy.special
import pandas as pd

import scipy_conf_parsers
import name_class

# CZW: 2017-06-20 problems with the parsers:
#  2009  unremoved affiliations
#  2012  mis-class due to (ln, fn) arrangement
#  2013  incomplete due to (name, name, name) arrangement
# CZW: 2017-06-25 todo:
#  - Update name_check.author_check to do a better job on 2009/2012/2013 name splits
#    - This update should do that. It seems to work better on (ln, fn) ordering, without
#      harm to other years where that isn't an issue.  Seems to work for all years.
#  - Add additional author weightings for statistics.  Currently uses only first authors


# Pull out the year to consider.
parser = argparse.ArgumentParser()
parser.add_argument('year', type=int)
args = parser.parse_args()

# Set things up
P_female_expect = 0.24 # This is likely not correct.  
talks = list()

# Parse the given year

if args.year is not None:
    year = args.year

    talks += scipy_conf_parsers.defined_content(year)
    if year in scipy_conf_parsers.urls:
        for url in scipy_conf_parsers.urls[year]:
            if url != "":
                if year == 2017 or year == 2016:
                    talks += scipy_conf_parsers.p2017(url,1)
                elif year == 2015:
                    talks += scipy_conf_parsers.p2015(url,0)
                elif year == 2014:
                    talks += scipy_conf_parsers.p2014(url)
                elif year == 2013 or year == 2012:
                    talks += scipy_conf_parsers.p2013(url)
                elif year == 2011:
                    talks += scipy_conf_parsers.p2011(url,'inner-content')
                elif year == 2010:
                    talks += scipy_conf_parsers.p2011(url,'content')
                elif year == 2009 or year == 2008:
                    talks += scipy_conf_parsers.p2009(url,'section')

else:
    for year in scipy_conf_parsers.urls.keys:
        talks += scipy_conf_parsers.defined_content(year) 
        for url in scipy_conf_parsers.urls[year]:
            if url != "":
                if year == 2017 or year == 2016:
                    talks += scipy_conf_parsers.p2017(url,1)
                elif year == 2015:
                    talks += scipy_conf_parsers.p2015(url,0)
                elif year == 2014:
                    talks += scipy_conf_parsers.p2014(url)
                elif year == 2013 or year == 2012:
                    talks += scipy_conf_parsers.p2013(url)
                elif year == 2011:
                    talks += scipy_conf_parsers.p2011(url,'inner-content')
                elif year == 2010:
                    talks += scipy_conf_parsers.p2011(url,'content')
                elif year == 2009 or year == 2008:
                    talks += scipy_conf_parsers.p2009(url,'section')

# Generate a dataframe from the list of talks:
talk_df = pd.DataFrame();

for talk in talks:
    authors = name_class.author_class(author)
    for author_index in range(0,len(authors)):

        talk_tmp = pd.DataFrame({'title' : talk[0], 'author' : authors[author_index][0], \
                                 'gender' : authors[author_index][1], 'author_order' : author_index, \
                                 'talk_type' : talk[2] }, index = [0])
        talk_df = talk_df.append(talk_tmp, ignore_index = True)

#print((talk_df.to_string()).encode('utf-8'))

# Do a pass on statistics:
# Count number of talks from each gender:
(N_talks, N_female, N_male, N_unclass) = (0,0,0,0)
for talk in talks:
    title,author,talk_type,talk_source = talk
    # returns list of (name, gender, fraction)
    authors = name_class.author_class(author)
    
    if authors[0][1] == "F":
        N_female += 1
        N_talks  += 1
    elif authors[0][1] == "M":
        N_male  += 1
        N_talks += 1
    else:
        N_unclass += 1

    print("%s@%s@%s@%s@%s" % (talk[0], talk[1], authors[0][1], talk[2], talk[3]))
    
# Methodology following:
# http://www.laurenbacon.com/how-likely-is-an-all-male-speakers-list-statistically/
    
P_female_frac = 0
for i in range(0,N_female):
    dP = scipy.special.binom(N_talks, i) * P_female_expect**i * \
         (1 - P_female_expect)**(N_talks - i)
    P_female_frac += dP
    
N_female_expect = math.ceil(P_female_expect * N_talks)

P_female_overrep = 0
for i in range(int(N_female_expect),N_talks):
    dP = scipy.special.binom(N_talks, i) * P_female_expect**i * \
         (1 - P_female_expect)**(N_talks - i)
    P_female_overrep += dP
    
print("##%04d %3d %3d %3d %3d Pexpect: %f Nexpect: %d Pobs: %f Pover: %f" %
      (year,N_talks,N_female,N_male,N_unclass,P_female_expect,N_female_expect,P_female_frac,P_female_overrep))

# Use the dataframe constructed above to generate statistics
def talk_statistics(df, stats_name=None, type_select=None):
    # Choose a default statistic:
    if stats_name is None:
        stats_name = "first_author"

    # Select only the rows with the specified talk_type value:
    if type_select is not None:
        df = df[df.talk_type == type_select]

    # Determine subsets to consider:
    if stats_name == "first_author":
        # Only use first authors
        df = df[df.author_order == 0]
    elif stats_name == "equal_weight":
        # Use all contributors equally
        df = df

    df_female = df[df.gender == "F"]
    df_male   = df[df.gender == "M"]

    N_female = df_female.count()
    N_male   = df_male.count()
    N_talks  = N_female + N_male

    P_female_frac = 0
    for i in range(0,N_female):
        dP = scipy.special.binom(N_talks, i) * P_female_expect**i * \
             (1 - P_female_expect)**(N_talks - i)
        P_female_frac += dP
        
    N_female_expect = math.ceil(P_female_expect * N_talks)
    
    P_female_overrep = 0
    for i in range(int(N_female_expect),N_talks):
        dP = scipy.special.binom(N_talks, i) * P_female_expect**i * \
             (1 - P_female_expect)**(N_talks - i)
    P_female_overrep += dP

    return N_talks, N_female, N_male, N_female_expect, P_female_frac, P_female_overrep

    
