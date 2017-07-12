# -*- coding: utf-8 -*-
#
# Attempt to intelligently parse the SciPy convention schedules to determine list of talks and authors.
#

import sys
import re
import requests
from bs4 import BeautifulSoup
from bs4 import element
import importlib 

importlib.reload(sys)
#sys.setdefaultencoding("utf-8")

#
# List of urls that I've used as the sources for the name scans.
urls = {2008: ('http://conference.scipy.org/SciPy2008/conference.html',""),
        2009: ('http://conference.scipy.org/SciPy2009/schedule.html',""),
        2010: ('http://conference.scipy.org/scipy2010/schedule.html',
               'http://conference.scipy.org/scipy2010/lightning.html'),
        2011: ('http://conference.scipy.org/scipy2011/talks.php',
               'http://conference.scipy.org/scipy2011/tutorials.php'),
        2012: ('http://conference.scipy.org/scipy2012/schedule/conf_schedule_1.php',
               'http://conference.scipy.org/scipy2012/schedule/conf_schedule_2.php',
               'http://conference.scipy.org/scipy2012/tutorials.php'),
        2013: ('http://conference.scipy.org/scipy2013/conference_talks_schedule.php',
               'http://conference.scipy.org/scipy2013/tutorials_schedule.php'),
        2014: ('http://conference.scipy.org/scipy2014/schedule/talks-posters',
               'http://conference.scipy.org/scipy2014/schedule/tutorials/',
               'http://conference.scipy.org/scipy2014/schedule/bofs/'),
        2015: ('http://scipy2015.scipy.org/ehome/115969/297898/',
               'http://scipy2015.scipy.org/ehome/115969/289057/'),
        2016: ('http://scipy2016.scipy.org/ehome/146062/332965/',
               'http://scipy2016.scipy.org/ehome/146062/332960/'),
        2017: ('http://scipy2017.scipy.org/ehome/220975/493422/',
               'http://scipy2017.scipy.org/ehome/220975/493418/') }

#
# Parsers.  I probably could have wrapped these together, but wasn't sure that was worth the effort.
#   All of them return a list of talks, with each talk being a tuple of:
#   (title, author_string, talk_type, talk_source)
#   The title is simple, the author_string contains all the authors in a (hopefully) semi-colon
#   separated list, the talk_type is one of k,n,t,l,b for keynote, normal, tutorial, lightning, and
#   bof.  The talk_source is "s" for schedule for all parsed talks, and may also be a:abstract or
#   t:talk slides for the pre-defined talks.

#
# Classify talk type.  Sometimes this can be pulled from the URL.  Assume most talks are normal, but allow
# keynotes and tutorials to be set based on information in the title.
def classify_talk(title, url):
    talk_type = "n"
    if re.search("lightning", url) is not None:
        talk_type = "l"
    if re.search("tutorial", url) is not None:
        talk_type = "t"
    if re.search("bofs", url) is not None:
        talk_type = "b"
    if re.search("keynote",title, re.IGNORECASE) is not None:
        talk_type = "k"
    elif re.search("\((Beginner|Intermediate|Advanced)\)", title, re.IGNORECASE) is not None:
        talk_type = "t"

    return talk_type

#
# Parser for 2017/2016.  Pull table cells, and then use regexp to extract information.
def p2017(url,use_first):
    i = 0
#    print ("%s\n" % url)
    r = requests.get(url)
    talks = list();
    
    soup = BeautifulSoup(r.text,'html5lib')
    tables = soup.findAll('table', { 'class' : 'agenda_table' })
    for table in tables:
        rows = table.findAll('tr', { 'class' : 'agenda_time_slot' })
        for row in rows:
            cols = row.findAll('td')
            for col in cols:
                title_text = ""
                author_text = ""

                if len(col.contents) == 0:
                    continue
                
#                print(col.contents)

                if use_first:
                    title_text = col.contents[0].string
                
                for content in col.contents[use_first:]:
                    if re.search("sessiondetails.php",str(content)) is not None and title_text == "":
                        title_text = content.string #x.encode('utf-8')
                    elif re.search("speakerdetails.php",str(content)) is not None and content.string is not None:
                        if author_text != "":
                            author_text += "; "
                        author_text += content.string
                    elif re.search('span class="speaker_name"', str(content)) is not None:
                        for ss in content.strings:
                            if author_text != "":
                                author_text += "; "
                            author_text += ss.string

                if title_text != "" and author_text != "":
                    author_text = author_text.replace("; , ",", ")
                    talk_type = classify_talk(title_text, url)
#                    talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
                    talks.append( (title_text, author_text, talk_type, "s"))
    return talks

#
# Parser for 2015.  Nearly idential to p2017, but needs to concatenate all the string entries to
# generate a title, instead of simply converting the cell directly.
def p2015(url,use_first):
    i = 0
#    print ("%s\n" % url)
    r = requests.get(url)
    talks = list();
    
    soup = BeautifulSoup(r.text,'html5lib')
    tables = soup.findAll('table', { 'class' : 'agenda_table' })
    for table in tables:
        rows = table.findAll('tr', { 'class' : 'agenda_time_slot' })
        for row in rows:
            cols = row.findAll('td')
            for col in cols:
                title_text = ""
                author_text = ""
                
#                print(col.contents)
                if len(col.contents) == 0:
                    continue
                
                if use_first:
                    title_text = col.contents[0].string
                
                for content in col.contents[use_first:]:
                    if re.search("sessiondetails.php",str(content)) is not None and title_text == "":
                        for ss in content.strings:
                            title_text += ss.string
                    elif re.search("speakerdetails.php",str(content)) is not None and content.string is not None:
                        if author_text != "":
                            author_text += "; "
                        author_text += content.string
                    elif re.search('span class="speaker_name"', str(content)) is not None:
                        for ss in content.strings:
                            if author_text != "":
                                author_text += "; "
                            author_text += ss.string
                if title_text != "" and author_text != "":
                    author_text = author_text.replace("; , ",", ")
                    talk_type = classify_talk(title_text, url)

#                    talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
                    talks.append( (title_text, author_text, talk_type, "s"))
    return talks

#
# Internal code for 2014.  Had other years shared the formatting, this would have been nice to share.
def p2014_internal(url, table_class, row_class, title_class, author_class, keynote_class):
    i = 0
#    print ("%s\n" % url)
    r = requests.get(url)
    talks = list();

    soup = BeautifulSoup(r.text,'html5lib')
    tables = soup.findAll('table', { 'class' : table_class })
    for table in tables:
        rows = table.findAll('tr', { 'class' : row_class })
        for row in rows:
            cols = row.findAll('td')
            for col in cols:
                title_span = col.find('span', { 'class' : title_class })
                author_span = col.find('span', { 'class' : author_class })

                if title_span is not None:
                    title_text = title_span.a.extract().string.strip()
                    author_text = author_span.extract().string.strip()
                    author_text = author_text.replace(", ","; ")
                    talk_type = classify_talk(title_text, url)
#                    talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
                    talks.append( (title_text, author_text, talk_type, "s"))
            cols = row.findAll('td', { 'class' : keynote_class })
            for col in cols:
                title_text, author_text = col.p.extract().string.split(' - ')
                author_text = author_text.replace(", ","; ")
                talk_type = classify_talk(title_text, url)
#                talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
                talks.append( (title_text, author_text, talk_type, "s"))
    return talks
#end

#
# Wrapper for 2014.
def p2014(url):
    return p2014_internal(url,"calendar table table-bordered","","title","speaker","slot slot-Keynote")

#
# Internal code for 2013/2012.  Talk information can show up wrapped in two places, so use common
# parsing code that can be called from each location.
def p2013_internal(contents):
    title_text = ""
    author_text = ""
    is_keynote = 0
    if len(contents) == 0:
        return None, None
    for content in contents:
        if re.search("Keynote",str(content), re.IGNORECASE) is not None:
            is_keynote = 1

        if re.search("presentation_detail.php",str(content)) is not None and title_text == "":
            for ss in content.strings:
                title_text += ss.string
        elif re.search("tutorial_detail.php",str(content)) is not None and title_text == "":
            for ss in content.strings:
                title_text += ss.string
        elif re.search('span class="bold"',str(content)) is not None and title_text == "":
            for ss in content.strings:
                title_text += ss.string
        elif re.search("speakerdetails.php",str(content)) is not None and content.string is not None:
            if author_text != "":
                author_text += "; "
                author_text += content.string
        elif re.search('span class="authors"', str(content)) is not None:
            for ss in content.strings:
                if author_text != "":
                    author_text += "; "
                author_text += ss.string
    if title_text != "" and author_text == "":
        author_text = contents[-1].string.strip()
        if re.search("Moderator",str(contents[-2]), re.IGNORECASE) is not None:
            author_text += contents[-2].string.strip()
    if title_text != "" and author_text == title_text:
        return None, None
    if title_text != "" and author_text != "":
        author_text = author_text.replace("; , ",", ")
        author_text = author_text.replace("- ","")
        if is_keynote:
            title_text = "Keynote: " + title_text
