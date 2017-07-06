#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import string
import datetime
import re

CENSUS_DIR = './ssa2017'

# These are authors that appear in the corpus, but aren't in the census data
external_authors = {
    'abhinav' : 'M',
    'afshin' : 'M',
    'aina' : 'F',
    'almar' :"M",
    'anubhav' : 'M',
    'alexey'    : 'M',
    'andrezej'  : 'M',
    'arfon'     : 'M',
    'bargava'   : 'M',
    'bj\xc3\xb6rn' : 'M',
    'chandrashekhar' : 'M',
    'chih-jen':'M',
    'chi-keung' : 'M',
    'christfried' : 'M',
    'chu-ching' : 'F',
    'dag'       : 'M',
    'damiÃ¡n' : 'M',
    'dami\xc3\x83\xc2\xa1n' : 'M',
    'dav'       : 'M',
    'demba':'M',
    'dmitry' : 'M',
    'dorota'    : 'F',
    'gael'      : 'M',
    'gaël'      : 'M',
    'gaÃ«l' : 'M',
    'ga\xc3\x83\xc2\xabl' : 'M',
    'ga\xc3\xabl' : 'M',
    'gaurika' : 'F',
    'gholamreza' : 'M',
    'francesc'  : 'M',
    'harsh' : 'M',
    'idesbald'  : 'M',
    'iqbal' : 'M',
    'isuru' : 'M',
    'jaako' : 'M',
    'jean-christophe' : 'M',
    'jean-luc' : 'M',
    'jean-r\xc3\xa9mi' : 'M',
    'jiwon'     : 'M',
    'jostefan':'M',
    'kannan'    : 'M',
    'kytt' : 'M',
    'leif'      : 'M',
    'loïc' : 'M',
    'maik': 'M',
    'mainak' : 'M',
    'marcin': 'M',
    'matar' : 'F',
    'mateusz':'M',
    'mattheus':'M',
    'mehmet' : 'M',
    'minesh':'M',
    'navjot':"M",
    'nelle' : 'F',
    'nikunj'    : 'M',
    'ondrej'    : 'M',
    'ond\xc5\x99ej' :'M',
    'pavel' : 'M',
    'pierrick' : 'M', 
    'piotr' : 'M',
    'pjotr' : 'M',
    'prabhu'    : 'M',
    'prahbu'    : 'M',
    'pranab'    : 'M',
    'ramalingam' : 'M',
    'razvan' : 'M',
    'r\xc3\xa9mi' : 'M',
    'sartaj' : 'M',
    'sergey' : 'M',
    'shoaib' : 'M',
    'shraddha' : 'F',
    'shreyas':'M',
    'sÃ¶ren' : 'M',
    's\xc3\xa9bastien':'M',
    's\xc3\x83\xc2\xb6ren' : 'M',
    'stÃ©fan' : 'M',
    'stéfan' : 'M',
    'st\xc3\x83\xc2\xa9fan' : 'M',
    'sylvain' : 'M',
    'tareq' : 'M',
    'thilina' : 'M',
    'tzanko'    : 'M',
    'vanderlei' : 'M',
    'ville' : 'M',
    'vinothan'  : 'M',
    'viral': 'M',
    'vojtech' : 'M',
    'wim'       : 'M',
    'xander':'M', 
    'yahya' : 'M',
    'yannick' : 'M',
    'yoshiki'   : 'M',
    'yoshua' : 'M',
    'zeljko'    : 'M',
}
# These are authors that have first names that class them in one way, but
# for which that is a mistake.  I'm tempted to use this to flag affiliations
# as well.
override_authors = {
    'ariel rokem'     : 'M',
    'toni alatalo' : 'M',
    'd. brown' : 'M',
    'c. doutriaux' : 'M',
    'd.n. williams' : 'M',
    'gael varoquaux' : 'M',
    'michele vallisneri' : 'M',
    'st\xc3\x83\xc2\xa9fan van der walt' : 'M',
    'enthought' : 'M',
    'france' : 'U',
    'india' : 'U',
    'oak ridge national lab' : 'U',
    'reno' : 'U',
    'kadambari devarajan' : 'F',
    'corran webster' : 'M',
    's. chris colbert' : 'M',
    'helge reikeras' : 'M',
    'video 2' : 'M',
    'robin kraft' : 'M', 
    'jan h. meinke':'M',
    'and roy weckiewicz' : 'M',
    'min ragan-kelley' : 'M', 'Min RK' : 'M', 
    'b.e. granger' : 'M', 
    'j.g. hemann' : 'M', 
    'baseem ali':'M', 
    'minwoo lee' : 'M',
    'yu (cathy) jiao' : 'F', 
    'dharhas pothina':'M',
    'shams imam' : 'M',
    'akand islam': 'M',
    'aakash prasad' : 'M',
    'damian, oquanta avila' : 'M',
    'kelsey jordahl' : 'M',
    'aashish chaudhary' : 'M',
    'j gregory caporaso' : 'M',
    'jan vandrol': 'M',
    'kester tong' : 'M',
    'st\xc3\x83\xc2\xa9fan Van der Walt' : 'M',
    'ga\xc3\x83\xc2\xabl varoquaux' : 'M',
    'dami\xc3\x83\xc2\xa1n avila':'M',
    'mi' : 'M',
    'cox, david d., harvard university' : 'M',
    'anthony, the university of chicago & numfocus, inc. scopatz' : 'M',
    'oliveira jr' : 'M',
    'barbosa': 'F',
    'emmanuel, centre blaise pascal (lyon, france) quemener': 'M',
    'goodman' : 'F',
    'adam, duke university, cnrs france richards' : 'M',
    'kosinski andrzej' : 'M',
    'ryan, national institute of diabetes and digestive and kidney diseases, national institutes of dale' : 'M',
    'lin wang': 'F',
    'eric, subaru telescope, national astronomical observatory of japan jeschke' : 'M',
    'geodecisions carissa' : 'F',
    'bruning, eric c., texas tech university':'M',
    'ottesen, hal h., adjunct professor' : 'M',
    'harinarayan krishnan':'M',
    'david, nanobiology institute, yale university baddeley':'M',
    'zachary, materials measurement science division, national institute of standards and technol trautt':'M',
    'burcin erocal':'M',
    'kapil arya':'M',
    "jeffrey, center for biomedical informatics, the children's hospital of philadelphia miller":'M',
    'larsson omberg':'M',
    'xianlong hou':'M',
    'northeast regional climate center':'M',
    'ga\xc3\x83\xc2\xabl varoquaux':'M',
    'zhang zhang':'M',
    'shashank belvadi':'M',
    'wei kang':'F',
    'weixiang yu':'M',
    'jean-luc r. stevens': 'M',
    'abinash panda' : 'M',
    'bagrat amirbekian':'M',
    'krishna sridhar':'M',
    'en zyme':'M',
    'jordi torrents':'M',
    'geophysical inversion facility':'F',
    'subir mansukhani': 'M',
    'gudni rosenkjaer':'M',
    'jaime huerta-cepas' :'M',
    'keynote speaker: jake vanderplas phd':'M',
    'michka popoff':'M',
    's\xc3\x83\xc2\xb6ren sonnenburg':'M',
    'jan dom\xc3\xa1nski' : 'M',
    'siu kwan lam' :"M",
    'yu feng':'M',
    'marijn van vliet':'M',
    'dhruv madeka' : 'M',
    'himanshu mishra' : 'M',
    'chiranth siddappa' : 'M',
    'daniil pakhomov' : 'M',
    'horea-ioan ioanas' : 'M',
    'yongjun choi': 'M',
    'gautham dharuman': 'M',



#    'stéfan van der walt' : 'M',
#    'bargava subramanian' : 'M',
#    'loïc estève' : 'M',
}

