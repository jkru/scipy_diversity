#!/usr/bin/env python

import sys
import argparse
import math
import scipy.special

import scipy_conf_parsers 
import name_class

# CZW: 2017-06-20 problems with the parsers:
#  2009  unremoved affiliations
#  2012  mis-class due to (ln, fn) arrangement
#  2013  incomplete due to (name, name, name) arrangement

# Pull out the year to consider.
parser = argparse.ArgumentParser()
parser.add_argument('year', type=int)
args = parser.parse_args()

# Set things up
P_female_expect = 0.24 # This is likely not correct.  
talks = list()

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
    
    
        
        

    

                    
                
