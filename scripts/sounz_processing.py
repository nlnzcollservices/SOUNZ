#python 3
import sys
import urllib3
import shutil
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import re
import zipfile
import requests
import csv
from bs4 import BeautifulSoup
from pymarc import parse_xml_to_array,record_to_xml, Field 
from datetime import datetime as dt
from time import sleep
import os
from openpyxl import load_workbook
from urllib.parse import urlparse
# import xlsxwriter
import glob
from openpyxl import Workbook,load_workbook
import time
import datetime
from Pypdf2_text import parse_pdf
from pathlib import Path
from rosetta_sip_factory.sip_builder import build_single_file_sip



prod_api_key = "l8xx24faa60a17b14ef2947fb2e8222f8f24"#Production
sb_api_key = "l8xx5d24fa2ed92248dfb913722b8e3fb2d6"#Sandbox

file_folder = r"Y:\ndha\CS_legaldeposit\LD\one-time\sounz\2023 08"
number_of_files_skipped = 0
working_folder = p = Path(__file__).parents[1]
template_folder = os.path.join(working_folder,"assets","templates")
sip_folder = os.path.join(working_folder,"SIP")
report_folder = os.path.join(working_folder,"log","reports")
rosetta_folder = r"Y:\ndha\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\oneoff"
sounz_set = os.path.join(working_folder,"assets","SOUNZ_titles.txt")
try:
    with open(os.path.join(working_folder,"log","reports","sounz_titles.txt"),"r", encoding="utf-8") as f:
        data = f.read()
    my_titles = data.split("\n")[:-1]
except:

    my_titles = []
####################################################################################################################
NON_FILING_WORDS = ( 'the', 'an', 'a' )
#####################################################Current Time Class#####################################
class Times(object):

    """
    This class produces current time in different format
    Methods:

    numtime - %Y%m%d number format
    lettime - '%B %d, %Y' - letter format
    hyphtime - '%Y-%m-%d' - number with hyphen format
    underscore - '%Y_%m_%d')) - number with hyphen format
    timeconvert - '%d %B %Y' to '%Y%m%d')# converts input letter time to number time
    timestamp - timestamp from date as "%d %B %Y"
    converttoyear -'%d %B %Y'  to  %Y - converts input letter time to number time
    

    """


    def numtime():
        return str(dt.now().strftime( '%Y%m%d' )[2:] )# number format
 
    def lettime():
        return str(dt.now().strftime( '%B %d, %Y' ))# letter format

    def hyphtime():
        return str(dt.now().strftime( '%Y-%m-%d'))# number with hyphen format

    def underscore():
        return str(dt.now().strftime( '%Y_%m_%d'))# number with hyphen format

    def timeconvert(date):
        return dt.strptime(date, '%d %B %Y').strftime('%Y%m%d')# converts input letter time to number time

    def timestamp(date):
        return time.mktime(datetime.datetime.strptime(date, "%d %B %Y").timetuple())

    def converttoyear(date):
        return dt.strptime(date, '%d %B %Y').strftime('%Y')# converts input letter time to number time

         
        
####################################################Writings IN FILE Class################################################################
class SIPMaker():


