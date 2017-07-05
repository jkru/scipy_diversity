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
        talks.append( ("Astronomical data analysis","Perry Greenfield","t","s") )
        talks.append( ("Bulding extensions with Numscons","David Cournapeau","t","s") )
        talks.append( ("Writing optimized extensions with Cython","Robert Bradshaw","t","s") )
        talks.append( ("Beyond pure python: Sage","William Stein", "t","s") )
        talks.append( ("Advanced NumPy","Stefan van der Walt", "t" ,"s") )
        talks.append( ("Scientific GUI applications with the Enthought Toolset","Eric Jones","t","s") )
        talks.append( ("Interactive plots using Chaco"," Peter Wang","t","s") )
        talks.append( ("3-d visualization using TVTK and Mayavi"," Prabhu Ramachandran; Gael Varoquaux", "t","s") )

    elif year == 2009:
        talks.append( ("Advanced numpy","Stefan van der Walt; David Cournapeau", "t","s") )
        talks.append( ("Advanced topics in matplotlib","John Hunter","t","s") )
        talks.append( ("Symbolic computing with sympy","Ondrej Certik","t","s") )
        talks.append( ("Statistics with Scipy","Robert Kern","t","s") )
        talks.append( ("Cython","Dag Sverre Seljebotn","t","s") )
        talks.append( ("Using GPUs with PyCUDA","Nicolas Pinto","t","s") )
        talks.append( ("Designing scientific interfaces with Traits","Enthought","t","s") )
        talks.append( ("Mayavi/TVTK","Prabhu Ramachandran","t","s") )
        
    elif year == 2010:
        talks.append( ("Intro to Python, IPython, NumPy, Matplotlib, SciPy, & Mayavi","Prabhu Ramachandran; Kadambari Devarajan; Christopher Burns","t","s") )
        talks.append( ("Matplotlib: beyond the basics","Ryan May","t","s") )
        talks.append( ("Advanced NumPy","Stefan van der Walt","t","s") )
        talks.append( ("Signals and Systems in Python","Gunnar Ristroph","t","s") )
        talks.append( ("High Performance and Parallel Computing in Python","Brian Granger","t","s") )
        talks.append( ("GPUs and Python: PyCuda, PyOpenCL","Andreas Kloeckner","t","s") )
        talks.append( ("Introduction to Traits","Corran Webster","t","s") )
        talks.append( ("Mayavi","Prabhu Ramachandran","t","s") )

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

    return talks
            
                    
                    
