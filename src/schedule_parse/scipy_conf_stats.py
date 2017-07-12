#!/usr/bin/env python3

import sys
import argparse
import math
import re
import scipy.special
import pandas as pd

import scipy_conf_parsers
import name_class

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
parser.add_argument('-P', '--p_expect',  type=float)
parser.add_argument('-f', '--file',      type=str)
#parser.add_argument('-s', '--stats_name', type=str)
#parser.add_argument('-t', '--type_select', type=str)
args = parser.parse_args()

# Set things up
P_female_expect = 0.24 # This is likely not correct.  
if args.p_expect is not None:
    P_female_expect = args.p_expect
talks = list()

# Generate a dataframe from the list of talks:
talk_df = pd.DataFrame();

year = args.year


# Parse the given year
if args.year > 0:

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
                    
    for talk in talks:
        title,author,talk_type,talk_source = talk

        author = re.sub('g.+?l\s+varoquaux','Gael Varoquaux',author, flags=re.IGNORECASE)
        author = re.sub('s.+?n\s+van der Walt','Stefan van der Walt',author, flags=re.IGNORECASE)
        author = re.sub('d.+?n\s+avila','Damian Avila', author, flags=re.IGNORECASE)
        author = re.sub('carissa, geodecisions','Carissa Brittain', author, flags=re.IGNORECASE)
        author = re.sub('o.+?j\s+\w+?ert\w+?k','Ondrej Certik', author, flags=re.IGNORECASE)
        author = re.sub('s.*?ren\s+sonnenburg','Soren Sonnenburg', author, flags=re.IGNORECASE)
        author = re.sub('B.+?n\s+Dahlgren','Bjorn Dahlgren', author) #, flags=re.IGNORECASE)
        author = re.sub('R.+?i\s+?Rampin','Remi Rampin', author) #, flags=re.IGNORECASE)
        author = re.sub('Jean-R\w+?mi\s+King','Jean-Remi King', author) #, flags=re.IGNORECASE)
        author = re.sub('s\w+?n buchoux','Sebastien Buchoux', author, flags=re.IGNORECASE)
        author = re.sub('&',';',author)
        
        authors = name_class.author_class(author,year)
        for author_index in range(0,len(authors)):
        
            talk_tmp = pd.DataFrame({'title' : talk[0], 'author' : authors[author_index][0], \
                                     'gender' : authors[author_index][1], 'author_order' : author_index, \
                                     'gender_frac' : authors[author_index][2], 'talk_type' : talk[2] }, index = [0])
            talk_df = talk_df.append(talk_tmp, ignore_index = True)
            print("%s@%s@%d@%s@%.2f@%s@%s" % (str(talk[0]).encode('utf-8'), str(authors[author_index][0]).encode('utf-8'), \
                                              author_index, authors[author_index][1], authors[author_index][2], talk[2], talk[3]))
else:
    input_file = open(args.file,"r")
    for line in input_file:
        if not line.startswith('#'):
            title, author, author_index, gender, gender_frac, talk_type, talk_source = line.strip().split('@')
            talk_tmp = pd.DataFrame({'title' : title, 'author' : author, \
                                     'gender' : gender, 'author_order' : author_index, \
                                     'gender_frac' : gender_frac, 'talk_type' : talk_type }, index = [0])
            talk_df = talk_df.append(talk_tmp, ignore_index = True)
        
        
N_talks, N_female, N_male, N_female_expect, P_female_frac, P_female_overrep = talk_statistics(talk_df, stats_name="equal_weight")
N_unclass = talk_df.shape[0] - N_talks

print("##%04d %3d %3d %3d %3d Pexpect: %f Nexpect: %d Pobs: %f Pover: %f" %
      (year,N_talks,N_female,N_male,N_unclass,P_female_expect,N_female_expect,P_female_frac,P_female_overrep))

        
# print((talk_df.to_string()).encode('utf-8'))
