from datetime import date
from datetime import timedelta
import json
import gspread

START_DATE = date(2021,7,14)

def open_spreadsheet():
	spreadsheet_key = '1Ud-UnGvsSFwrUZu8fKktKHDaK38y_ubLh07AS57AEKg'; # ключ таблицы, в которой работаем
	gc = gspread.service_account(filename = 'credentials.json')
	sh = gc.open_by_key(spreadsheet_key)
	return sh.worksheet('Итого'), sh.worksheet('Нулевики')

def main():
	ws_in, ws_out = open_spreadsheet()
	r = ws_in.batch_get(['D2:CE318'])
	print(r[0][3])

	out = [['0',''] for _ in range(len(r[0]))]
	for user in range(len(r[0])):
		for i in range(len(r[0][user])):
			if (r[0][user][i] == '0') and (i % 2 == 0):
				out[user][0] = str(int(out[user][0]) + 1)
				if out[user][1] == '':
					out[user][1] = (START_DATE + timedelta(days = i // 2)).isoformat()
				else:
					out[user][1] += ', ' + (START_DATE + timedelta(days = i // 2)).isoformat()
	ws_out.update('E2',out)

if __name__ == '__main__':
	main()