import hashlib
import requests
import json
import gspread
from datetime import datetime
from datetime import timedelta

headers = {
    'Authorization': '05be2d5f4a313f3e62ea733b38717266',
    'Content-Type': 'application/json'
}
body = {
    "client_id": 'pacer_998a1ddf2ffd49bc8fc2139adb3fea93',
    "refresh_token": '',
    "grant_type": "refresh_token",
}

def open_spreadsheet():
    spreadsheet_key = '1Ud-UnGvsSFwrUZu8fKktKHDaK38y_ubLh07AS57AEKg'; # ключ таблицы, в которой работаем
    gc = gspread.service_account(filename = 'credentials.json')
    sh = gc.open_by_key(spreadsheet_key)
    return sh.sheet1

def end_date():
    return str(datetime.now() + timedelta(days=1))

def main():
    ws = open_spreadsheet()
    upd_payload = ws.batch_get([f'R1:S{ws.row_count}'])[0][1:]
    for i in range(len(upd_payload)):
        if upd_payload[i] != []:
            body['refresh_token'] = upd_payload[i][1]
            r = requests.post("http://openapi.mypacer.com/oauth2/access_token", headers = headers, json = body).json()
            if r['success'] == True:
                data = r['data']
                upd_payload[i][0] = data['access_token']
                upd_payload[i].append(end_date())
            else:
                upd_payload[i][0] = ''
                upd_payload[i][1] = ''
                upd_payload[i].append('DELETED')
    ws.update('R2', upd_payload)

if __name__ == '__main__':
    main()