#        print("nNn%snTn%saAa" % (title_text.encode('utf-8'),author_text.encode('utf-8')))
        return title_text, author_text                
    else:
        return None, None
        
#
# Top level wrapper for 2013/2012.  Identifies the content locations for the internal parser.
def p2013(url):
    i = 0
#    print ("%s\n" % url)
    r = requests.get(url)
    talks = list();
    
    soup = BeautifulSoup(r.text,'html5lib')
    tables = soup.findAll('table', { 'id' : 'registrants_table' })
    for table in tables:
        rows = table.findAll('tr')
        for row in rows:
            cols = row.findAll('td')
            for col in cols:
                if len(col.contents) == 0:
                    continue

                divs = col.findAll('div')
                if len(divs) == 0:
                    title_text, author_text = p2013_internal(col.contents)
                    if title_text is not None and author_text is not None:
                        talk_type = classify_talk(title_text, url)
#                        talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
                        talks.append( (title_text, author_text, talk_type, "s"))
                else:
                    for div in divs:
                        title_text,author_text = p2013_internal(div.contents)
                        if title_text is not None and author_text is not None:
                            talk_type = classify_talk(title_text, url)
#                            talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type,"s"))
                            talks.append( (title_text, author_text, talk_type, "s"))
    return talks

#
# Parser for 2011/2010.  Less clear due to formatting, and requires conditional array indices to
# determine what to use to generate the author lists.
def p2011(url,content_key):
    i = 0
#    print ("%s\n" % url)
    r = requests.get(url)
    talks = list();
    
    soup = BeautifulSoup(r.text,'html5lib')
    utility = soup.find('div', { 'id' : content_key })
    blocks = utility.findAll('ul')
    for block in blocks:
        entries = block.findAll('li')
        for entry in entries:
            title_text = ""
            author_text = ""
#            print(entry.contents)
            if len(entry.contents) < 2:
                continue

            title_text = entry.contents[0].string

            if content_key == 'inner-content':
                author_text = entry.contents[1].string.rstrip()
                if author_text == " -":
                    author_text = entry.contents[2].string.rstrip()
            elif content_key == 'content':
                if entry.contents[-1].string.rstrip() == "":
                    author_text = entry.contents[-2].string.rstrip()
                else:
                    author_text = entry.contents[-1].string.rstrip()

            if title_text != "" and author_text != "":
                if title_text is not None and author_text is not None:
                    title_text = title_text.replace(" | ","")
                    title_text = title_text.replace(" | ","")
                    title_text = title_text.replace("\n\t"," ")

                    author_text = author_text.replace(" | ","")
                    author_text = author_text.replace(" | ","")
                    author_text = author_text.replace("\n\t"," ")
                    author_text = author_text.replace(", ","; ")

                    talk_type = classify_talk(title_text, url)
#                    talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
                    talks.append( (title_text, author_text, talk_type, "s"))
    return talks

#
# Parser for 2009/2008.  Similar to p2011, but the content is more uniform in ordering.
# The "strong" entry needs to be destroyed, as this contaminates the results.
def p2009(url,content_key):
    i = 0
#    print ("%s\n" % url)
    r = requests.get(url)
    talks = list();
    
    soup = BeautifulSoup(r.text,'html5lib')
    blocks = soup.findAll('div', { 'class' : content_key })
    for block in blocks:
        entries = block.findAll('p')
        for entry in entries:
            title_text = ""
            author_text = ""

            if entry.strong is not None:
                entry.strong.decompose()

            text_string = ""
            for content in entry.contents:
                text_string += content.string.rstrip()

            text_string = text_string.lstrip().replace("\n"," ")

            if re.search("\(",text_string) is not None:
                title_text,author_text = text_string.rsplit(" (",1)
                author_text = author_text.replace(")","")
            
            if title_text != "" and author_text != "":
                if title_text is not None and author_text is not None:
                    title_text = title_text.replace(" | ","")
                    title_text = title_text.replace(" | ","")
                    title_text = title_text.replace("\n\t"," ")
                    
                    author_text = author_text.replace(" | ","")
                    author_text = author_text.replace(" | ","")
                    author_text = author_text.replace("\n\t"," ")
                    author_text = author_text.replace(", ","; ")

                    talk_type = classify_talk(title_text, url)
#                    talks.append( (title_text.encode('utf-8'), author_text.encode('utf-8'), talk_type, "s"))
#                    talks.append( (str(title_text.decode('utf-8')), str(author_text.decode('utf-8')), talk_type, "s"))
                    talks.append( (title_text, author_text, talk_type, "s"))
    return talks


