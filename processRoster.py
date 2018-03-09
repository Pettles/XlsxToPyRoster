#!/usr/bin/env python

#Logging
import logging

#Used for naming
import datetime

#Used for download
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import shutil
from getpass import getpass

#Used for conversion
import xlrd
import csv

#Used for email
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

#Used for verification
import hashlib
import os.path
import os

#Used for comparison and table building
import roster


#/////////////////////////////////////////////
# GLOBALS
#/////////////////////////////////////////////
#AUTHUSER = ''       #HTTP Auth username to download file.
#AUTHPASS = ''       #HTTP Auth password to download file.
FILEURL = 'https://www.example.com/example_roster.xlsx'
WORKSHEET = "example_roster" #The Excel Worksheet that contains the roster.
ROSTERNAME = "roster" #Defines the base naming convention of the output files. e.g. roster = rosterYYYYMMDD.xlsx
MAILSERVER = "mail.example.com"
FROMEMAIL = "example@example.com"
MAILRECIPS = {'':''}
# MAILRECIPS - Dictionary of Member headers of roster to check against
# Key: Column header of staff member (e.g. 'Pettles')
# Value: Email address to send result to for that member (e.g. pettles@github.com)
# e.g. {'Pettles':'pettles@github.com','Kevin':'kevin@example.com'}
#/////////////////////////////////////////////

