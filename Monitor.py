""" 
Alerts of any changes on natgasweather.com and sends the natural gas demand widget along with updated description to a list of recepients by email.

A fun little project that was supposed to help me make fast decisions on whether to long/short Natgas on the market without having to manually monitor 
the website or subscribe to a paid service to do that for me.
"""

# v1.0: Initial release

import requests
from bs4 import BeautifulSoup
import string
import smtplib
import re
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime
import sys
import os

# SETTINGS
# -----------------------------

# Gets authentication and recepient info from a file
script_dir = os.path.dirname(__file__)
filename = os.path.join(script_dir, 'EmailSettings.txt')
with open(filename) as file:
    settings = file.read().splitlines()
file.close()

# Gets email address & password to send the scraped emails from
email = settings[0].replace('email:', '')
password = settings[1].replace('password:', '')
send_to_emails = settings[2].replace('send_to_emails:', '')
send_to_emails = send_to_emails.split(',')

# WEBSITE POLLING
# -----------------------------

# Indefinite loop to keep checking the website for changes
while True:
    url = "https://www.natgasweather.com/"
    # Impersonate a mainstream browser
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers) # Download the page
    soup = BeautifulSoup(response.text, "lxml") # Grab all text from the page

    # If the following string still exists on the page - assume the webpage hasn't been updated
    if str(soup).count("Dec 31-Jan 6") == 1: # ! Need to dynamically save somewhere and compare, instead of manually inputting
        print('Old: '+strftime("%Y-%m-%d %H:%M:%S", gmtime())) # Log the output
        time.sleep(120) # Wait some time before - don't get banned for sending too many requests
        continue # Continue monitoring from the beginning
        
    # Else if the string doesn't exist, the webpage must have gotten updated
    else:
        # Write the parsed website text to a log file for reference/debug
        f = open('web_log.txt', 'w')
        print(str(soup).replace('\xa2', ' '), file=f)
        f.close()

        # SMTP server config for the sender account
        server = smtplib.SMTP('smtp.gmail.com', 587) # Creates an SMTP session
        server.starttls() # Start TLS
        server.login(email, password) # Authentication

        # Scrape an image interested in and include it in the HTML above the main text 
        widget = re.findall('<div class="widget widget_text" id="text-8">.*', str(soup))
        messageHTML = '<html><body>'+str(widget[0])+'</div></body></html><a href="www.natgasweather.com">natgasweather.com</a>'
        messageHTML = messageHTML.replace('\xa0', ' ')
        print('New!: '+strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' - sending to: ' + ", ".join(send_to_emails))

        # Email content config
        subject = 'natgasweather news!'
        messagePlain = 'Change of content'
        msg = MIMEMultipart('alternative') # Multiple MIME support - text/plain
        msg['From'] = email
        msg['To'] = ", ".join(send_to_emails) # List of recepients separated by ","
        msg['Subject'] = subject

        # MIME - text & plain
        msg.attach(MIMEText(messagePlain, 'plain'))
        msg.attach(MIMEText(messageHTML, 'html'))

        # Send the email
        text = msg.as_string() # Return the entire message flattened as a string
        server.sendmail(email, send_to_emails, text) # Send the email
        server.quit() # Disconnect from the server
        
        break
input()

# References
# https://chrisalbon.com/python/web_scraping/monitor_a_website/
# https://docs.python.org/2/library/email.message.html
# https://stackoverflow.com/questions/33775903/how-to-send-a-email-body-part-through-mimemultipart