import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
import os

DIR = "/home/pi" #os.environ["HOME"]

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(DIR + '/.ssh/task_list.json', scope)
client = gspread.authorize(creds)
sheet = client.open('To Do Demo')
sheet_instance = sheet.get_worksheet(0)


def get_tasks():
	#print(sheet_instance.col_count)
	#print(sheet_instance.cell(col=3,row=2))  # get the value at the specific cell

	# get all the records of the data
	col_name = sheet_instance.cell(col=1,row=1).value
	records_data = sheet_instance.get_all_records()
	#print(records_data)

	# return a simple array
	tasks = []
	for task in records_data:
		t = {
			"task" : task["Task"], 
			"priority" : task["Priority"], 
		}
		try:
			t["priority"] = int(t["priority"])
		except ValueError:
			t["priority"] = 999
		tasks.append(t)
	sorted_tasks = sorted(tasks, key=lambda k: k['priority']) 
	#return an array of strings.
	return list(o["task"] for o in sorted_tasks)

if __name__ == "__main__":
	tasks = get_tasks()
	print(tasks)