#
# Method to dump out pre-defined content information.  This covers information that does not have
# an existing URL to pull from, as well as content that is poorly formatted (and which doesn't justify
# a full parsing solution when there are only a small number of entries).
def defined_content(year):
    talks = list();

    if year == 2002:
        talks.append( ("Biological Sciences Libraries","Michel Sanner", "t","s") )
        talks.append( ("Lightning Talks I","Travis Vaught","l","s") )
        talks.append( ("Lightning Talks II","Travis Vaught","l","s") )
        talks.append( ("NumArray","Perry Greenfield","t","s") )
        talks.append( ("PMV and underlying components","Michel Sanner","t","s") )
        talks.append( ("Faster Python Weave, Accelerate","Eric Jones; Patrick Miller","n","s") )
        talks.append( ("Astronomy","Perry Greenfield","b","s") )
        talks.append( ("Biology","Michel Sanner","b","s") )
        talks.append( ("Intro to Numeric","Eric Jones","t","s") )
        talks.append( ("Intro to SciPy","Travis Oliphant","t","s") )
        talks.append( ("Graphics","Dave Morrill; Eric Jones","t","s") )
        talks.append( ("Parallel Computing","Patrick Miller","t","s") )
        talks.append( ("Community Development - Standards, Peer Review, etc.(SciPy.org)","Michael Aivazis; Travis Vaught","b","s") )
        talks.append( ("SciPy Library Development","Travis Oliphant","n","s") )
        talks.append( ("Visual Programming Components","Michel Sanner","n","s") )

    elif year == 2003:
        talks.append( ("NumArray: A status update","Perry Greenfield","n","s") )
        talks.append( ("The Chaco plotting library: A status report","Dave Morrill; Eric Jones","n","s") )
        talks.append( ("Something Biological 1","Michel Sanner","n","s") )
        talks.append( ("Parallel Programming","Konrad Hinsen","n","s") )
        talks.append( ("Pyre","Michael Aivazis","n","s") )
        talks.append( ("Grid Computing","Keith Jackson","n","s") )
        talks.append( ("MayaVi","Prabhu Ramachandran","n","s") )
        talks.append( ("Accelerate Python","Patrick Miller","n","s") )
        talks.append( ("Wavelet Library","Chad Netzer","n","s") )
        talks.append( ("Exploratory space-time data analysis with Python","Serge Rey; Mark Janikas; Boris Dev; Young Sik-Kim","n","s") )
        talks.append( ("Ipython --An interactive shell for Python","Fernando Perez","n","s") )
        talks.append( ("HippoDraw","James Chiang; Paul Kunz","n","s") )
        talks.append( ("Large Scale Interoperability Framework with Python","Matt Knepley","n","s") )
        talks.append( ("Python as a Key for the Development of a Large Numerical Model","Mike Mueller","n","s") )
        talks.append( ("pyMPI","Patrick Miller","l","s") )
        talks.append( ("NumArray Extensions","Todd Miller","l","s") )
        talks.append( ("Sparse Matrices","Travis Oliphant","l","s") )
        talks.append( ("Kiva","Eric Jones","l","s") )
        talks.append( ("Augmented Reality Talk","Michel Sanner","l","s") )
        talks.append( ("Systems Biology with Python","Jeff Sosserman","l","s") )
        talks.append( ("Wrapping with SWIG and Boost: a comparison","Prabhu Ramachandran","l","s") )

    elif year == 2004:
        talks.append( ("keynote","Jim Hugunin","k","s") )
        talks.append( ("Elmer: glues Pythons to other animals","Rick Ratzel","l","s") )
        talks.append( ("New Traits Mechanism in Python","Eric Jones","l","s") )
        talks.append( ("PyNGL: Visualization for the geosciences","Mary Haley","l","s") )
        talks.append( ("Numarray status","Perry Greenfield","l","s") )
        talks.append( ("Envisage: A scientific application framework","Eric Jones","n","s") )
        talks.append( ("Adaptive PDE solvers using multiwavelets","Fernando Perez","n","s") )
        talks.append( ("Sparse Matrices, Iterative Tools, and Optimization","Travis Oliphant","n","s") )
        talks.append( ("Building Python-based Scientific Computation Platform from LiveZope DVD","Chu-Ching Huang","n","s") )
        talks.append( ("Matplotlib --- a 2D graphics package","John Hunter","n","s") )
        talks.append( ("Software Components for Structural Bio-informatics","Michel Sanner","n","s") )
        talks.append( ("The Enable and Chaco Toolkit","Dave Morill","n","s") )
        talks.append( ("Python in a scientific camera testing system","Andrew Moore","n","s") )
        talks.append( ("Multidrizzle: Automated Image Combination and Cosmic-Ray Identification Software","Robert Jedrzejewski","n","s") )
        talks.append( ("Special Session: Making Python attractive to General Scientists","Joe Harrington; Perry Greenfield","b","s") )
        talks.append( ("Python for CFD: A Case Study","Prahbu Ramachandran","n","s") )
        talks.append( ("ExoPy: A Python Interface to a Finite Element Database","Vincent Urias; Phil Sackinger","n","s") ) # t for sackinger
        talks.append( ("High Performance Data Management with PyTables and Family","Francesc Alted","n","s") )
        talks.append( ("Interactive Work in Python: IPython's Present and Future","Fernando Perez","n","s") )
        talks.append( ("NetworkX: Growing a Python-based Toolbox for Complex Networks","Aric Hagberg","n","s") )
        talks.append( ("Vision: Visual Programming for Python","Daniel Stoffler; Michel Sanner","n","s") ) # t for sanner
        talks.append( ("PyARTK: a Python interface to ARToolKit, with Application in Molecular Biology","Alexandre Gillet","n","s") )
        talks.append( ("Python in the Flexibility Study of Biological Molecules","Yong Zhao","n","s") )
        talks.append( ("Experience with Python-based Tools for Proteomics","Randy Heiland; Charles Moad; Sean Mooney","n","s") ) # t for moad, mooney
        talks.append( ("NEAT: A NITF 2.1 File Explorer","Pranab Banerjee","n","s") )
        talks.append( ("A Python Configure Replacement","Matt Knepley","n","s") )

    elif year == 2005:
        talks.append( ("New Array Object for scipy.base","Travis Oliphant","n","s") )
        talks.append( ("Off the Beaten Path: Advanced Matplotlib Features","John Hunter","n","s") )
        talks.append( ("PyTrilinos: A Python Interface to Trilinos, a Set of Object-Oriented Solver Packages","Bill Spotz","n","s") )
        talks.append( ("PDE Libraries in Python","Matt Knepley","n","s") )
        talks.append( ("FiPy","Daniel Wheeler; Jonathon Guyer; James Warren","n","s") ) #a for guyer, warren
        talks.append( ("Using AutoDock with AutoDockTools: A Tutorial","Ruth Huey; Garret Morris; Michel Sanner","t","s") ) # a for morris, sanner
        talks.append( ("No title","Fernando Perez","l","s") )
        talks.append( ("No title","D. Brown","l","s") )
        talks.append( ("No title","Travis Oliphant","l","s") )
        talks.append( ("Envisage","Eric Jones","n","s") )
        talks.append( ("Chaco","Brandon DuRette","n","s") )
        talks.append( ("Interactive Documents with IPython","Robert Kern; Toni Alatalo; Tzanko Matev; Fernando Perez","n","s") ) # a for alatalo, matev, perez
        talks.append( ("NiPy NeuroImaging Software in Python","Matthew Brett","n","s") ) # typo talk "m"
        talks.append( ("Vision: A Visual Programming Component","Michel Sanner","n","s") ) # typo talk "m"
        talks.append( ("Using a generalized MPI interface for Python, MYMPI","Timothy Kaiser; Sarah Healy; Leesa Brieger","n","s") ) # a for healy, brieger; typo talk "m/f"

    elif year == 2006:
        talks.append( ("Numpy","Travis Oliphant","t","s") )
        talks.append( ("IPython/Matplotlib","Fernando Perez; John Hunter","t","s") )
        talks.append( ("Question and Answer Session","Fernando Perez; John Hunter","t","s") )
        talks.append( ("Scientific Apps - Traits/TraitsUI","Eric Jones; Dave Morrill","t","s") )
        talks.append( ("Data Exploration with Chaco","Peter Wang","t","s") )
        talks.append( ("Mayavi/TVTK","Prabhu Ramachandran","t","s") )
        talks.append( ("Keynote","Guido van Rossum","k","s") )
        talks.append( ("Understanding NumPy: How to Use dtype Objects","Travis Oliphant","n","s") )
        talks.append( ("Extending NumPy: a comparison of SWIG, f2py, weave, Pyrex, and ctypes","Travis Oliphant","n","s") )
        talks.append( ("Python for Modern Scientific Algorithm Development","Fernando Perez","n","s") )
        talks.append( ("Building a Distributed Component Framework","Michael Aivazis","n","s") )
        talks.append( ("The Enthought Tool Suite for Scientific Applications","Eric Jones","n","s") )
        talks.append( ("Synthetic Programming with Python","Chris Mueller","n","s") )
        talks.append( ("3D visualization with TVTK and MayaVi2","Prabhu Ramachandran","n","s") )
        talks.append( ("Realtime Computing with Python","Andrew Straw","n","s") )
        talks.append( ("Prototyping Mid-Infrared Detector Data Processing Algorithms","Mike Ressler","n","s") ) # no talk type listed, assuming normal
        talks.append( ("The State of IPython","Brian Granger","l","s") )
        talks.append( ("Array Interface BOF","Travis Oliphant","l","s") )
        talks.append( ("Enstaller","Travis Vaught","l","s") )
        talks.append( ("The Current State of Vision","Michel Sanner","l","s") )
        talks.append( ("Quick Overview of Chaco","Peter Wang","l","s") )
        talks.append( ("SAGE:Software for Algebra and Geometry Experimentation Notes","William Stein","n","s") )
        talks.append( ("Mathematica-like Plotting in SAGE Notes","Alex Clemesha","n","s") )
        talks.append( ("BioHub Presentation","Diane Trout","n","s") )
        talks.append( ("Software Carpentry","Greg Wilson","n","s") )
        talks.append( ("AutoLigand for AutoDock","Rodney Harris","n","s") )
        talks.append( ("GpuPy: Using GPUs to Accelerate NumPy","Benjamin Eitzen","n","s") )
        talks.append( ("Boost Graph Library","Douglas Gregor","n","s") )
        talks.append( ("Fast Multipole Algorithm","Idesbald Van den Bosch","n","s") )
        talks.append( ("OOF  Object-Oriented Finite Elements at NIST","Andrew Reid","n","s") )
        talks.append( ("Parallel PDE Solvers in Python","Bill Spotz","n","s") )
        talks.append( ("Python Imaging Tools for Reconstructing Magnetic Resonance Images","Mike Trumpis","n","s") )
        talks.append( ("PyRoot","Wim Lavrijsen","n","s") )
        talks.append( ("Python Interface to QScimpl presentation","Eric Dobbs","n","s") )
        talks.append( ("Python Web and Grid Service Tools","Keith Jackson","n","s") )
        talks.append( ("GENESIS SciFlo: Scientific Knowledge Creation on the Grid using a Semantically-Enabled Dataflow Execution Environment","Brian Wilson","n","s") )
        talks.append( ("Seeing Through the MIST: Richer Reconfigurable Interactive Systems","Tripp Lilley","n","s") )
    elif year == 2007:
        talks.append( ("Flight Software Code Generaton Tools for the Mars Science Laboratory","Leonard J. Reder","l","s") ) 
        talks.append( ("Climate Data Analysis Tools", "C. Doutriaux; D.N. Williams", "l","s"))
        talks.append( ("The Numenta Platform for Intelligent Computing", "Numenta, Inc.", "l","s") )
        talks.append( ("Teaching Scientific Computing with Python", "Rick Wagner", "l","s") )
        talks.append( ("PyStream: Stream and GPU computing in Python", "Brian Granger", "l","s") )
        talks.append( ("TVTK and MayaVi2", "Prabhu Ramachandran", "l","s") )
        talks.append( ("MLab", "Gael Varoquaux", "l","s") )
        talks.append( ("TConfig - Traits-based declarative configuration for programs", "Fernando Perez", "l","s") )
        talks.append( ("A plug for numpy.i (swig interface file), and release 8.0 of Trilinos, including the PyTrilinos package","Bill Spotz", "l","s") )

        talks.append( ("Scientific Computing using IPython/!NumPy/!SciPy/matplotlib/etc.", "Fernando Perez; Brian Granger", "t","s") )
        talks.append( ("Idiomatic Python","Titus Brown", "t","s") )
        talks.append( ("Wrapping Code with Python", "Bill Spotz; Eric Jones", "t","s") )
        talks.append( ("SciPy for Signal Processing and Image Processing", "Travis E. Oliphant", "t","s") )

        talks.append( ("Keynote","Ivan Krstic", "k","s") )
        talks.append( ("Python buffer interface", "Travis Oliphant", "n","s") )
        talks.append( ("CorePy: Using Python on IBM's Cell/B.E.", "Chris Mueller", "n","s") )
        talks.append( ("Python and the Mock LISA Data Challenges", "Michele Vallisneri", "n","s") )
        talks.append( ("Interactive Plotting for Fun and Profit", "Peter Wang", "n","s") )
        talks.append( ("Pygr: The Python Graph Database Framework for Bioinformatics", "Chris Lee", "n","s") )
        talks.append( ("Beowulf Analysis Symbolic INterface-BASIN: a multi-user environment for parallel data analysis and visualization","Enrico Vesperini; Doug Jones; Dave Goldberg; Steve McMillan", "n","s") )
        talks.append( ("Evolving Wavelets using Scipy: Analysis of Controlled Plasma Transients", "Terence Yeoh", "n","s") )
        talks.append( ("The Cartwheel Project: Python tools for regulatory genomics", "Titus Brown", "n","s") )
        talks.append( ("The Galaxy platform for accessible and reproducible scientific research", "James Taylor", "n","s") )
        talks.append( ("Elefant (Efficient Learning, Large-scale, Inference, and Optimization Toolkit)", "Christfried Webers", "n","s") )
        talks.append( ("Using Python for electronic structure calculations, nonlinear solvers, FEM and symbolic manipulation", "Ondrej Certik", "n","s") )
        talks.append( ("River: A Foundation for the Rapid Development of Reliable Parallel Programming Systems", "Gregory Benson; Alexey S. Fedosov", "n","s") )

    elif year == 2008:
        talks.append( ("Basics of Python","Perry Greenfield; Michael Droettboom; Fernando Perez","t","s") )
        talks.append( ("Astronomical Data Analysis","Perry Greenfield","t","s") )
        talks.append( ("Building Extensions with Numscons","David Cournapeau","t","s") )
        talks.append( ("Writing Optimized Extensions with Cython","Robert Bradshaw","t","s") )
        talks.append( ("Beyond Pure Python: Sage","William Stein","t","s") )
        talks.append( ("Advanced NumPy","Stefan van der Walt","t","s") )
        talks.append( ("Scientific GUI Applications with the Enthought Toolset","Eric Jones","t","s") )
        talks.append( ("Interactive Plots Using Chaco","Peter Wang","t","s") )
        talks.append( ("3-d Visualization using TVTK and Mayavi","Prabhu Ramachandran; Gael Varoquaux","k","s") )
        talks.append( ("Keynote","Alex Martelli","n","s") )
        talks.append( ("State of SciPy","Travis Vaught; Jarrod Millman","n","s") )
        talks.append( ("Exploring network structure, dynamics, and function using NetworkX","Aric Hagberg","n","s") )
        talks.append( ("Interval arithmetic: Python implementation and applications","Stefano Taschini","n","s") )
        talks.append( ("Experiences Using Scipy for Computer Vision Research","Damian Eads","n","s") )
        talks.append( ("The new NumPy documentation framework","Stefan Van der Walt","n","s") )
        talks.append( ("Matplotlib solves the riddle of the sphinx","Michael Droettboom","n","s") )
        talks.append( ("The SciPy documentation project","Joe Harrington","n","s") )
        talks.append( ("Sage: creating a viable free Python-based open source alternative to Magma, Maple, Mathematica and Matlab","William Stein","n","s") )
        talks.append( ("Pysynphot: A Python Re-Implementation of a Legacy App in Astronomy","Perry Greenfield","n","s") )
        talks.append( ("How the Large Synoptic Survey Telescope LSST is using Python","Robert Lupton","n","s") )
        talks.append( ("Real-time Astronomical Time-series Classification and Broadcast Pipeline","Dan Starr","n","s") )
        talks.append( ("Analysis and Visualization of Multi-Scale Astrophysical Simulations using Python and NumPy","Matthew Turk","n","s") )
        talks.append( ("Mayavi: Making 3D data visualization reusable","Prabhu Ramachandran; Gael Varoquaux","n","s") )
        talks.append( ("Finite Element Modeling of Contact and Impact Problems Using Python","Ryan Krauss","n","s") )
        talks.append( ("PyCircuitScape: A Tool for Landscape Ecology","Viral Shah","n","s") )
        talks.append( ("Summarizing Complexity in High Dimensional Spaces","Karl Young","n","s") )
        talks.append( ("UFuncs: A generic function mechanism in Python","Travis Oliphant","n","s") )
        talks.append( ("NumPy Optimization: Manual tuning and automated approaches","Evan Patterson","n","s") )
        talks.append( ("Converting Python functions to dynamically-compiled C","Ilan Schnell","n","s") )
        talks.append( ("unPython: Converting Python numerical programs into C","Rahul Garg","n","s") )
        talks.append( ("Implementing the Grammar of Graphics for Python","Robert Kern","n","s") )
        
        # talks.append( ("Astronomical data analysis","Perry Greenfield","t","s") )
        # talks.append( ("Bulding extensions with Numscons","David Cournapeau","t","s") )
        # talks.append( ("Writing optimized extensions with Cython","Robert Bradshaw","t","s") )
        # talks.append( ("Beyond pure python: Sage","William Stein", "t","s") )
        # talks.append( ("Advanced NumPy","Stefan van der Walt", "t" ,"s") )
        # talks.append( ("Scientific GUI applications with the Enthought Toolset","Eric Jones","t","s") )
        # talks.append( ("Interactive plots using Chaco"," Peter Wang","t","s") )
        # talks.append( ("3-d visualization using TVTK and Mayavi"," Prabhu Ramachandran; Gael Varoquaux", "t","s") )

        
    elif year == 2009:
        talks.append( ("Advanced topics in matplotlib","John Hunter","t","s") )
        talks.append( ("Symbolic computing with sympy","Ondrej Certik","t","s") )
        talks.append( ("Statistics with Scipy","Robert Kern","t","s") )
        talks.append( ("Cython","Dag Sverre Seljebotn","t","s") )
        talks.append( ("Using GPUs with PyCUDA","Nicolas Pinto","t","s") )
        talks.append( ("Designing scientific interfaces with Traits","Enthought","t","s") )
        talks.append( ("Mayavi/TVTK","Prabhu Ramachandran","t","s") )
        talks.append( ("Advanced numpy","David Cournapeau; Stefan van der Walt","t","s") )
        talks.append( ("Introductory to Scientific computing with Python","Gael Varoquaux; Stefan van der Walt; Christopher Burns; Mike Droettboom; Perry Greenfield; David Cournapeau; Eric Jones","n","s") )
        talks.append( ("Update on the core projects","Charles Harrison; Fernando Perez; John Hunter; David Cournapeau","k","s") )
        talks.append( ("Keynote: What to demand from a Scientific Computing Language -- Even if you don't care about computing or languages","Peter Norvig","n","s") )
        talks.append( ("nipy.timeseries: Neuroimaging time-series analysis","Ariel Rokem","n","s") )
        talks.append( ("Virtual reality: a tool for the highly quantitative study of animal behavior","Andrew Straw","n","s") )
        talks.append( ("Parallel Kernels: An Architecture for Distributed Parallel Computing","Nikunj Patel","n","s") )
        talks.append( ("PaPy: Parallel and distributed data-processing pipelines in Python","Marcin Cieslik","n","s") )
        talks.append( ("High-Performance Code Generation Using CorePy","Andrew Friedley","n","s") )
        talks.append( ("Sherpa: 1D/2D modeling and fitting in Python","Brian Refsdal","n","s") )
        talks.append( ("Multiprocess System for Virtual Instruments in Python","Brian D'Urso","n","s") )
        talks.append( ("ESPResSo++: A Python-controlled, Parallel Simulation Software for Soft Matter Research","Olaf Lenz","n","s") )
        talks.append( ("Sympy","Ondrej Certik","n","s") )
        talks.append( ("Python implementation of weno interpolation and reconstruction","Adrian Townsend","n","s") )
        talks.append( ("Writing Safer NumPy Extensions in C++ with Templates and TooN","Damian Eads","k","s") )
        talks.append( ("Keynote: Modeling of Materials with Python","Jonathan Guyer","n","s") )
        talks.append( ("The PyMca Application and Toolkit","Armando Sole","n","s") )
        talks.append( ("Implementation of automatic script recording and network control for Mayavi","Prabhu Ramachandran","n","s") )
        talks.append( ("Fast numerical computations with Cython","Dag Sverre Seljebotn","n","s") )
        talks.append( ("Fwrap: The Next-Generation Fortran-to-Python Interface Generator","Kurt Smith","n","s") )
        talks.append( ("PySAL: A Python Library for Spatial Analysis and Geocomputation","Serge Rey","n","s") )
        talks.append( ("Neutron Scattering Data Acquisition and Experiment Automation with Python","Piotr Zolnierczuk","n","s") )
        talks.append( ("Exploring the future of bioinformatics data sharing and mining with Pygr and Worldbase","Chris Lee","n","s") )
        talks.append( ("A full software stack for visualizing next-generation sequence information","Titus Brown","n","s") )
        talks.append( ("Pyclaw - The Evolution of Clawpack into Python","Kyle Mandli","n","s") )
        talks.append( ("NumPy and SciPy Documentation in 2009 and Beyond","Joe Harrington","n","s") )
        talks.append( ("Python in science and engineering education in India","Prabhu Ramachandran","b","s") )
        talks.append( ("Next challenges for Python in Science","Jarrod Millman","b","s") )
        talks.append( ("The view of the pioneers","John Hunter; Eric Jones; Charles Harrison; Fernando Perez; Prabhu Ramachandran","b","s") )
        talks.append( ("The view of the young generation","David Cournapeau; Pauli Virtanen; Gael Varoquaux; Stefan van der Walt","b","s") )
        talks.append( ("Python and Parallel computing","Michael Aivazis; Brian Granger; Nicolas Pinto; Gael Varoquaux","b","s") )
        talks.append( ("State of Python visualization tools","John Hunter; Prabhu Ramachandran; Peter Wang; Stefan van der Walt","b","s") )
        
        
        # talks.append( ("Advanced numpy","Stefan van der Walt; David Cournapeau", "t","s") )
        # talks.append( ("Advanced topics in matplotlib","John Hunter","t","s") )
        # talks.append( ("Symbolic computing with sympy","Ondrej Certik","t","s") )
        # talks.append( ("Statistics with Scipy","Robert Kern","t","s") )
        # talks.append( ("Cython","Dag Sverre Seljebotn","t","s") )
        # talks.append( ("Using GPUs with PyCUDA","Nicolas Pinto","t","s") )
        # talks.append( ("Designing scientific interfaces with Traits","Enthought","t","s") )
        # talks.append( ("Mayavi/TVTK","Prabhu Ramachandran","t","s") )
        
    elif year == 2010:
        talks.append( ("Intro to Python, IPython, NumPy, Matplotlib, SciPy, & Mayavi","Prabhu Ramachandran; Kadambari Devarajan; Christopher Burns","t","s") )
        talks.append( ("Matplotlib: beyond the basics","Ryan May","t","s") )
        talks.append( ("Advanced NumPy","Stefan van der Walt","t","s") )
        talks.append( ("Signals and Systems in Python","Gunnar Ristroph","t","s") )
        talks.append( ("High Performance and Parallel Computing in Python","Brian Granger","t","s") )
        talks.append( ("GPUs and Python: PyCuda, PyOpenCL","Andreas Kloeckner","t","s") )
        talks.append( ("Introduction to Traits","Corran Webster","t","s") )
        talks.append( ("Mayavi","Prabhu Ramachandran","t","s") )

    elif year == 2012:
        talks.append( ("CompuCell3D - Using Python to Understand Complexity of Living Cells, Tissues, Organs and Organisms","Maciej Swat","p","s") )
        talks.append( ("Fiber Optic Nanobiosensor","Adam Hughes","p","s") )
        talks.append( ("High end computations based on python including Genetic algorithm/Neural network/Fuzzy logic analysis on seismic attributes and AVA inversion to predict reservoir properties","Yudhvir Singh ","p","s") )
        talks.append( ("ImaGen: Generic library for 0D, 1D and 2D pattern distributions","James Bednar","p","s") )
        talks.append( ("MUSKETEER: A generator of high fidelity synthetic network data","Alexander Gutfraind","p","s") )
        talks.append( ("Open Source Tools for Solving Level Set Problems","Daniel Wheeler ","p","s") )
        talks.append( ("PyMC: Bayesian Statistical Modeling in Python","Christopher Fonnesbeck ","p","s") )
        talks.append( ("PyNE: Python for Nuclear Engineering","Anthony Scopatz ","p","s") )
        talks.append( ("Python interface to Magadascar","Sergey Fomel ","p","s") )
        talks.append( ("Running Python on Microsoft Windows Azure","Wenming Ye ","p","s") )
        talks.append( ("Stochastic Modeling and Comparisons of Mating Systems in Nematode Species","Vikas Kache ","p","s") )
        talks.append( ("The Continuing Development of a Physics Simulation Setup Framework","Eugene Dougherty ","p","s") )
        talks.append( ("The Reference Model for Disease Progression"," Jacob Barhak","p","s") )
        talks.append( ("Unlock: A Python-based framework for rapid development of practical brain-computer interface applications","Byron Galbraith","p","s") )
        talks.append( ("Using the Quantum Toolbox in Python to Investigate an Optomechanical Cavity QED System","James P Clemens","p","s") )

    elif year == 2013:
        talks.append( ("Organizing the SciPy Conference","Brett Murphy","b","s") )
        talks.append( ("PyData", "Leah Silen", "b","s") )
        talks.append( ("Reproducibility","Matthew McCormick; Katy Huff","b","s") )
        talks.append( ("Teaching scientific computing with Python","David Sanders","b","s") )
        talks.append( ("The Future of Array Oriented Programming","Jonathan Rocher","b","s") )
        talks.append( ("PyNE Updates","Anthony Scopatz","b","s") )
        talks.append( ("Python and Finance","Jason Wirth","b","s") )
        talks.append( ("NumFOCUS","Leah Silen","b","s") )
        talks.append( ("Python in Astronomy","Thomas Aldcroft","b","s") )
        talks.append( ("SciPy 2014","Jonathan Rocher; Andy Terrel","b","s") )
        talks.append( ("Collaborating and Contributing in Open Science","Jeffrey Spies","b","s") )
        talks.append( ("Matplotlib enhancement proposal discussion","Damon McDougall","b","s") )
        talks.append( ("PySide development planning and sprint kickoff","John Ehresman","b","s") )
        talks.append( ("Women in Scientific Computing: Discussion and Mixer","Kristen Thyng","b","s") )
        talks.append( ("Data access and munging tools for oceanographic and hydrological applications","Emilio Mayorga","b","s") )

        talks.append( ("3D Perception: Point cloud data processing and visualization","Pat Marion","p","s") )
        talks.append( ("A Python way to an undergraduate CFD course","Jaime Kardontchik","p","s") )
        talks.append( ("Basic Interactive Unix for Data Processing","Walker Hale","p","s") )
        talks.append( ("Basin-hopping and beyond: Global optimization and energy landscape exploration in molecular systems","Jacob Stevenson ; Victor Ruhle","p","s") )
        talks.append( ("Code as text: Open source in academia","Sergio Rey","p","s") )
        talks.append( ("Data Wrangling with the SheafSystem","David M. Butler","p","s") )
        talks.append( ("Dedalus: A Python-Based Spectral PDE Solver","Keaton J. Burns; Jeffrey S. Oishi; Geoffrey M. Vasil; Daniel Lecoanet; Eliot Quataert","p","s") )
        talks.append( ("Experimental Mathematics with Python: Calculating Lyapunov exponents of non-elastic billiard models","Alonso Espinosa ; David P. Sanders","p","s") )
        talks.append( ("G-mode Clustering Method applied to Asteroid Taxonomy","P. H. Hasselmann ; J. M. Carvano ;  D. Lazzaro","p","s") )
        talks.append( ("Hearing Assessment: Lessons learned developing a modular solution for audiometric testing","Robert D. Chambers ; William H. Finger ; Jesse A. Norris ; Cl","p","s") )
        talks.append( ("HTSQL - A Navigational Query Language For Relational Databases","Charles Tirrell ;  Clark Evans","p","s") )
        talks.append( ("IRLB, a fast partial SVD","Jim Baglama; Michael Kane","p","s") )
        talks.append( ("Managing Ensembles of Multi-Processor Jobs with Tex-MECS and PyLauncher","Michael Tobis; Victor Eijkhout","p","s") )
        talks.append( ("Mica: data-mining the Chandra archive for satellite operations","Jean M. Connelly; Thomas L. Aldcroft","p","s") )
        talks.append( ("Modeling elastic wave propagation using PyOpenCL","Ursula Iturraran-Viveros ; Miguel Molero","p","s") )
        talks.append( ("Navigating the Scientific Python Communities - the missing guide","Paul Ivanov","p","s") )
        talks.append( ("Peatland data analysis and simulation with Python","Andrew Reeve ; Claire Westervelt","p","s") )
        talks.append( ("Powering Recommendations with Distributed Computing using Python and MapReduce","Marcel Caraciolo ; Atapassar","p","s") )
        talks.append( ("PyDocX: Parsing Word documents in order to increase greater collaboration in collaborative writing","Samuel Portnow; Jason Ward; Jeff Spies","p","s") )
        talks.append( ("Scholarly: An open, freely accessible dataset of the academic citation network","Harry Rybacki,; Joshua Carp; Jeffery Spies","p","s") )
        talks.append( ("Self-documenting runtime: becoming omniscient with Contexture","Alexander Kouznetsov","p","s") )
        talks.append( ("Technical and social challenges in creating the Python ARM Radar Toolkit (Py-ART)","Jonathan Helmus ; Scott Collis","p","s") )
        talks.append( ("The UQ Foundation: Supporting the Right Scientific Tools for Reproducibility","Drew Marsden ; Michael McKerns ; Houman Owhadi ; Clint Scovel ; Tim Sullivan","p","s") )
        talks.append( ("The Use of Python in the Prompt Assessment of Global Earthquake Response (PAGER) System","Michael Hearne","p","s") )
        talks.append( ("Ureka: a distribution of Python & IRAF software for astronomy","James Turner ; Christine Slocum ; Sienkiewicz","p","s") )
        talks.append( ("Using Git to improve reproducibility & transparency","Toni Gemayel","p","s") )
        talks.append( ("Using Python to Study Rotational Velocity Distributions of Hot Stars","Gustavo Bragan-a ; Simone Daflon","p","s") )
        talks.append( ("UV-CDAT Re-sharable Analyses and Diagnostics (U-ReAD): a framework to create and share UV-CDAT plugins","Charles Doutriaux","p","s") )

    elif year == 2014:
        talks.append( ("SymPy: Symbolic math for Python","Aaron Meurer","p","s") )
        talks.append( ("Web-based Analysis and Visualization for Large Geospatial Datasets for Climate Scientists","Aashish Chaudhary","p","s") )
        talks.append( ("Scientific Computing with SciPy for Undergraduate Physics Majors","Bill Baxter","p","s") )
        talks.append( ("PySIMS: A Python library for ToF-SIMS analysis","Bob Moision","p","s") )
        talks.append( ("hyperopt-sklearn: A hyperparameter optimization framework for scikit-learn","Brent Komer","p","s") )
        talks.append( ("Python based pipeline for calibration and post-processing in Astronomical High-Contrast Imaging","Carlos Alberto Gomez Gonzalez","p","s") )
        talks.append( ("Building a Dynamic High Performing Particle Tracking Model","Christopher Barker","p","s") )
        talks.append( ("A new bridge to share your content with the world: NikIPy.","Damian Avila","p","s") )
        talks.append( ("Validated numerics in Python","David P. Sanders","p","s") )
        talks.append( ("PyCube: A python-based visualization tool for the NWP model on the cubed-sphere grid","Dongchan Joo","p","s") )
        talks.append( ("Python in X-ray Astronomy","Gerrit Schellenberger","p","s") )
        talks.append( ("Analyzing and Plotting Idealized WRF Simulations in Python","Gokhan Sever","p","s") )
        talks.append( ("Pyadisi - A Python package for animal locomotion studies","Isaac Yeaton","p","s") )
        talks.append( ("In with the old, In with the new: Matplotlib's role in a D3js world","Jake VanderPlas","p","s") )
        talks.append( ("Python cross-compilation and platform builds for HPC and scientific computing","Jean-Christophe Fillion-Robin","p","s") )
        talks.append( ("Python Coding of Geospatial Processing in Web-based Mapping Applications","Michael Nowak","p","s") )
        talks.append( ("How to open science by connecting the tools you use or develop to the scientist's workflow","Jeffrey Spies","p","s") )
        talks.append( ("An community collection of decoders for instrument-specific data formats","Joe Young","p","s") )
        talks.append( ("Investigating Stiffness Controls on Earthquake Behavior -- An Ideal Environment for Python Workflows","John Leeman","p","s") )
        talks.append( ("Scientific Knowledge Management with Web of Trails","Jon Riehl","p","s") )
        talks.append( ("Teaching Phase Transformations Using FiPy","Jonathan Guyer","p","s") )
        talks.append( ("Keeping Scientists Happy: Creating Easy to Install Scientific Python Packages.","Jonathan Helmus","p","s") )
        talks.append( ("PyGECoRe: Geometrically Exact Conservative Remapping tool for any grids in spherical geometry","Ki-Hwan Kim","p","s") )
        talks.append( ("Using Fatiando a Terra to solve inverse problems in geophysics","Leonardo Uieda","p","s") )
        talks.append( ("you're doing it wrong: the lack of reproducibility in statistical science, and how to fix it","Michael McKerns","p","s") )
        talks.append( ("The ANSS Comprehensive Earthquake Catalog and Tools","Mike Hearne","p","s") )
        talks.append( ("Platform to Enable Shared Scientific Computing Advances Research Assets (PESSCARA)","Panagiotis Korfiatis","p","s") )
        talks.append( ("Having your big-array cake and eating it.","Richard Hattersley","p","s") )
        talks.append( ("SimPEG: A framework for Simulation and Parameter Estimation in Geophysics","Rowan Cockett","p","s") )
        talks.append( ("Modeling the global shipping trade using a Python-based analysis stack","Shaun Walbridge","p","s") )
        talks.append( ("Making Medical Image Analysis Research Easier, Faster, and More Reproducible with IPython","Timothy Lee Kline","p","s") )
        talks.append( ("Integrating IPython into Large-Scale Development Environments","Zachary H. Jones","p","s") )

    elif year == 2015:
        talks.append( ("A Bioinformatic Pipeline to Search for Genetic Variants of Wood Frog Environmental Response Genes","Jordan Brooker","p","s") )
        talks.append( ("A Web-based Visualization Platform for Microbiome Metaproteomics","Sandip Chatterjee","p","s") )
        talks.append( ("Comparing and Evaluating Clustering Methods for Protein Simulations","Jan H. Meinke","p","s") )
        talks.append( ("Computational Astrophysical Hydrodynamics for Students","Michael Zingale","p","s") )
        talks.append( ("Detecting Carcinogenic Somatic Mutations Using Scikit-learn","Chak-Pong Chung","p","s") )
        talks.append( ("Developing Robust and Maintainable PyQt GUI Applications for Neutron Scattering at a Large DOE User Facility","Wenduo Zhou ; Ke An ; Jean-Christophe Bilheux ; Stephen D. Miller ; Peter F. Peterson","p","s") )
        talks.append( ("Development of Large Image Analysis Workflows in the Context ","Dhanannjay Djay Deo ; Brian Helba","p","s") )
        talks.append( ("Epithelial Tissue Simulation and with Initial Conditions Taken From In Vivo Images","Melvyn Drag","p","s") )
        talks.append( ("ESPResSo++: A Parallel Python Module for Soft Matter Simulations","Horacio Vargas Guzman ; Torsten Stuehn","p","s") )
        talks.append( ("MetOceanTrack: A Desktop GUI to Simulate The Dispersal of Invasive Species in Coastal and Continental Shelf Regions","Andre Lobato","p","s") )
        talks.append( ("Patient Signals - Building and Deploying Predictive Apps in Healthcare","Corey Chivers","p","s") )
        talks.append( ("Perceptual Colormaps in matplotlib with an Application in Oceanography","Kristen Thyng","p","s") )
        talks.append( ("Performance of PyCUDA (Python in GPU High Performance Computing)","Roberto Colistete Junior","p","s") )
        talks.append( ("Python Tool to Load, Process, and Plot Conductive Temperature Depth (CTD) data","Filipe Fernandes","p","s") )
        talks.append( ("Reassortment Primes Influenza for Ecotype Switches","Eric Ma","p","s") )
        talks.append( ("Relation: The Missing Container","James Larkin ; Scott James","p","s") )
        talks.append( ("Risk Analysis of Privacy Invasion in Social Network using Python with SciPy","Jun-Bum Park","p","s") )
        talks.append( ("rsfmodel - A Frictional Modeling Tool for Fault and Laboratory Data Analysis","John Leeman ; Ryan May","p","s") )
        talks.append( ("The Use of Python in the Large-Scale Analysis and Identification of Potential Antimicrobial Peptides","Shaylyn Scott","p","s") )
        talks.append( ("TLS Benchmarking with IPython","Christopher Niemira","p","s") )
        talks.append( ("Toolset and Workflow for Verification, Validation and Uncertainty Quantification in Large-scale Engineering Applications","Damon McDougall","p","s") )
        talks.append( ("Topological Data Analysis using Python","Dan Dickinson","p","s") )
        talks.append( ("Using Python and Jupyter Notebooks for a Biomedical Imaging Phenotyping Service","Brian Chapman ; John Roberts ; Stuart Schulthies","p","s") )
        talks.append( ("Using Python to Manage 800,000 WAAS Data Points per Second","Benjamin Potter","p","s") )
        talks.append( ("Using Self Organizing Maps to Visualize and Cluster High Dimensional Data","Richard Xie","p","s") )
        talks.append( ("Working with Matplotlib via PyQt/Qt Designer","Jean Bilheux ; Steve Miller ; Wenduo Zhou","p","s") )
        talks.append( ("An MR Spectroscopy Database Query and Visualization Engine as a Clinical Diagnostic Tool","Justin Foong","p","s") )
        talks.append( ("Coupling Geophysical Terminology and Package Development","Rowan Cockett","p","s") )
        talks.append( ("Creating a Real-Time Recommendation Engine using Modified K-Means Clustering and Remote Sensing Signature Matching Algorithms","David Lippa ; Jason Vertrees","p","s") )
        talks.append( ("Efficiently Exploring the Universe of Porous Media: Generating, Simulating, and Mutating Hypothetical Pseudo-materials","Alec Kaija","p","s") )
        talks.append( ("Fast Visualization and User Interfaces with PyQtGraph","Luke Campagnola","p","s") )
        talks.append( ("How Would You Like Your 'Tab' to Be?","Hyungtae Kim","p","s") )
        talks.append( ("Jupyter Notebook + SciPy = Rapid Fire Data Science","Jonathan Whitmore","p","s") )
        talks.append( ("MDSynthesis: a Python Package Enabling Data-driven Molecular Dynamics Research","David Dotson","p","s") )
        talks.append( ("OOF 3D: Modular Software Design in the Face of Major Feature Changes","Andrew Reid","p","s") )
        talks.append( ("Psi4: Open-Source Quantum Chemistry","Lori Burns","p","s") )
        talks.append( ("PyCO2...because we need to know.","Juliana Leonel ; Filipe Fernandes","p","s") )
        talks.append( ("Python Interfaces in Mantid","Steve Miller","p","s") )
        talks.append( ("PyUgrid: Handling NetCDF for Unstructured Grids","Chris Calloway","p","s") )
        talks.append( ("Scientific GUI Application Development Using Qt Designer and PyQt","Steve Miller ; Jean Bilheux ; Wenduo Zhou","p","s") )
        talks.append( ("SciPy and Real-time Big Data for Site Optimization","Winnie Cheng","p","s") )
        talks.append( ("Testing for serial correlation and non-stationarity of long time series after ARIMA modeling with SciPy and Statsmodels","Margaret Mahan","p","s") )

    elif year == 2016:
        talks.append( ("AESOP: Analysis of Electrostatic Structures Of Proteins","Rohith Mohan ; Reed Harrison ; Dimitrios Morikis","p","s") )
        talks.append( ("BETOC-PyCUDA : BayEsian Tools for Observational Cosmology with PyCUDA","Roberto Colistete Junior","p","s") )
        talks.append( ("Dengue Fever Surveillance in Asia Using Text Mining Cluster Analysis","Andrea Villanes","p","s") )
        talks.append( ("Pixel Level Segmentation of Coral Reef Photomosaics","Nick Cortale","p","s") )
        talks.append( ("1B Human Disease Cells + Fancy Camera + Python Stack = N New Disease Treatments","Blake Borgeson","p","s") )
        talks.append( ("Applications of Python at a NOAA/National Weather Service Weather Forecast Office","Paul Iniguez","p","s") )
        talks.append( ("Autocnet: A Library for Creating Sparse, Multi-Image Control Networks","Kristen Berry","p","s") )
        talks.append( ("Automated Data Reduction and Visualization for Neutron Single Crystal Diffractometer","Wenduo Zhou","p","s") )
        talks.append( ("Cell_tree2d: A High Performance Bounding Volume Hierarchy for Unstructured Meshes","Jay Hennen","p","s") )
        talks.append( ("Cloud Compute Cannon: Scalable, Scientific Computing for Anyone, Anywhere.","Dion Amago Whitehead","p","s") )
        talks.append( ("Comparison of Machine Learning Methods Applied to Birdsong Element Classification","David Nicholson","p","s") )
        talks.append( ("Condensed Matter Physics Meets Python via SageMath","Amit Jamadagni","p","s") )
        talks.append( ("Data Analysis Checkpointing","Horatio Voicu ; Pawel Penczek","p","s") )
        talks.append( ("Deciphering Epigenetic Signatures Underlying Transcript Type and Cell-type Specificity","Pamela Wu","p","s") )
        talks.append( ("Designing a Cloud Platform for Simulation Management","Daniel Wheeler","p","s") )
        talks.append( ("Fitting Human Decision Making Models using Python","Alejandro Weinstein ; Wael El-Deredy ; Steren Chabert ; Myriam Fuentes","p","s") )
        talks.append( ("Functional Uncertainty Constrained by Law and Experiment","Andrew Fraser","p","s") )
        talks.append( ("glumpy","Nicolas Rougier","p","s") )
        talks.append( ("Improving Food Accessibility via Spatial Clustering","Jennifer Flynn","p","s") )
        talks.append( ("It's All about the Features: Siamese Networks for a Lower Dimensional, Similarity Preserving Metric Space","Mason Victors","p","s") )
        talks.append( ("Molecular Modeling, 3D Visualization, and Distributed Computing in Jupyter Notebooks","Aaron Virshup","p","s") )
        talks.append( ("Neutron Imaging Analysis Using jupyter Notebook","Jean Bilheux","p","s") )
        talks.append( ("ObjArray: Better Integrating Python Objects with Numpy Arrays","Justin Fisher","p","s") )
        talks.append( ("Redefining the Breast Tumor Margin Utilizing a Computational Genomic Ruler of Tumor and Tumor-adjacent Normal Tissue","Amanda Ernlund","p","s") )
        talks.append( ("scikit-beam: Reusable and Composable Algorithms for the X-Ray, Neutron and Electron Sciences","Eric Dill","p","s") )
        talks.append( ("Single Pixel Adaptive Thermal Imaging on the Raspberry Pi","Scott Sievert","p","s") )
        talks.append( ("Storing Reproducible Results from Computational Experiments using Scientific Python Packages","Christian Schou Oxvig ; Thomas Arildsen ; Torben Larsen","p","s") )
        talks.append( ("The Formation of Massive Compact Quiescent Galaxies at z < 1","Nicholas Baeza Hochmuth","p","s") )
        talks.append( ("The Universality of CNN Distributed Representations","TJ Torres","p","s") )
        talks.append( ("Tools for High-throughput Computations of the Elastic Properties of Solids","Maarten De Jong ; Wei Chen ; Patrick Huck ; Donald Winston ; Anubhav Jain ; Kristin Persson ; Joseph Montoya","p","s") )
        talks.append( ("Towards CliMT 1.0","Joy Monteiro ; Rodrigo Caballero","p","s") )
        talks.append( ("Using Python to Create an Integrated Modular Framework for Atomistic Modeling of Molecular Structures","Steven C. Howell ; Joseph Curtis ; Emre Brookes","p","s") )
        talks.append( ("Validating Function Arguments in Python Signal Processing Applications","Patrick Pedersen ; Christian Oxvig ; Jan Ostergaard ; Torben Larsen","p","s") )
        talks.append( ("Web Data Analysis at the Spallation Neutron Source","Ricardo Ferraz Leal","p","s") )
        talks.append( ("Where Are the Diamonds? - Using a Giant Battery","Michael Mitchell ; Seogi Kang","p","s") )
        talks.append( ("Where Are the Diamonds? - Using Earth's Potentials","Dominique Fournier","p","s") )
        talks.append( ("Where Are the Diamonds? - Using Explosions","Brendan Smithyman","p","s") )
        talks.append( ("Where Are the Diamonds? - Using the Northern Lights","Gudni Karl Rosenkjaer","p","s") )

    elif year == 2017:
        talks.append( ("A New Approach of Combining Time-Series Forecasts Using Scipy and SKLearn","Eugene Chen","p","s") )
        talks.append( ("Hunting for Astrophysical Point Sources with Python","Siddharth Mishra Sharma","p","s") )
        talks.append( ("noWorkflow: Collecting, Managing, and Analyzing Provenance from Python Scripts","Joao Felipe Nicolaci Pimentel ; Juliana Freire ; Vanessa Braganholo ; Leonardo Murta","p","s") )
        talks.append( ("Python Data Processing System for Exploring Optical Properties of Materials with T-Rays","Alexander Mamrashev ; Lev Maximov ; Alexey Nazarov","p","s") )
        talks.append( ("3D Magnetic Modelling of Ellipsoidal Bodies","Diego Tomazella","p","s") )
        talks.append( ("Accuracy and Numerical Precision of Discrete Probability Distributions: A Comparison of SciPy, R, and a Numba/Cephes-Based Implementation.","Elliot Hallmark","p","s") )
        talks.append( ("An Overview of Bayesian Network Structure Learning","Jacob Schreiber","p","s") )
        talks.append( ("Automatic Small Angle Scattering Anisotropic Data Reduction","Ricardo Ferraz Leal","p","s") )
        talks.append( ("Bayesian Tools for Observational Cosmology of Type Ia Supernovae using PyCUDA","Roberto Colistete Jr","p","s") )
        talks.append( ("BespON: Extensible Config Files with Multiline Strings, Lossless Round-Tripping, and Hex Floats","Geoffrey Poore","p","s") )
        talks.append( ("Building a Monitoring Dashboard for In-Situ Space Weather Ion and Electron Spectrometers","Daniel da Silva","p","s") )
        talks.append( ("Building Better Radar Data, Block by Open Source Block","Scott Collis","p","s") )
        talks.append( ("Canvas-Style Interaction with Python: A D3 Interface to Phcpy in Jupyter","Jasmine Otto","p","s") )
        talks.append( ("Challenges of Numerical Analysis in Near-IR Echellogram Data Reduction","Andrew Colson","p","s") )
        talks.append( ("Competition and Bank Fragility","Blake Marsh","p","s") )
        talks.append( ("Creating a Python Cocoon around Legacy C Code","Molly Hardman ; Mary J. Brodzik ; Kevin Beam","p","s") )
        talks.append( ("Defining Features of mRNAs Regulated by Oncogenic eIF4E: A Pan-Survey Study Utilizing Predictive Technology to Define the Translational Landscape of eIF4E in Cancer.","Amanda Ernlund","p","s") )
        talks.append( ("Easy Steps for Accelerating Scientific Python","Robert Cohn ; Anton Malakhov","p","s") )
        talks.append( ("FigureFirst: A Layout Tool for Itterative Scientific Figure Construction","Theodore Lindsay ; Peter Weir ; Floris Van Breugel","p","s") )
        talks.append( ("Interactive HPC Gateways with Jupyter and Jupyterhub","Michael Milligan","p","s") )
        talks.append( ("Jupyter Notebooks for Neutron Radiography Data Processing Analysis","Jean Bilheux","p","s") )
        talks.append( ("Keep it Sympl: Representing Clouds and Turbulence with CHOMP","Jeremy McGibbon ; Christopher S. Bretherton","p","s") )
        talks.append( ("Looking for a Challenge? Lessons in Running International Grand Challenges","Brian Helba","p","s") )
        talks.append( ("Maintaining the Psi4 Ecosystem: Adventures in Building and Distribution","Lori Burns","p","s") )
        talks.append( ("Meteorologists and their CAPEs","John Leeman ; Ryan May","p","s") )
        talks.append( ("Network Analysis on Twitter #Gamergate 2+ Years Later","Emily Chao","p","s") )
        talks.append( ("NeuroLachesis: A Neuromorphic Framework","Georgios Detorakis ; Dan Barsever ; Emre Neftci","p","s") )
        talks.append( ("Parallel Analysis in MDAnalysis Using the Dask Parallel Computing Library","Mahzad Khoshlessan ; Oliver Beckstein ; Shantenu Jha ; Ioannis Paraskevakos","p","s") )
        talks.append( ("Pescador: A Stream Manager for Iterative Learning","Brian McFee","p","s") )
        talks.append( ("pyMolDyn: Identification, Structure, and Properties of Cavities/Vacancies in Condensed Matter and Molecules","Ingo Heimbach","p","s") )
        talks.append( ("PySeqArray: Data Manipulation of Whole-Genome Sequencing Variants in Python","Xiuwen Zheng","p","s") )
        talks.append( ("Python Implementation of Item Response Theory Calculations for Fitting Logistic Models","David Mashburn","p","s") )
        talks.append( ("Python Meets Systems Neuroscience: Affordable, Scalable and Open-Source Electrophysiology in Awake, Behaving Rodents.","Narendra Mukherjee","p","s") )
        talks.append( ("Scikit-beam: Python Data Analysis Library for X-ray, Neutron and Electron Data.","Sameera Abeykoon ; Thomas Caswell ; Daniel Allan ; Arman Akilic ; Staurt Campbell ; Kirstein van Dam ; Li Li","p","s") )
        talks.append( ("Secrets of Accelerating Scientific Python","Anton Malakhov ; Oleksandr Pavlyk ; Denis Nagorny","p","s") )
        talks.append( ("Software Transactional Memory in Pure Python","Dillon Niederhut","p","s") )
        talks.append( ("SPORCO: A Python Package for Standard and Convolutional Sparse Representations","Brendt Wohlberg","p","s") )
        talks.append( ("Storm Cell Tracking in Python","Mark Picel","p","s") )
        talks.append( ("Synthpy: A Synthetic Data Generation Library Built on the Python Scientific Computing Stack","Pamela Wu ; David Fenyo","p","s") )
        talks.append( ("The Intersection of Data Science, Machine Learning and Structural Engineering","David Najera","p","s") )
        talks.append( ("Unified Approach for Constructing Optimization Strategies Based on Python Linear Algebra Modules","Nadia Udler","p","s") )
        talks.append( ("Using Matplotlib and IPython In Neutron Scattering Experiment Data Reduction Software","Wenduo Zhou","p","s") )
        talks.append( ("Using Python to Generate 3D Wind Fields from Doppler Radars","Robert Jackson","p","s") )
        
    return talks
            
                    
                    
