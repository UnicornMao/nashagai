from argparse import ArgumentParser
from datetime import date
from datetime import timedelta
import gspread
import time
import requests

START_DATE = date(2021,7,12)

def open_spreadsheet():
	spreadsheet_key = '1Ud-UnGvsSFwrUZu8fKktKHDaK38y_ubLh07AS57AEKg'; # ключ таблицы, в которой работаем
	gc = gspread.service_account(filename = 'credentials.json')
	sh = gc.open_by_key(spreadsheet_key)
	return sh.sheet1, sh.worksheet('Sheet7')

def parse_date():
	# Взятие данных из консоли 
	parser = ArgumentParser()
	parser.add_argument("-d", "--day", help="Загрузить кол-во шагов в этот день. Формат: YYYY-MM-DD.", 
		default = (date.today() - timedelta(days=1)).isoformat())
	day = parser.parse_args().day
	try:
		parsed_date = date.fromisoformat(day)
		return parsed_date
	except Exception as e:
		print(day)
		print('Неправильный формат! Используйте YYYY-MM-DD.')
		print(e)
		exit()

def cell_range_a1_notation(row, column):
    col_A1 = ""
    while column > 0:
        column, remainder = divmod(column - 1, 26)
        col_A1 = chr(65 + remainder) + col_A1
    return col_A1 + str(row)  

def main():
	ws_in, ws_out = open_spreadsheet()
	parsed_date = parse_date()
	r = ws_in.batch_get([f'Q1:R{ws_in.row_count}',f'U1:U{ws_in.row_count}'])
	users = [[r[0][i], r[1][i]] for i in range(1,len(r[0]))]

	upd_payload = [[''] for _ in range(319)]
	for i in range(len(users)):
		user = users[i]
		steps = ''
		if (len(user[0]) > 1) and (user[1][0] != '#N/A'):
			headers = {
    			'Authorization' : "Bearer " + user[0][1]
			}
			r = requests.get(f'http://openapi.mypacer.com/users/{user[0][0]}/activities/daily.json?start_date={parsed_date}&end_date={parsed_date}&accept_manual_input=false', 
				headers = headers).json()
			if r['success'] == True:
				#print(r['data'])
				if r['data']['daily_activities'] != []:
					if len(r['data']['daily_activities']) > 1:
						print(r['data']) 
					steps = r['data']['daily_activities'][0]['steps']
				else:
					steps = 'EMPTY'
			else:
				steps = 'ERR'
			upd_payload[int(user[1][0])-2][0] = steps
	col = (parsed_date - START_DATE).days + 3
	if ws_out.col_count < col:
		ws_out.resize(cols = col)
		ws_out.update_cell(1,col, parsed_date.isoformat())
	rng = cell_range_a1_notation(2,col)

	ws_out.update(rng, upd_payload)


if __name__ == '__main__':
	main()