# Volume = dcterms:bibliographicCitation
# Issue = dcterms:issued
# Number = dcterms:accrualPeriodicity
# Year = dc:date
# Month = dcterms:available
# Day = dc:coverage


    def __init__(self, title, subtitle, year ,filepath, mms ):

        """This class is used for making SIPs from existing foler
        Parameters:
            title (str) - title
            chron_i (str) - year

        Returns:
            None

    """

        
        self.flag = False
        self.title = title
        self.year = year
        self.mms = mms
        self.filepath = filepath
        self.subtitle = subtitle
        self.make_SIP()



    def make_SIP(self):
            """Method is used for making SIPs from description information

            Returns:
                bool  - True, if built, False otherwise
            """
            self.subtitle = self.subtitle.strip("()-:_,!").replace(" and ","").replace("for ","")
            subtitle_list = self.subtitle.split(" ")
            if len(subtitle_list) >3:
                subt_part = "_".join(subtitle_list[1:3])
            else:
                subt_part = subtitle_list[0]
            self.output_folder = os.path.join(sip_folder, self.title.replace(" ","_").replace("'","").replace(':',"_").replace("?","").replace("/","_").replace(",","_")+"_"+subt_part + "_"+self.year)
            if self.output_folder.startswith("for_"):
                self.output_folder = os.path.join(sip_folder, subt_part + "_"+self.year)
            print(self.filepath )
            print(self.output_folder)
            self.pref = "SOUNZ_"
            
            try:
                build_single_file_sip (
                                    ie_dmd_dict=[{"dc:date":self.year,  "dc:title":self.title}],
                                    filepath=self.filepath,
                                    generalIECharacteristics=[{"IEEntityType":"OneOffIE","UserDefinedA":"SOUNZ"}],
                                    objectIdentifier= [{"objectIdentifierType":"ALMAMMS", "objectIdentifierValue":self.mms}],
                                    accessRightsPolicy=[{"policyId":"200"}],
                                    digital_original=True,
                                    sip_title=self.pref+self.title+"_"+subt_part+"_"+self.year,
                                    output_dir=self.output_folder 
                                )
                print('Done')

                report_name = "report_sips"+str(dt.now().strftime("_%d%m%Y"))+".txt"
                with open(os.path.join(report_folder, report_name),"a") as f:
                    f.write("{}|{}|{}".format(self.title,self.mms, self.year))
                    f.write("\n")
                self.flag =  True


            except Exception as e:
                report_name = "report_sips"+str(dt.now().strftime("_%d%m%Y"))+".txt"
                with open(os.path.join(report_folder, report_name),"a") as f:
                    f.write("{}|{}|{}|Faild: {}".format(self.title,self.mms, self.year,str(e)))
                    f.write("\n")
                




def sip_checker(sippath):

    """Checks if met files are empty, or no_file
        Parameters:
        sippath(str) - path to sip
        Returns:
        flag(bool) - True if error found.  False if size of file is wrong or audio file or met file are empty.
    """
    flag = False

    if os.path.getsize(os.path.join(sippath, "content", "mets.xml")) == 0:
        print("Attention - empty met! {} ".format(sippath))
        flag = True
    if os.path.getsize(os.path.join(sippath, "content", "dc.xml")) == 0:
        print("Attention - empty  dc met! {}".format(sippath))
        flag = True
    if len(os.listdir(os.path.join(sippath,  "content", "streams"))) == 0:
        print("Attention - no file! {}".format(sippath))
        flag = True
    if len(os.listdir(os.path.join(sippath,  "content", "streams"))) >1:
        print("Attention - more then 1 file in the! {}".format(sippath))
        flag = True
    if len(os.listdir(os.path.join(sippath,  "content"))) == 0:
        print("Attention - streem folder! {}".format(sippath))
        flag = True
    else:
        myfilepath = os.path.join(sippath, "content", "streams", os.listdir(os.path.join(sippath,  "content", "streams"))[0])
        if os.path.getsize(myfilepath) == 0:
                logger.info("Attention - 0 byte file! {}".format(myfilepath))
                flag = True             
    return flag
    
        

#######################################################Creating bib data############################################################
def check_from_text_file():

    """Checking if all records in sounz.txt report are exist"""

    with open (text_file_path,"r",encoding="utf-8") as f:
        data = f.read()

    for line in data.split("\n")[:-1]:
        line_list = line.split("|")
        if len(line_list)>1:
            filename = line_list[0]
            mms = line_list[1]
            holding = line_list[2]
            item = line_list[3]
            url = r'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}'.format(mms)
            headers = {'content-type': 'application/xml'}
            parameters = {"apikey": api_key}
            r = requests.get( url, headers=headers, params = parameters, verify= False)
            
            if str(r.status_code).startswith("4"):
                print(line)
        else:
            print(line)

def parsing_bib_xml(metadata):

    """Parsing digital template and insert metadata to make bib xml
    
    Parameters:
        metadata(dict) - dictionary from parse_pdf method
    Returns:
        bib_xml(str) - bibliographic record in xml format
    """    
    flag_year = False
    full_xml_name = os.path.join(template_folder,"BIB_Sounz.xml")
    record = parse_xml_to_array(  full_xml_name )[0]

 
    # Field 245

    record['245']['c'] = metadata['author'] + '.'
    record['245']['a']= metadata['title'].rstrip(" ") + ' :'
    record['245']['b'] = metadata['subtitle'].rstrip(" ") + ' /'
      
    title_words = metadata["title"].split( ' ' )
    if title_words[0].lower() in NON_FILING_WORDS:# or title_words[0].lower() == "at":
                #offset = len( title_words[0] ) + 1
                if title_words[0] == "The":
                    record["245"].indicators = ['1', '4']
                if title_words[0] == "A":
                    record["245"].indicators = ['1', '2']
                if title_words[0] == "An":
                    record["245"].indicators = ['1', '3']
   
    
    
    #Field 264
    
    record['264']['c'] = "[{}]".format(metadata['year'].rstrip(" ").lstrip(" "))

    
    print ( record )
    bib_data = record_to_xml(record)
    bib_data = re.sub("b'<","<",str(bib_data))
    bib_data = str(bib_data)[:-1]
    bib_data = '<?xml version="1.0" encoding="UTF-8"?><bib><record_format>marc21</record_format><suppress_from_publishing>false</suppress_from_publishing>{}</bib>'.format(str(bib_data) )

    return ( bib_data)