class Roster:
	def __init__(self):
		self._log = self._setupLogging('./log/logs.log')
		self._name = ROSTERNAME + datetime.datetime.now().strftime("%Y%m%d")
		self._httppath = FILEURL
		self._xlsxpath = "./downloaded/"
		self._csvpath = "./converted/"
		self._excelxtn = ".xlsx"
		self._csvxtn = ".csv"
		self._xlsxfull = self._xlsxpath + self._name + self._excelxtn
		self._csvfull = self._csvpath + self._name + self._csvxtn
		self._recips = MAILRECIPS

	def _setupLogging(self,logFile):
		logger = logging.getLogger('myapp')
		hdlr = logging.FileHandler(logFile)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		logger.addHandler(hdlr)
		logger.setLevel(logging.INFO)
		return logger

	def process(self):

		try:
			self._log.info("Processing roster for " + datetime.datetime.now().strftime("%d/%m/%Y") + "...")
			self._log.info("===========================================================")
			self._log.info("Current path is: " + self._httppath)
			self._log.info("Downloading...")
			if self._download():
				self._log.info("Comparing " + self._name + " roster against existing versions...")
				if self._locateLastFile(self._xlsxpath, ROSTERNAME, self._excelxtn) and self._compareFiles(self._xlsxfull,self._locateLastFile(self._xlsxpath, ROSTERNAME, self._excelxtn)):
					self._log.info("No changes to roster since last download. Removing downloaded file: " + self._name + self._excelxtn)
					os.remove(self._xlsxfull)
					self._log.info("File deleted. No further actions required.")
				else:
					self._log.info("Downloaded file is newer than the last available version.")
					self._log.info("Converting to *.csv")
					self._convert()

					self._log.info("Emailing latest versions..")
					currentRoster = roster.Roster(self._csvfull)
					self._log.info("First done")
					prevRoster = roster.Roster(self._locateLastFile(self._csvpath, ROSTERNAME, self._csvxtn))
					self._log.info("Second done")
					today = datetime.datetime.now().strftime("%d/%m/%Y")
					fortnite = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%d/%m/%Y")
					self._log.info("Resources allocated, looping...")
					for key in self._recips:
						if currentRoster.showMemberPeriod(key,today,fortnite) == prevRoster.showMemberPeriod(key,today,fortnite):
							self._log.info("{0} is the same in both rosters between {1} and {2}. Skipping...".format(key, today, fortnite))
						else:
							self._log.info("{0} is different between {1} and {2}. Emailing to {3}...".format(key, today, fortnite,self._recips[key]))
							self._email(key,self._recips[key],currentRoster.showMemberPeriod(key,today,fortnite),prevRoster.showMemberPeriod(key,today,fortnite))
			else:
				self._log.info("File '" + self._name + "' already exists!")
				self._log.info("Aborting file conversion...")
				self._log.info("Aborting emailing files...")
				self._log.info("Please complete these manually or remove the following file and re-run the process:")
				self._log.info(self._xlsxfull)
			self._log.info("===========================================================")
			self._log.info("Processing complete!")

		except Exception as e:
			self._log.error("##################")
			self._log.error("PROCESSING FAILED!")
			self._log.error("##################")
			self._log.error(str(e))

	###################################
	# Downloads a copy of the xlsx roster
	# Saves as './downloaded/rosterYYYYMMDD.xlsx'
	###################################
	def _download(self):

		try:
			if os.path.isfile(self._xlsxfull):
				return False
			user = raw_input("Please enter username: ")
			#user = AUTHUSER
			pwd = getpass("Please enter password for '" + user + "': ")
			#pwd = AUTHPASS
			r = requests.get(self._httppath, auth=(user,pwd), verify=False, stream=True)
			if r.status_code != requests.codes.ok:
				raise Exception("Unable to download file. Check credentials and connectivity")
			self._log.info("Credentials good, downloading...")
			r.raw.decode_content = True

			with open(self._xlsxfull,'wb') as out_file:
				shutil.copyfileobj(r.raw,out_file)
				self._log.info(self._name + self._excelxtn + " downloaded successfully!")
				return True
		except Exception as e:
			self._log.error("Something broke while trying to download: " + str(e))

	###################################
	# Converts the xlsx file to a csv format
	# Saves as './converted/rosterYYYYMMDD.csv'
	###################################
	def _convert(self):
		try:
			wb = xlrd.open_workbook(self._xlsxfull)
			sh = wb.sheet_by_name(WORKSHEET)

			with open(self._csvfull,'w') as new_csv:
				wr = csv.writer(new_csv, quoting=csv.QUOTE_ALL)
				for row in range(sh.nrows):
					wr.writerow(sh.row_values(row))
				self._log.info("CSV written to: " + self._csvfull)

		except Exception as e:
			self._log.error("Something broke, are all the file and path names correct?")
			self._log.error(str(e))

	###################################
	# Will email a copy of both the xlsx and csv files to a nominated address
	###################################
	def _email(self,name,address,current,previous):
		send_from = FROMEMAIL
		data = self._buildHTMLTable(name,current,previous)
		body = "Hey, {0}!".format(name)
		body += """<br><br>The roster has been updated recently and my little scripty thing has found that your upcoming shifts have changed!
<br><br>Below is a table of your upcoming shifts and the aforementioned changes:<br><br>"""
		body += data
		body += """
<br>If you want to double-check these shifts, please see the current version of the roster here:"""
body += "<br><a href='" + FILEURL + "'>" + FILEURL + "</a>"
body += """

<br><br>To stop receiving these emails, simply reply 'STOP!', and nothing will happen.
Then come over and ask me to remove you from this mailing list and I'll think about it ;)
Also, if you want this sent to a different email address, let me know.

<br><br>With love ('n' stuff),
<br>Me.""".format(name)
		
		files = [self._xlsxfull,self._csvfull]

		try:
			self._log.info("Sending email to '" + address + "'...")
			msg = MIMEMultipart()
			msg['From'] = send_from
			msg['To'] = address
			msg['Subject'] = "Latest Roster " + datetime.datetime.now().strftime("%Y%m%d")

			msg.attach(MIMEText(body, 'html'))

			#Removed this as we no longer need to attach the files.
			#for f in files or []:
			#	with open(f, "rb") as fil:
			#		part = MIMEApplication(fil.read())
			#
			#	part['Content-Disposition'] = 'attachment; filename="%s"' % f
			#	msg.attach(part)

			smtp = smtplib.SMTP(MAILSERVER)
			smtp.sendmail(send_from, address, msg.as_string())
			smtp.close()
			self._log.info("Email sent successfully!")
		except Exception as e:
			self._log.error("Failed to send email: " + str(e))

	###################################
	# Returns the MD5 checksum of the file
	# Used to check the file against previous versions
	###################################
	def _getChecksum(self,path):
		try:
			with open(path, "rb") as checkfile:
				data = checkfile.read()
				return hashlib.md5(data).hexdigest()

		except Exception as e:
			self._log.error("Unable to open " + path + " " + str(e))
	
	###################################
	# Attempts to locate the last file following the requested naming convention
	###################################
	def _locateLastFile(self, folder, name, xtn):
		count = 1
		date = datetime.datetime.now()
		while True:
			try:
				otherfile = folder + name + (date - datetime.timedelta(days=count)).strftime("%Y%m%d") + xtn
				if os.path.isfile(otherfile):
					self._log.info("Found: " + otherfile)
					return otherfile
				elif count == 28:
					self._log.info("Unable to locate a file within the last 28-days.")
					return False
				else:
					#print(otherfile + " does not exist. Trying previous day...")
					count = count + 1
			except Exception as e:
				self._log.error("An error occurred when attempting to locate the last file: " + str(e))

	###################################
	# Compares the MD5 Checksum of two files
	###################################
	def _compareFiles(self,file1,file2):
		try:
			#print(self._getChecksum(file1))
			#print(self._getChecksum(file2))
			if self._getChecksum(file1) == self._getChecksum(file2):
				return True
			else:
				return False
		except:
			return False

	def _buildHTMLTable(self,key,current,previous):
		table = """
<style>
table, tr, th, td {
 border: 1px solid black;
 border-collapse: collapse;
 text-align: center;
}
</style>
<table>
		<tr><th style='width: 150px;'>Date</th><th style='width: 150px;'>Previous Shift</th><th style='width: 150px;'>New Shift</th></tr>"""
		for day in sorted(current[key].keys(), key=lambda k: (k[:2:-1],k[:2])):	#Sorts by YYYY/MM then DD
			table += "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(day,previous[key][day],current[key][day])
		table += "</table>"
		return table
