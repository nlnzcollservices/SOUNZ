import PyPDF2
import re
import os
import requests
from datetime import date
import spacy
current_year = date.today().year
my_instrument_list = []
file_folder = r"Y:\ndha\pre-deposit_prod\LD_working\SOUNZ\tests\pypdf_text_test\files"
sounz_instruments = ['flute', 'piano', 'solo', 'voice', 'guitar', 'viola', 'violoncello', 'jenny', 'cello', 'oboe', 'brass', 'quintet', 'trumpet', 'horn', 'f', 'tenor', 'saxophone', 'orchestra', 'elegy',  'vocalist',  'woman',  'hath', 'soprano', 'small', 'kiri', 'palmer', 'violin', 'chamber', 'cutwork', 'jazz', 'fusion', 'ensemble', 'string', 'quartet']

def extract_name(text):


	nlp = spacy.load('en_core_web_sm')

	# Analyze the text using the NER model
	doc = nlp(text)

	# Find the name in the analyzed text
	name = ""
	for ent in doc.ents:
	    if ent.label_ == 'PERSON':
	        name = ent.text
	        break
	return name

def clean_content(text):

	elements = ["Thank you for supporting the music of New Zealand composers.","For each score purchased a commission is paid to the composer.","You can further support New Zealand music by reporting performances of this work to: SOUNZ Centre for New Zealand Music sounz.org.nz and Australasian Performing Right Association, APRA, apra.co.nz.","No part of this score may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical, copying, recording or otherwise, without the prior permission of the Centre for New Zealand Music Trust or the appropriate copyright holder."]
	new_text =[]
	for el in elements:
		for i,e in enumerate(text):
			if el in e:	
				text[i] = text[i].replace(el,"")

	for elem in  text:
		elem = elem.replace("\u2028","")
		if "\xa0" in elem:
			print("here3")
			el_list = elem.split("\xa0")
			for wrd in el_list:
				if wrd!="":

					new_text += [wrd.rstrip(" ").lstrip(" ")]
		else:
			if elem.strip(" ") != "":
				new_text.append(elem.rstrip(" ").lstrip(" "))

	text = list(new_text)
	new_text = []	
	for el in text:
		if "for" in el:
			new_text.append(el.split("for")[0])
			new_text.append("for" + el.split("for")[-1])
		else:
			if el.strip(" ")  != "":
				new_text.append(el)
	text = list(new_text)
	new_text = []	
	for el in text:
		if el!= "":
			new_text.append(el)


	return new_text

def cleaned(title):
	"""
	This function is cleaning script from wrong characters

	Parameters:
		title(str) - string for cleaning
	Returns:
		title (str) - cleaned sting

	"""


	title = title.replace("Õ","'").replace("ß","fl").replace("©",'').rstrip(" ").lstrip(" ").replace("   ","").replace("  "," ").replace(" ","").replace("ﬂ","fl").replace("\u2028","")
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
	subtitle_flag = False
	message= ""
	pdf_file = open(file_path, 'rb')
	read_pdf = PyPDF2.PdfReader(pdf_file)
	number_of_pages = len(read_pdf.pages)

	page0 = read_pdf.pages[0]
	page_content0 = page0.extract_text().split('\n')
	print(page_content0)
	page_content0 = clean_content(page_content0)

	page1 = read_pdf.pages[1]

	page_content1 = page1.extract_text()
	print(page_content1)


	title = page0.extract_text().split("Thank you")[0].replace("\n","").replace("  "," ").lstrip(" ").rstrip(" ")
	# print("Title: ", title)
	copyright_index = None
	copyright_flag = False
	for ind,e in enumerate(page_content0):

		if "©" in e:
			copyright_flag = True
			print("here1")
			copyright_index = int(ind)
			copyright_statement  = str(page_content0[ind])
			print(copyright_statement)

			for cop in copyright_statement.split(" "):
				if cop.strip("().rev ").isdigit():
					copyright_year = str(cop).strip("()rev")
			copyright_holder = copyright_statement.split(copyright_year)[1].lstrip(" )")

	if copyright_flag:
		print("here1")
		for ind,e in enumerate(page_content0):
			if page_content0[ind].startswith("for") and not subtitle_flag:
				if not page_content0[ind].split(" ")[1][0].isupper():
					if copyright_index>ind:
						subtitle = " ".join(page_content0[ind:copyright_index])
					else:
						subtitle=page_content0[ind]
					subtitle_flag = True
		if not subtitle_flag:
			for ind,e in enumerate(page_content0):
				if page_content0[ind].startswith("for") and not subtitle_flag:
					if copyright_index>ind:
						subtitle = " ".join(page_content0[ind:copyright_index])
					else:
						subtitle=page_content0[ind]

	else:
		print("here2")
		for ind,e in enumerate(page_content0):
			if page_content0[ind].startswith("for") and not subtitle_flag:

				subtitle=page_content0[ind]
				subtitle_flag = True

	print(subtitle)
	print(subtitle_flag)
	if copyright_holder:
		if copyright_holder in title:
			title = " ".join(page_content0[copyright_index+1:])

	else:
		copyright_holder = extract_name(subtitle)
		print(copyright_holder)
		subtitle = subtitle.replace(copyright_holder,"").replace("  ","").lstrip(" ").rstrip(" ")


	# if "!" in title or "!" in subtitle:
	# 	message = "Check if title of subtitle contains ! or missed 'ff'"

	try:
		title = title.replace(copyright_holder,"")
	except:
		pass
	try:
		title = title.replace(copyright_year,"")
	except:
		pass
	try:
		title = title.replace(subtitle,"")
	except:
		pass
	try:
		copyright_year = cleaned(copyright_year)
	except:
		try:
			copyright_year = re.findall(r'\b\d{4}\b', page_content1)[0]
		except:

			print("No year!!!")
			quit()
			#if script failed here, you can process this file individually and set copyright year here
			# comment quit() and uncoment
			#copyright_year = "2017"
	if not subtitle:
		message = "Check subtitle"
		subtitle = ""
	if cleaned(subtitle) in cleaned(title):
		message = " Check title"

	if not copyright_year:
		message += " Check year"
	if not copyright_holder:
		message += " Check author"
		copyright_holder = ""
	if "arranged" in copyright_holder:
		subtitle = "arranged " + subtitle
		copyright_holder = copyright_holder.replace("arranged","").rstrip(" ").lstrip(" ")



	print ({"title":cleaned(title), "subtitle":cleaned(subtitle), "year":copyright_year,"author":cleaned(copyright_holder),"message":message})
	return ({"title":cleaned(title), "subtitle":cleaned(subtitle), "year":copyright_year,"author":cleaned(copyright_holder),"message":message})
	
	


def main():

	filefolder = "Y:\ndha\pre-deposit_prod\LD_working\SOUNZ\tests\pypdf_text_test\files"

	files = os.listdir( file_folder )
	for fl in files:
		print(fl)    
		if ".pdf" in fl:
			my_dict = parse_pdf(os.path.join(file_folder, fl))
			print(my_dict["title"])
			print(my_dict["subtitle"])




if __name__ == '__main__':
	main()

