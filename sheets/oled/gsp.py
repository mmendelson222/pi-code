import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
import os

DIR = os.environ["HOME"]

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(DIR + '/credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open('To Do Demo')
sheet_instance = sheet.get_worksheet(0)


def get_tasks():

	#print(sheet_instance.col_count)
	#print(sheet_instance.cell(col=3,row=2))  # get the value at the specific cell

	# get all the records of the data
	col_name = sheet_instance.cell(col=1,row=1).value
	records_data = sheet_instance.get_all_records()

	#with open(DIR + '/todo.json', "a") as json_file:
	#	json_file.write(json.dumps(records_data, indent=2))
	
	# return a simple array
	tasks = []
	for task in records_data:
		tasks.append(task[col_name])
	return tasks
