import PyPDF2
import re
import os
import requests
from datetime import date

current_year = date.today().year
my_instrument_list = []
file_folder = r"Y:/ndha/CS_legaldeposit/LD/one-time/sounz/2022 11"
sounz_instruments = ['flute', 'piano', 'solo', 'voice', 'guitar', 'viola', 'violoncello', 'jenny', 'cello', 'oboe', 'brass', 'quintet', 'trumpet', 'horn', 'f', 'tenor', 'saxophone', 'orchestra', 'elegy',  'vocalist',  'woman',  'hath', 'soprano', 'small', 'kiri', 'palmer', 'violin', 'chamber', 'cutwork', 'jazz', 'fusion', 'ensemble', 'string', 'quartet']
def cleaned(title):
	"""
	This function is cleaning script from wrong characters

	Parameters:
		title(str) - string for cleaning
	Returns:
		title (str) - cleaned sting

	"""


	title = title.replace("Õ","'").replace("ß","fl").replace("©",'')#.replace("!","")
	return title

def parse_pdf ( file_path):
	"""Parsing pdf and extracting title, subtitle, year and author info. Making message if sometning could not extracted.
	Parameters:
		file_path(string) - pdf path
	Returns:
		dictionary(dict) - with following metadata 		({"title":title, "subtitle":subtitle, year":copyright_year,"author":copyright_holder,"message":message})

	"""

	copyright_holder = None
	copyright_year = None
	copyrate_statement = None
	autor = None
	title = None
	subtitle = None
	message= ""
	pdf_file = open(file_path, 'rb')
	read_pdf = PyPDF2.PdfFileReader(pdf_file)
	number_of_pages = read_pdf.getNumPages()

	page0 = read_pdf.getPage(0)
	page1 = read_pdf.getPage(1)
	page_content0 = page0.extractText().split('\n')
	page_content1 = page1.extractText().split('\n')
	page_content1_string = " ".join(page_content1)
	title = page0.extractText().split("Thank you")[0].replace("\n","").replace("  "," ").lstrip(" ").rstrip(" ")
	# print("Title: ", title)
	for ind in range(len(page_content0)):

		if "©" in page_content0[ind]:

			copyright_statement  = page_content0[ind]
			# print(copyrate_statement)
			for cop in copyright_statement.split(" "):
				if cop.strip("().rev ").isdigit():
					copyright_year = str(cop).strip("()rev")
			copyright_holder = copyright_statement.split(copyright_year)[1].lstrip(" )")
			# print(copyright_year)
			# print(copyright_holder)
		if "for " in page_content0[ind] and not "for New" in page_content0[ind] :
			subtitle = page_content0[ind].lstrip(" ").rstrip(" ")
			# print(subtitle)
			if copyright_holder:
				subtitle = subtitle.replace(copyright_holder,"").rstrip(" ").lstrip("")
	if cleaned(subtitle) in cleaned(title):
		message = " Check title"

	print(copyright_holder)
	print(copyright_year)
	if not copyright_year:
		message += " Check year"
	if not copyright_holder:
		message += " Check author"
		copyright_holder = ""
	print(message)
	try:
		copyright_year = cleaned(copyright_year)
	except:
		copyright_year = str(current_year)

	try:
		return ({"title":cleaned(title), "subtitle":cleaned(subtitle), "year":copyright_year,"author":cleaned(copyright_holder),"message":message})
	except:
		None

def get_mms_by_sru(title):
	""" This heler function checking titles if there is archived something already"""
	q_title = title.replace(" ","%20")
	url="https://ndhadeliver.natlib.govt.nz/delivery/sru?version=1.2&operation=searchRetrieve&recordPacking=xml&startRecord=0&query=IE.dc.title={}&maximumRecords=10&recordSchema=DC&maximumRecords=100".format(q_title)
	r = requests.get(url)
	print(r.text)

def main():

	files = os.listdir( file_folder )
	for fl in files:
		print(fl)    
		if ".pdf" in fl:
			my_dict = parse_pdf(os.path.join(file_folder, fl))
			print(my_dict["title"])
			print(my_dict["subtitle"])




if __name__ == '__main__':
	main()