def parsing_bib_xml_phys(metadata):
    """Parsing physical template and insert metadata to make bib xml
    
    Parameters:
        metadata(dict) - dictionary from parse_pdf method
    Returns:
        bib_xml(str) - bibliographic record in xml format
    """    

    flag_year = False
    full_xml_name = os.path.join(template_folder,"BIB_Sounz_phys.xml")
    print(full_xml_name)
    record = parse_xml_to_array(  full_xml_name )[0]

 
    # Field 245

    record['245']['c'] = metadata['author'] + '.'
    record['245']['a']= metadata['title'].rstrip(" ") + ' :'
    record['245']['b'] = metadata['subtitle'].rstrip(" ") + ' /'
      
    title_words = metadata["title"].split( ' ' )
    if title_words[0].lower() in NON_FILING_WORDS:# or title_words[0].lower() == "at":
                #offset = len( title_words[0] ) + 1
                if title_words[0] == "The":
                    record["245"].indicators = ['1', '4']
                if title_words[0] == "A":
                    record["245"].indicators = ['1', '2']
                if title_words[0] == "An":
                    record["245"].indicators = ['1', '3']

    
    #Field 264
    
    record['264']['c'] = "[{}]".format(metadata['year'].rstrip(" ").lstrip(" "))

    
    print ( record )
    bib_data = record_to_xml(record)
    bib_data = re.sub("b'<","<",str(bib_data))
    bib_data = str(bib_data)[:-1]
    bib_data = '<?xml version="1.0" encoding="UTF-8"?><bib><record_format>marc21</record_format><suppress_from_publishing>false</suppress_from_publishing>{}</bib>'.format(str(bib_data) )

    return ( bib_data)


###################################################Pushing to Alma sandbox##########################################################



def bib_creating( value , key  ): 
    """Makes record in alma and extracts mms id
    Parameters:
        value(str) - bib record in xml format 
    Returns:
        flag(bool) - True if something got wrong
        mms (str) - Alma mms id from new record

    """

    if key == "sb":
        api_key = sb_api_key
    if key == "prod":
        api_key = prod_api_key

    flag = False
    url = r'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs'
    headers = {'content-type': 'application/xml'}
    parameters = {"apikey": api_key}
    r = requests.post( url, headers=headers, data = value.replace("\\", "").replace('<datafield ind1=" " ind2="4" tag="264"><subfield code="c">copyrightcopyright</subfield></datafield>',""), params = parameters, verify= False)
    bib_grab = BeautifulSoup( r.text, 'lxml-xml' )
    try:
        mms = bib_grab.find( 'bib' ).find( 'mms_id' ).string  #looking for mms-id
        statement = 'MMS_ID: '+mms + "\n" +r.text +"\n"
        print( statement )
        with open ( "mms.txt", "a" ) as mms_file:
            mms_file.write( mms )
            mms_file.write("\n")
    except AttributeError as e:
        statement =  "Error during creating bib {}, {}.\n Data: {} \n".format ( type( e ),str( e ), value ) 
        print( statement )
        flag  = True
        mms = None
   
    return( mms, flag )

def create_po_line( values ,key ):

    """Makes PO_line

    Parameters:
        value(str) - bib record in xml format
    Returns:
        flag(bool) - True if po_line was not created
        pol (str) - Alma po_line number
    """
    if key == "sb":
        api_key = sb_api_key
    if key == "prod":
        api_key = prod_api_key
    flag = False
    url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines?apikey={}'.format(api_key)
    headers = {'content-Type':'application/xml'}
    r = requests.post( url, headers=headers, data = values )
    grab = BeautifulSoup( r.text, 'lxml-xml' )
    try:
        POL = grab.find( 'po_line' ).find( 'number' ).string#looking for po-line number  
        statement = 'posted: '+POL
        print ( statement )
       
    except AttributeError as e:
        statement = "Error during creating POL {}\t{}\t{}\n".format( values, type( e ),str( e ) )
        print(statement)
        POL = None
        flag = True
    return (POL, flag)  