def override(fn,ln):
    check_name = ""
    check_name += fn.lower()
    check_name += " "
    check_name += ln.lower()
    check_name = check_name.rstrip().lstrip()

    if check_name in override_authors:
        return(override_authors[check_name], -1)
    else:
        return None

def name_class(name,year):
    start_year = year - 30 - 5
    end_year   = year - 30 + 5
    this_year = datetime.date.today().year
    if this_year > end_year + 1:
        end_year = this_year - 1

    female_count = 0
    male_count = 0
    
    for year in range(start_year,end_year):
        f_name = ('%s/yob%04d.txt' % (CENSUS_DIR, year))
        f = open(f_name,"r")
        for line in f:
            scan_name, scan_gender, scan_count = line.strip().split(',')
            if (scan_name.lower() == name.lower()):
                if (scan_gender == 'F'):
                    female_count += int(scan_count)
                else:
                    male_count   += int(scan_count)

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

def author_class(author_string,year):
    author_list = list()
    author_string = str(author_string)
    authors = author_string.split(";")
#    print(">A>%s<<<" % author_string.encode('utf-8'))
    for auth in authors:
        auth = re.sub("\s+"," ",auth)
#        print(">>%s<<" % auth.encode('utf-8'))
        
        if re.search(":",auth) is not None:
            trash,auth = auth.split(": ", 1)
        if re.search(",",auth) is not None:
            if auth.count(',') == 2:

                ln, fn, affil = auth.split(",", 2)
                ln = ln.rstrip().lstrip()
                fn = fn.rstrip().lstrip()
                if (len(ln.split(" ")) == 1) and (len(fn.split(" ")) == 1):
                    auth = fn + " " + ln
                elif len(ln.split(" ")) > 1:
                    auth = ln

#                print ("In check value 2: %s %d %d %s %s" % (auth.encode('utf-8'), len(ln.split(" ")), len(fn.split(" ")), fn.encode('utf-8'), ln.encode('utf-8')))
                    
            else:
                auth,affil = auth.split(",", 1)
                if len(auth.split(" ")) == 1:
                    # This is the case of (ln, fn) type names
                    auth = affil + " " + auth
#                    print("In check value else: %s" % auth.encode('utf-8'))
                    

        auth = auth.rstrip().lstrip()
        fn = ""
        ln = ""
        if re.search(" ",auth) is not None:
            fn,ln = auth.split(" ", 1)
        else:
            fn = auth

        gender = ""
        g_frac = -1
        if override(fn,ln) is not None:
            gender, g_frac = override(fn,ln)
        else:
            gender, g_frac = name_class(fn,year)

        if auth != "":
            author_list.append( (auth, gender, g_frac) )
#        print("     >>%s<< >%s< %s %f" % (fn.encode('utf-8'), auth.encode('utf-8'), gender, g_frac))

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
    (gender_value, ratio) = name_class(args.name.lower(),2017)
    print( args.name, gender_value, ratio)
#    I = open(args.infile,"r")
#    N_talk = 0
#    N_male = 0
#    N_female = 0
#    for line in I:
#        name, title, talk_type, gender, multiple, source = line.strip().split('@')
#        test_name, other = name.split(' ', 1)




        
        
                                            
