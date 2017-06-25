#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import string
import datetime
import re

CENSUS_DIR = './ssa2017'

# These are authors that appear in the corpus, but aren't in the census data
external_authors = {
    'alexey'    : 'M',
    'andrezej'  : 'M',
    'arfon'     : 'M',
    'christfried' : 'M',
    'chu-ching' : 'F',
    'dag'       : 'M',
    'damiÃ¡n' : 'M',
    'dav'       : 'M',
    'dorota'    : 'M',
    'gael'      : 'M',
    'gaÃ«l' : 'M',
    'gholamreza' : 'M',
    'francesc'  : 'M',
    'idesbald'  : 'M',
    'jean-christophe' : 'M',
    'jiwon'     : 'M',
    'kannan'    : 'M',
    'leif'      : 'M',
    'nikunj'    : 'M',
    'ondrej'    : 'M',
    'prabhu'    : 'M',
    'prahbu'    : 'M',
    'pranab'    : 'M',
    'ramalingam' : 'M',
    'stÃ©fan' : 'M',
    'tzanko'    : 'M',
    'vanderlei' : 'M',
    'vinothan'  : 'M',
    'wim'       : 'M',
    'yoshiki'   : 'M',
    'zeljko'    : 'M',
}

def name_class(name):
    this_year = datetime.date.today().year
    female_count = 0
    male_count = 0
    
    for year in range((this_year - 30) - 5, (this_year - 30) + 5):
        f_name = ('%s/yob%04d.txt' % (CENSUS_DIR, year))
        f = open(f_name,"r")
        for line in f:
            scan_name, scan_gender, scan_count = line.strip().split(',')
            if (scan_name.lower() == name.lower()):
                if (scan_gender == 'F'):
                    female_count += string.atoi(scan_count)
                else:
                    male_count   += string.atoi(scan_count)

        denominator = female_count + male_count
        if (denominator == 0):
            if name.lower() in external_authors:
                return external_authors[name.lower()], -1
            else:
                return "U", -1
            
        if (female_count >= male_count):
            return "F", 1.0 * female_count / denominator
        else:
            return "M", 1.0 * male_count   / denominator

def author_class(author_string):
    author_list = list()
    authors = author_string.split(";")
    for auth in authors:
#        print(auth)
        auth = re.sub("\s+"," ",auth)
        if re.search(":",auth) is not None:
            trash,auth = auth.split(": ", 1)
        if re.search(",",auth) is not None:
            auth,affil = auth.split(",", 1)
            

        auth = auth.rstrip().lstrip()
        if re.search(" ",auth) is not None:
            fn,ln = auth.split(" ", 1)
        else:
            fn = auth
        gender, g_frac = name_class(fn)
        author_list.append( (auth, gender, g_frac) )

    return author_list
        
#    author_list = author_string("; ")
    # cases:
    # (fn ln)
    # (fn ln; fn ln)
    # (fn ln, affil; fn ln, affil)
    # (fn ln, fn ln)
    # (fn ln, affil, fn ln, affil)
    # (ln, fn, ln, fn)
    # (ln, fn, affil, ln, fn, affil)


    

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    (gender_value, ratio) = name_class(args.name.lower())
    print( args.name, gender_value, ratio)
#    I = open(args.infile,"r")
#    N_talk = 0
#    N_male = 0
#    N_female = 0
#    for line in I:
#        name, title, talk_type, gender, multiple, source = line.strip().split('@')
#        test_name, other = name.split(' ', 1)




        
        
                                            
