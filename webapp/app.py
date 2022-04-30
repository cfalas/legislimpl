from flask import Flask, render_template
import json
import requests
import time
import math
import datetime

app = Flask(__name__)

summaries = json.load(open('./data/all_summaries.json'))
print(len(summaries))
base_url = 'https://api.govinfo.gov'
query = '?api_key=oheReJtqERpvb0Wp49qV4Exow10jobDSCF8QtzhR'
config = {
    'query': query
}

likes = {}


@app.route("/bill/<bill_id>")
def view_bill(bill_id):
    bill = get_bill(bill_id)
    full_text = requests.get(bill['download']['txtLink'] + query).text
    bill['full'] = full_text
    bill['summary'] = 'This summary is not available yet. Check again soon!'
    bill['likes'] = 0
    if bill['packageId'] in summaries:
        bill['summary'] = summaries[bill['packageId']]
    if bill_id in likes:
        bill['likes'] = likes[bill_id]
    return render_template('bill.html', bill=bill, config=config)


@app.route("/weekly/<monday>")
def view_week(monday):
    return "<p>Hello, World!</p>"


all_bills = {}
all_bills = json.load(open('./data/all_bills.json'))


def get_bill(bill_id):
    f = requests.get(f'{base_url}/packages/{bill_id}/summary{query}').json()
    return f


def get_bills(count=1000):
    for x in range(0, count, 100):
        f = requests.get(f'{base_url}/collections/BILLS/2022-01-01T00:00:00Z'
                         f'{query}&offset={x}&pageSize=100').json()
        f = f['packages']
        for bill in f:
            if bill['packageId'] not in all_bills:
                all_bills[bill['packageId']] = bill
    f = open('./data/all_bills.json', 'w')
    json.dump(all_bills, f)
    f.close()
    return f


def hot(bill):
    s = bill['likes']
    order = math.log10(max(s, 1))
    days = datetime.date.today() - datetime.datetime.strptime(bill['date'],
                                                              '%Y-%m-%d').date()
    days = days.days
    print(s, order, days)
    return days - order


@app.route('/')
def index():
    bills = [
        {
            'id': all_bills[bill]['packageId'],
            'title': all_bills[bill]['title'],
            'summary': (summaries[all_bills[bill]['packageId']]
                        if all_bills[bill]['packageId'] in summaries else ''),
            'date': all_bills[bill]['dateIssued'],
            'likes': likes[bill] if bill in likes else 0,
        }
        for bill in all_bills if all_bills[bill]['packageId'] in summaries]
    bills = sorted(bills, key=lambda d: hot(d))
    bills = bills[:200]
    return render_template('listing.html', listings=bills)


@app.route('/like/<bill>', methods=['POST'])
def like(bill):
    if bill in likes:
        likes[bill] += 1
    else:
        likes[bill] = 1


def periodic():
    time.sleep(100)
    while True:
        print('periodic')
        get_bills(count=100)
        time.sleep(120)


if __name__ == '__main__':
    '''
    reload_thread = threading.Thread(target=periodic)
    reload_thread.start()
    '''
    app.run(debug=True, host='0.0.0.0')
