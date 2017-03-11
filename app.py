import urllib2
import threading
import os
import sys
import ConfigParser
import requests
import urllib
import re
import json

def main():
    Config = ConfigParser.ConfigParser()
    Config.read('Config.ini')

    checkPrice(Config, 0)


def sendSMS(accountSid, authToken, text, fromSMS, toSMS):

    s = requests.Session()
    s.auth = (accountSid, authToken)
    body = { 'To' : toSMS, 'From' : fromSMS, 'Body':text}
    url = 'https://api.twilio.com/2010-04-01/Accounts/' + accountSid + '/Messages.json'

    r = s.post(url, body)
    if r.status_code != 201:
        print 'There was a problem sending your SMS'
        print r.content
    else :
        print 'Successfully sent the SMS'

def notify(config, price):
    text = 'Current Bitcoin price is $' + str(price)

    sendSMS(config.get('Twilio', 'AccountSid'), config.get('Twilio', 'AuthToken'),
        text, config.get('SMS','From'), config.get('SMS','To'))

def checkPrice(config, price):

    url = 'http://api.coindesk.com/v1/bpi/currentprice/usd.json'
    data = urllib2.urlopen(url).read(20000) #number of chars that should catch the announcement
    jsonData = json.loads(data)
    currentPrice = jsonData['bpi']['USD']['rate_float']
    if price == 0:
        price = currentPrice

    price = int(price)

    if currentPrice > price + 100:
        print 'Price is above ' + str(price)
        notify(config, currentPrice)
        price = price + 100
        print 'Raising target alert price to ' + str(price)

    elif currentPrice < price - 100:
        print 'Price is below ' + str(price - 100)
        notify(config, currentPrice)
        price = price - 100
        print 'Lowering target alert price to ' + str(price)

    else:
        print 'Current price is ' + str(currentPrice)
        print 'Thresholds set at ' + str(price + 100) + ' and ' + str(price - 100)


    threading.Timer(60, checkPrice,[config, price]).start()

main()
