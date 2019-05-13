from Robinhood import Robinhood, endpoints
import os
import requests
import csv
import datetime
import time

filename = 'data/{}.csv'.format(str(datetime.datetime.now().date()))

### IMPORT ENVIRONMENT VARIABLES ###
if os.path.isfile('.env'):
    params = []
    with open('.env','r') as f:
        for line in f.readlines():
            params.append(line.rstrip().split('='))
    params = dict(params)
elif {'rh_username','rh_password','rh_2fatoken'}.issubset(os.environ):
    params = {'rh_username':os.getenv('rh_username'),
              'rh_password':os.getenv('rh_password'),
              'rh_2fatoken':os.getenv('rh_2fatoken')}
else:
    raise ValueError('Robinhood credentials not configured')
#####################################


rh = Robinhood()
login = rh.login(username=params['rh_username'],password=params['rh_password'],qr_code= params['rh_2fatoken'])
print('is login successful: {}'.format(login))

start_time = datetime.datetime.now()
count = 0
def process_popularity(link_url):
    global start_time
    global count
    if not link_url:
        resp = rh.instruments(link_url)
    else:
        resp = rh.get_url(link_url)

    results,n = [],45
    instruments = [(v['id'],v['symbol']) for v in resp['results'] if v['tradability']!='untradable']
    instrument_group = [instruments[i * n:(i + 1) * n] for i in range((len(instruments) + n - 1) // n )]
    for instruments in instrument_group:
        symbol_names = [v[1] for v in instruments]
        instrument_string = ','.join([v[0] for v in instruments])
        query_url=endpoints.api_url+'/instruments/popularity/?ids='+instrument_string
        popularity_resp = rh.session.get(query_url,timeout=500)
        if popularity_resp.status_code!=200:
            print(datetime.datetime.now()-start_time)
            start_time=datetime.datetime.now()
            print(popularity_resp.status_code)
        while popularity_resp.status_code==429:
            print('exceeded API request limit, sleeping...')
            time.sleep(10)
            popularity_resp = rh.session.get(query_url,timeout=30)
        popularity_resp=popularity_resp.json()
        popularity_resp = popularity_resp.get('results','')
        curr_time = int(datetime.datetime.now().timestamp()*1e6)
        popularity_values = [(curr_time,symbol,v['num_open_positions']) for
                             symbol,v in
                             zip(symbol_names,popularity_resp) if
                             v['num_open_positions']>=0]
        count+=len(popularity_values)
        results.extend(popularity_values)

    print(count)
    with open(filename,'a+') as f:
        csv_out = csv.writer(f)
        for row in results:
            csv_out.writerow(row)

    next_url = resp['next']
    return next_url

if not os.path.isfile(filename):
    with open(filename,'a+') as f:
        f.write('ts,symbol,popularity\n')

next_url = process_popularity('')
while next_url:
    next_url=process_popularity(next_url)