def get_po_line(pol):

    """ Gets po_line xml via Alma API
    Parameters:
        pol(str) - po_line


    """

    flag = False
    url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines/{}?apikey={}'.format(pol, api_key)
    r = requests.get( url )
    print( '{}\t{}\n'.format( r, r.text ) )


def get_pid( pol , key ):

    """ Gets item pid via Alma API
    Parameters:
        pol(str) - po_line


    Returns:
        pid (str) - item pid    
        flag(bool) - True if error

    """
    if key == "sb":
        api_key = sb_api_key
    if key == "prod":
        api_key = prod_api_key
    flag = False
    url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines/{}?apikey={}'.format(pol, api_key)
    r = requests.get( url )
    print( '{}\t{}\n'.format( r, r.text ) )
    try:
        grab = BeautifulSoup( r.text, 'lxml-xml' )
        pid = grab.find( 'po_line' ).find( 'locations' ).find( 'location' ).find( 'copies' ).find( 'copy' ).find( 'pid' ).string  
        statement = "PID: {}".format( pid )
        print( statement )
    except AttributeError as e:
        statement =  "Error during getting pid {}\t{}\t{}\n".format( POL, type( e ),str( e ) ) 
        print( statement )
        pid = None
        flag = True
    return (pid, flag)



def receive_item( pol, pid, key ):

    """ Receives existing item via Alma API
    Parameters:
        pol(str) - po_line
        pid (st) - item pid

    Returns:
        statement(str) - Received or Not Received.    

    """
    if key == "sb":
        api_key = sb_api_key
    if key == "prod":
        api_key = prod_api_key
    flag = False
    url = 'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines/{}/items/{}?op=receive&apikey={}'.format( pol, pid, api_key )
    # print(url)
    values  = '<item />'
    headers = {  'Content-Type':'application/xml'  }
    r = requests.post( url, data = values, headers = headers )
    # print( '{}\n{}\n'.format(r, r.text ) )
    if len( r.text )>1000:  
        statement =  "Received\n"
        print(statement)
        return( "Received", flag)

    else:
            statement =  "Not able to receive {}\n".format( pol ) 
            print( statement )
            flag = True
            return( "Not Received", flag)


def checker(fn, bib_data, po_data, mms, pol_no, pid, flag_bib, flag_po, flag_pid, flag_receive ,key):

    """Checks flags and reruning failed part of the process

    Parameters:
        fn(str) - filename
        bib_data(str) - bib data as xml
        po_data(str) - po data as xml
        mms(str) - mms id
        pol_no(str) - po line
        pid (str) - item pid
        flag_bib(bool) - True if record was created
        flag_po(bool) - True if po was not done
        flag_pid(bool) - True if pid was not found
        flag_receive(bool) - true if item with pid was not recreived
    Returns:
        mms(str) - mms id
        pol_no(str) - po line
        pid (str) - item pid
        resp(str) - received item message

    """
    
    if flag_bib:
        print( "3. Creating bib record" )
        mms, flag_bib = bib_creating( bib_data, key )
        flag_bib = False
        print (mms)

    if not flag_bib and  flag_po:
        print( "4. Creating PO line" )
        po_data = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><po_line><owner desc="Central Acquisition Department">COL</owner>     <type desc="Print_Book - One Time">PRINTED_BOOK_OT</type><vendor desc="Sounz, Centre For NZ Music">SOUNZ</vendor><vendor_account>SOUNZ-LD</vendor_account><acquisition_method desc="Legal Deposit">LEGAL_DEPOSIT</acquisition_method><price><sum>0.00</sum><currency desc="New Zealand Dollar">NZD</currency></price><reporting_code>DIGISCORE</reporting_code><resource_metadata><mms_id>[MMS]</mms_id></resource_metadata><locations><location><quantity>1</quantity><library desc="Alexander Turnbull Library">ATL</library><shelving_location>ATL.DA</shelving_location><copies><copy><item_policy desc="Heritage">HERITAGE</item_policy></copy></copies></location></locations><material_type desc="Digital File">KEYS</material_type></po_line>'%( mms )   
        pol_no, flag_po = create_po_line( po_data, key)
        flag_po = False
        print( pol_no )

    if not flag_bib and not flag_po and flag_pid:
        print( "5. Getting pid" )
        pid, flag_pid =get_pid( pol_no , key )
        flag_pid = False
        print( pid )

    if not flag_bib and not flag_po and not flag_pid and flag_receive:
        print( "6. Receiving item" )
        resp, flag_receive = receive_item( pol_no, pid , key )  
        flag_receive = False      
    return( mms, pol_no, pid, resp )



