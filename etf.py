import urllib2
import threading
import os
import sys
import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import requests
import smtplib
import urllib
import re

def main():
    if len(sys.argv)!=2:
        print 'please include the arguments: fromEmailPassword.'
        sys.exit()
    
    fromEmailPW=sys.argv[1]

    #init and import the configuration file
    Config = ConfigParser.ConfigParser()
    Config.read('Config.ini')

    checkETF('https://www.sec.gov/rules/sro/batsbzx.htm', Config, fromEmailPW)
    checkFTP('https://www.sec.gov/rules/sro/batsbzx/2017/?C=M;O=A', Config, fromEmailPW)

def sendEmail(emailtext,fromEmail,fromEmailPW,toEmail):
    msg = MIMEMultipart('alternative')
    msg['To'] = toEmail
    msg['Subject'] = 'Bitcoin etf resuls!'
    msg['From'] = formataddr((str(Header('Python BTC SEC ETF Bot :)', 'utf-8')), fromEmail))
    part1 = MIMEText(emailtext, 'plain')
    msg.attach(part1)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(fromEmail, fromEmailPW)
    server.sendmail(fromEmail, toEmail, msg.as_string())
    server.close()
    print 'successfully sent the email'

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

def notify(config, url, fromEmailPW):
    text= 'Bitcoin has been detected on ' + url
    print text

    if config.get('Preferences', 'Email') == 'true':
        sendEmail(text, config.get('Emails','From'), fromEmailPW, config.get('Emails','To'))
    if config.get('Preferences', 'SMS') == 'true':
        sendSMS(config.get('Twilio', 'AccountSid'), config.get('Twilio', 'AuthToken'),
            text, config.get('SMS','From'), config.get('SMS','To'))

def checkETF(url, config, fromEmailPW):

    threading.Timer(15, checkETF,[url, config, fromEmailPW]).start()
    data = urllib2.urlopen(url).read(20000) #number of chars that should catch the announcement
    
    #Use lower case by default
    eachWord = data.lower().split()

    if 'bitcoin' in eachWord:
        notify(config, url, fromEmailPW)
                
        os._exit(0)
    else:
        print 'No mention of bitcoin has been found yet on ' + url

def checkFTP(url, config, fromEmailPW):

    threading.Timer(15, checkFTP,[url, config, fromEmailPW]).start()
    data = urllib2.urlopen(url).read(20000) #number of chars that should catch the announcement
    
    #Use lower case by default
    words = data.lower().split()

    #Check for any new documetns during the ten days after March 10th 2017
    matches = [string for string in words if re.match('1.-mar-2017', string)]
    if matches:
        notify(config, url, fromEmailPW)
                
        os._exit(0)
    else:
        print 'No mention of bitcoin has been found yet on ' + url

main()

