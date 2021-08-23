import hashlib
import requests
import json
import gspread
from datetime import datetime

spreadsheet_key = '1Ud-UnGvsSFwrUZu8fKktKHDaK38y_ubLh07AS57AEKg'; # ключ таблицы, в которой работаем
gc = gspread.service_account(filename = 'credentials.json')
sh = gc.open_by_key(spreadsheet_key)
ws = sh.sheet1
registrations_file = '/var/www/u1417944/data/www/nashagai.xyz/registrations.json' #файл с данными после регистрации. Последний апдейт 08.07 12:38

def get_ids():  #Создаём список id
	user_ids = []
	J_users = ws.col_values(10)
	P_users = ws.col_values(16)
	for i in range(max(len(J_users), len(P_users))):
		if J_users[i] != '':
			user_ids.append(J_users[i])
		else:
			user_ids.append(P_users[i])
	return user_ids[1:]

def open_file():
	with open(registrations_file, 'r') as f:
		reg_data = json.load(f)
	now = datetime.now()
	dt_string = now.strftime("%d-%m %H.%M.%S")
	fname = '/var/www/u1417944/data/www/nashagai.xyz/registrations ' + dt_string + '.json'
	with open(fname, 'w') as f:
		json.dump(reg_data, f)
	return reg_data

def main():
	user_ids = get_ids()
	upd_payload = [[] for i in range(len(user_ids))]
	reg_data = open_file()
	# Добавляем данные в update_payload
	for i, user_id in reversed(list(enumerate(user_ids))):
		for data in reversed(reg_data):
			if data != {}:
				if data["user_id"] == user_id:
					upd_payload[i] = [data["user_id"], data["access_token"], data["refresh_token"]]
					for i in range(len(reg_data)):  #Удаляем повторения
						if 'user_id' in reg_data[i]:
							if reg_data[i]["user_id"] == user_id:
								reg_data[i] = {}
	with open(registrations_file, 'w') as f:
		json.dump(reg_data, f)
	
	ws.update('Q2', upd_payload)



if __name__ == '__main__':
	main()