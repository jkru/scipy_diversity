#!/usr/bin/env python3

import sys
import argparse
import math
import re
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

# Use the dataframe constructed from the talks to generate statistics
def talk_statistics(df, stats_name=None, type_select=None):
    # # Methodology following:
    # # http://www.laurenbacon.com/how-likely-is-an-all-male-speakers-list-statistically/

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

    N_female = df_female.shape[0]
    N_male   = df_male.shape[0]
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

# Generate a dataframe from the list of talks:
talk_df = pd.DataFrame();

for talk in talks:
    title,author,talk_type,talk_source = talk

#    print (author.encode('utf-8'))
    author = re.sub('g\w+?l\s+varoquaux','Gael Varoquaux',author, flags=re.IGNORECASE)
    author = re.sub('s\w+?n\s+van der Walt','Stefan van der Walt',author, flags=re.IGNORECASE)
    author = re.sub('d\w+?n\s+avila','Damian Avila', author, flags=re.IGNORECASE)
    author = re.sub('carissa, geodecisions','Carissa Brittain', author, flags=re.IGNORECASE)
    author = re.sub('o\w+?j\s+\w+?ert\w+?k','Ondrej Certik', author, flags=re.IGNORECASE)
    author = re.sub('s.*?ren\s+sonnenburg','Soren Sonnenburg', author, flags=re.IGNORECASE)
    author = re.sub('B\w+?n\s+Dahlgren','Bjorn Dahlgren', author) #, flags=re.IGNORECASE)
    author = re.sub('R.+?i\s+?Rampin','Remi Rampin', author) #, flags=re.IGNORECASE)
    author = re.sub('Jean-R\w+?mi\s+King','Jean-Remi King', author) #, flags=re.IGNORECASE)
    author = re.sub('s\w+?n buchoux','Sebastien Buchoux', author, flags=re.IGNORECASE)
#    print (author.encode('utf-8'))

    authors = name_class.author_class(author,year)
    for author_index in range(0,len(authors)):

        talk_tmp = pd.DataFrame({'title' : talk[0], 'author' : authors[author_index][0], \
                                 'gender' : authors[author_index][1], 'author_order' : author_index, \
                                 'gender_frac' : authors[author_index][2], 'talk_type' : talk[2] }, index = [0])
        talk_df = talk_df.append(talk_tmp, ignore_index = True)
        print("%s@%s@%s@%.2f@%s@%s" % (str(talk[0]).encode('utf-8'), str(authors[author_index][0]).encode('utf-8'), \
                                  authors[author_index][1], authors[author_index][2], talk[2], talk[3]))

        
N_talks, N_female, N_male, N_female_expect, P_female_frac, P_female_overrep = talk_statistics(talk_df, stats_name="equal_weight")
N_unclass = talk_df.shape[0] - N_talks

print("##%04d %3d %3d %3d %3d Pexpect: %f Nexpect: %d Pobs: %f Pover: %f" %
      (year,N_talks,N_female,N_male,N_unclass,P_female_expect,N_female_expect,P_female_frac,P_female_overrep))

        
# print((talk_df.to_string()).encode('utf-8'))