######################################################START OF SCRIPT################################################################      

def sounz_routine(key):

    """Manages all the process of making digital and pysical record an aquisition part and writes the sounz.txt reports"""
    files = os.listdir( file_folder )
    files = files[number_of_files_skipped:]
    lines = []
    titles = []
    authors = []
    subtitles = []
    mmss = []
    if key == "sb":
        api_key = sb_api_key
    if key == "prod":
        api_key = prod_api_key
    with open(sounz_set,"r",encoding = "utf-8") as f:
        data = f.read()
    for line in data.split("\n")[:-1]:
        print(line)

        line_list = line.split("||")

        titles.append(line_list[0])
        subtitles.append(line_list[1])
        authors.append(line_list[2])
        mmss.append(line_list[3])




    for fl in files:
        dup_flag = False
        message_flag =True
        print("#"*50)
        print(os.path.join(fl))    
        if ".pdf" in fl:# and fl == "29307_dl copy.pdf":
            print("1. Parse pdf")
            my_dict = parse_pdf(os.path.join(file_folder, fl))
            for i,t in enumerate(titles):
                if  titles[i] == my_dict["title"]:
                    if (subtitles[i] == my_dict["subtitle"] and authors[i] == my_dict["author"]):
                        dup_flag = True
                        my_dup_mms = str(mmss[i])
                    elif (subtitles[i] == my_dict["subtitle"] or authors[i] == my_dict["author"]):
                        my_dict["message"] = my_dict["message"] + " Check for duplicate: " + mmss[i]
            if not dup_flag:
                if my_dict["title"] in titles and my_dict["subtitle"] in subtitles and my_dict["author"] in authors:
                    my_dict["message"] = my_dict["message"] + " Might be duplicated"
                if my_dict:
                    print("here")
                    print("2.1 Parse template for digital")
                    bib_data = parsing_bib_xml(my_dict)
                    print(bib_data)
                    mms, flag_bib = bib_creating( bib_data, key )
                    print(mms)
                    with open (os.path.join(template_folder, "PO_line.xml"),"r") as polfl:
                        po_data = polfl.read()
                    po_data = re.sub(r"\[MMS\]", mms, po_data)
                    pol_no, flag_po = create_po_line( po_data, key )
                    print( "5.1 Getting pid" )
                    pid, flag_pid =get_pid( pol_no, key )
                    #print( "6.1 Receiving item" )
                    # resp,flag_receive = receive_item( pol_no, pid, key)
                    # if flag_bib or flag_po or flag_pid or flag_receive:
                    #     mms, pol, pid, resp = checker(fn, bib_data, po_data, mms, pol_no, pid, flag_bib, flag_pol, flag_pid, flag_receive)
                    # print(working_folder)
                    print( "7.1 Writing ")
                    with open(os.path.join(working_folder,"log","reports","sounz_{}.txt".format(Times.underscore())),"a", encoding="utf-8") as f:
                        f.write(fl+"|"+mms+"|"+pol_no+"|"+pid+"|"+ "|||"+my_dict["title"]+"|"+my_dict["message"]+"\n")
                    print("2.2 Parse template for physical")
                    bib_data = parsing_bib_xml_phys(my_dict)
                    mms, flag_bib = bib_creating( bib_data, key)
                    print(mms)
                    with open (os.path.join(template_folder, "PO_line_phys_nl.xml"),"r") as polfl:
                        po_data = polfl.read()
                    po_data = re.sub(r"\[MMS\]", mms, po_data)
                    pol_no_nl, flag_po = create_po_line( po_data , key)
                    print( "5.2.1 Getting pid for physical Nat Lib" )
                    pid_nl, flag_pid =get_pid( pol_no_nl, key )
                    #print( "6.2.1 Receiving item for physical Nat Lib" )
                    # resp,flag_receive = receive_item( pol_no_nl, pid_nl, key )
                    # if flag_bib or flag_po or flag_pid or flag_receive:
                    #     mms, pol_nl, pid_nl, resp = checker(fn, bib_data, po_data, mms, pol_no_nl, pid_nl, flag_bib, flag_pol, flag_pid, flag_receive)
                    # print(working_folder)
                    with open (os.path.join(template_folder, "PO_line_phys_atl.xml"),"r") as polfl:
                        po_data = polfl.read()
                    po_data = re.sub(r"\[MMS\]", mms, po_data)
                    pol_no_atl, flag_po = create_po_line( po_data, key )
                    print( "5.2.2 Getting pid for physical ATL" )
                    pid_atl, flag_pid =get_pid( pol_no_atl, key)
                    # print( "6.2.2 Receiving item for physical ATL" )
                    # resp,flag_receive = receive_item( pol_no_atl, pid_atl,key )
                    # if flag_bib or flag_po or flag_pid or flag_receive:
                    #     mms, pol_atl, pid_atl, resp = checker(fn, bib_data, po_data, mms, pol_no_atl, pid_atl, flag_bib, flag_pol, flag_pid, flag_receive)
                    # print(working_folder)   
                    print( "7. Writing ")
                    with open(os.path.join(working_folder,"log","reports","sounz_phys_{}.txt".format(Times.underscore())),"a", encoding="utf-8") as f:
                        f.write(fl+"|"+mms+"|"+pol_no_nl+"|"+pid_nl+"|"+pol_no_atl+"|"+pid_atl+"|"+my_dict["title"]+"|"+my_dict["message"]+"\n")
                
                # else:
                    # with open(text_file_path,"a") as f:
                    #     f.write(fl+"||||could not make a record"+"\n")
                    if key=="prod":
                        with open(os.path.join(working_folder,"log","reports","sounz_titles.txt"),"a", encoding="utf-8") as f:
                            f.write(my_dict["title"]+"\n")
                    if key =="prod":
                        with open(sounz_set,"a",encoding= "utf-8") as f:
                            f.write(my_dict["title"] + "||"+my_dict["subtitle"]+"||"+my_dict["author"]+"||"+mms+"\n")
            else:
                with open(os.path.join(working_folder,"log","reports","sounz_phys_{}.txt".format(Times.underscore())),"a", encoding="utf-8") as f:
                    f.write(fl+"| | | | | |"+my_dict["title"]+"|"+my_dict["message"]+ r"Dup found {}".format(my_dup_mms) + "\n")


    print("8. Reading text file")
    with open (text_file_path,"r") as f:
        data = f.read()

    for line in data.split("\n")[:-1]:
        if not "dup found " in line:
            line_list = line.split("|")
            if len(line_list)>1:
                filename = line_list[0]
                mms_id = line_list[1]
                po_line = line_list[2]
                pid = line_list[3]
                pol_no_nl = line_list[2]
                pid_nl = line_list[3]
                fl = line_list[0]
                fl_path = os.path.join(file_folder,fl)
                my_dict = parse_pdf(fl_path)
                print("9. Making sip")
                my_sip =  SIPMaker(title = my_dict["title"], subtitle = my_dict["subtitle"], mms = mms_id, year = my_dict["year"] ,filepath = os.path.join(file_folder,fl))
                if my_sip.flag:
                    print(fl, " - sip done")
                else:
                    print(fl, " - failed to build sip")
    if key == "prod":
        print("Check SIPs and copy")
        for sip in os.listdir(sip_folder):
            sip_path = os.path.join(sip_folder, sip)
            if not sip_checker(sip_path):
                shutil.move(sip_path, rosetta_folder)
            else:
                print("Check SIP - ",sip_path)


##########################################SETTINGS##############################################################    
#use this for updates text_file_path = os.path.join(working_folder,"log","reports","sounz_phys_{}.txt".format(Times.underscore())) 
text_file_path = os.path.join(working_folder,"log","reports","sounz_{}.txt".format(Times.underscore()))    

print(text_file_path)



def main():
    my_key = "prod"
    if my_key == "sb":
        print("Working in SandBox")
    if my_key == "prod":
        print("Working in Production")
    for sip in os.listdir(sip_folder):
        sip_path = os.path.join(sip_folder, sip)
        shutil.rmtree(sip_path)

    sounz_routine(my_key)
    
if __name__ == '__main__':
    main()

