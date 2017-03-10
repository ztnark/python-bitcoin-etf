import urllib2
import threading
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import smtplib

def main():
    if len(sys.argv)!=4:
        print "please include the arguments: fromEmail,fromEmailPW,toEmail."
        sys.exit()

    url="https://www.sec.gov/rules/sro/batsbzx.htm"
    fromEmail=sys.argv[1]
    fromEmailPW=sys.argv[2]
    toEmail=sys.argv[3]
    checkETF(url,fromEmail,fromEmailPW,toEmail)

def sendEmail(emailtext,fromEmail,fromEmailPW,toEmail):
    msg = MIMEMultipart('alternative')
    msg['To'] = toEmail
    msg['Subject'] = "Bitcoin etf resuls!"
    msg['From'] = formataddr((str(Header('Python BTC SEC ETF Bot :)', 'utf-8')), fromEmail))
    part1 = MIMEText(emailtext, 'plain')
    msg.attach(part1)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(fromEmail, fromEmailPW)
    server.sendmail(fromEmail, toEmail, msg.as_string())
    server.close()
    print "successfully sent the mail"

def checkETF(url,fromEmail,fromEmailPW,toEmail):

    threading.Timer(15, checkETF,[url,fromEmail,fromEmailPW,toEmail]).start()
    data = urllib2.urlopen(url).read(20000) #number of chars that should catch the announcement
    eachWord = data.split()

    if "Bitcoin" in eachWord:
        text= "Bitcoin has been detected on"+url
        print text
        sendEmail(text,fromEmail,fromEmailPW,toEmail)
        os._exit(0)
    else:
        print "not found yet"

main()

