import sys
sys.path.insert(0, )
from alma_tools import AlmaTools

my_api = AlmaTools("sb")


mms_ids = ["919266429402836","9919266427602836"]
po_lines = ["POL-195825","POL-195847"]
print(len(mms_ids))
print(len(po_lines))
for i,mms_id in enumerate(mms_ids):
	print("#"*50)
	print(mms_id)
	print(po_lines[i])
	new_item_data = None
	my_api.get_holdings(mms_id)
	print(my_api.xml_response_data)
	holding_ids = re.findall(r"<holding_id>(.*?)</holding_id>",my_api.xml_response_data)
	print("holding id")
	print(holding_ids)
	for holding_id in holding_ids:
		item_count=0
		my_api.get_items(mms_id,holding_id,{"limit":"100"})
		try:
			item_count = re.findall(r'_count="(.*?)">',my_api.xml_response_data)[0]
		except:
			item_count = 0
		for i in range((int(item_count)//100)+2):
			my_api.get_items(mms_id,holding_id,{"limit":"100"})#,"offset":100*i})
			items = re.findall(r"<pid>(.*?)</pid>",my_api.xml_response_data)
			print("items")
			print(items)
			for item in items:
				my_api.get_item(mms_id,holding_id, item)
				# print(my_api.xml_response_data)
				if str(my_api.status_code).startswith("2"):
					item_data = my_api.xml_response_data
					#descr = re.findall(r"<description>(.*?)</description>", my_api.xml_response_data)[0]
					# if descr in designations:
					# 	if descr not in design2:
					# 		print(descr)
					# 		my_api.create_item(mms_id2, holding_id2, my_api.xml_response_data)
					# 		print(my_api.status_code)
					# 		if str(my_api.status_code).startswith("2"):
					#item_data = str(my_api.xml_response_data)
					new_item_data = item_data.replace('<committed_to_retain desc="Yes">true</committed_to_retain>','<committed_to_retain desc="No">false</committed_to_retain>')
					print("Updating item")
					my_api.update_item(mms_id,holding_id, item, new_item_data)
					print("Deleting item")
					my_api.delete_item(mms_id,holding_id, item)
					print(my_api.xml_response_data)
					# print( mms_id, descr, my_api.status_code)
	if holding_ids !=[]:
		"Deleting holdings"
		my_api.delete_holding(mms_id,  holding_id)
		print(my_api.xml_response_data)
	print("Deleting bib")
	my_api.delete_bib(mms_id)
	print(my_api.xml_response_data)
	print("Getting po_line")

	my_api.get_po_line(po_lines[i])
	po_data= my_api.xml_response_data.replace(mms_id,"")
	print(po_data)
	print("Removing mms from po_line")
	my_api.update_po_line(po_lines[i], po_data)
	print(my_api.xml_response_data)
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("Removing pol")
	my_api.delete_po_line(po_lines[i],{"reason":"TECHNICAL_ISSUES","override":True})

	print(my_api.xml_response_data)
	if new_item_data:
		print("$"*50)
		print("Second time")
		new_item_data = new_item_data.replace(po_lines[i],"")
		print("Removing pol from item")
		my_api.update_item(mms_id,holding_id, item, new_item_data)
		print("Delete item")
		my_api.delete_item(mms_id,holding_id, item)
		print("Delee holding")
		my_api.delete_holding(mms_id,  holding_id)
		print(my_api.xml_response_data)
		print("delete bib")
		my_api.delete_bib(mms_id)
		print(my_api.xml_response_data)