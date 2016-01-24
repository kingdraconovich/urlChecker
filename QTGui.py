# -*- coding: utf-8 -*-
import threading
import time
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *
import pycurl
from io import BytesIO
import sys

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode


buffer = BytesIO()

# Create an PyQT4 application object.
a = QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
w = QWidget()

# Set window size.
w.setFixedSize(800, 600)

# Set window title
w.setWindowTitle("URL Checker for SmartyAds QA Team")

stop = False

@pyqtSlot()
def stop_processing():
        global stop
        stop = True

@pyqtSlot()
def on_click(stop_processing):
    logTextbox.clear()
    logTextbox.setTextColor(QColor('black'))
    # Sending the login request and storing the cookie for session
    c = pycurl.Curl()
    if urlTextbox.text() != '':
        c.setopt(c.URL, 'http://'+str(urlTextbox.text())+'/user/login/js/1')
    else:
        c.setopt(c.URL, 'http://smartyads.com/user/login/js/1')
    c.setopt(c.COOKIEFILE, '')

    post_data = {'emailAddressH': emailTextbox.text(), 'password': passTextbox.text(), 'header': '1',
                 'rememberMe': '1'}
    #print('http://'+str(urlTextbox.text())+'/user/login/js/1')
    #print(post_data)
    # Form data must be provided already urlencoded.
    postfields = urlencode(post_data)
    #print(postfields)
    # Sets request method to POST,
    # Content-Type header to application/x-www-form-urlencoded
    # and data to send in request body.
    c.setopt(c.POSTFIELDS, postfields)
    c.setopt(c.WRITEFUNCTION, buffer.write)


    c.perform()
    logTextbox.append("")
    logTextbox.append("===========LOGIN STATUS===========")

    if urlTextbox.text() != '':
       logTextbox.append("Logging to: http://"+str(urlTextbox.text())+"/user/login/js/1")
    else:
        logTextbox.append("Logging to: http://smartyads.com/user/login/js/1")

    logTextbox.append('Status: %d' % c.getinfo(c.RESPONSE_CODE))
    # Elapsed time for the transfer.
    logTextbox.append('Status: %f' % c.getinfo(c.TOTAL_TIME))
    if "incorrect" in str(buffer.getvalue()):
        logTextbox.append("Login or password incorrect, crawling as unlogged user")
    logTextbox.append("==================================")
    logTextbox.append("")
    QApplication.processEvents()

    # URL = "http://smartyads.com/publishers"
    urlList = []

    f = open('UrlMap.txt')
    for line in f.readlines():
        if str(urlTextbox.text()) != '':
           urlList.append(line.strip("\n'").replace("smartyads.com", str(urlTextbox.text())))
        else:
           urlList.append(line.strip("\n'"))
    f.close()
    urlListCount = len(urlList)
    c.setopt(c.WRITEDATA, buffer)
    logTextbox.append("==================================")
    logTextbox.append("Total URLS in Map file: %d" %urlListCount)
    logTextbox.append("==================================")
    logTextbox.append("")
    QApplication.processEvents()



    def outputStatus(URL):
        c.setopt(pycurl.URL, URL)
        c.perform()
        outStr = 'URL: ' + URL + " ........................" 'Status: %d' % c.getinfo(
            c.RESPONSE_CODE) + ',' ' Time: %f' % c.getinfo(c.TOTAL_TIME)
        if c.getinfo(c.RESPONSE_CODE) in range(300, 399):
            logTextbox.setTextColor(QColor('darkGray'))
        elif c.getinfo(c.RESPONSE_CODE) == 200:
            logTextbox.setTextColor(QColor('darkGreen'))
        elif c.getinfo(c.RESPONSE_CODE) in range(400, 599):
            logTextbox.setTextColor(QColor('darkRed'))
        logTextbox.append(outStr)
        QApplication.processEvents()

    global stop
    for URL in urlList:

        if stop == True:
            stop = False
            break
        outputStatus(URL)

    c.close()



# Add a button
urlCheckButton = QPushButton('Check!', w)
urlCheckButton.setToolTip('Click to check all the URLs from site map')
urlCheckButton.clicked.connect(on_click)
urlCheckButton.resize(urlCheckButton.sizeHint())
urlCheckButton.move(585, 50)

# Add a button
stopButton = QPushButton('Stop', w)
stopButton.setToolTip('Click to stop current processing')
stopButton.clicked.connect(stop_processing)
stopButton.resize(stopButton.sizeHint())
stopButton.move(500, 50)

# Create textbox
urlTextbox = QLineEdit(w)
urlTextbox.resize(280, 30)
urlTextbox.move(160, 50)

passTextLabel = QLabel("Test server URL:", w)
passTextLabel.move(47, 55)

# Create textbox
emailTextbox = QLineEdit(w)
emailTextbox.move(160, 7)
emailTextbox.resize(180, 30)

emailTextLabel = QLabel("Email:", w)
emailTextLabel.move(115,12)

# Create textbox
passTextbox = QLineEdit(w)
passTextbox.move(490, 7)
passTextbox.resize(180, 30)

passTextLabel = QLabel("Password:", w)
passTextLabel.move(415, 12)

# Create textbox
logTextbox = QTextEdit(w)
logTextbox.move(20, 90)
logTextbox.resize(760, 500)
logTextbox.setReadOnly(True)

#editUrlMapButton = QPushButton('Edit URL map', w)
#editUrlMapButton.clicked.connect(exit)
#editUrlMapButton.resize(editUrlMapButton.sizeHint())
#editUrlMapButton.move(450, 40)

# Show window
t1 = threading.Thread(target=w.show())
t1.daemon
t1.start()

sys.exit(a.exec_())
