#!/usr/bin/env python

import datetime
import csv
import re

import day
import person
import shifts

#########
# GLOBALS
#########
CSVDIALECT = 'excel'
DEFAULTNEWSHIFT = 'Off'

#//////////////////////////////////////////////////////////////////
# CLASS: Roster
# Creates a Roster object from an imported CSV file for manipulation by other programs
#
# Parameters:
#	csvfile: File location of the CSV to convert
#	-- Datatype: String
#//////////////////////////////////////////////////////////////////
class Roster:
	def __init__(self,csvfile):
		self.__roster = self.__returnArray(csvfile)
		self.__headers = self.__roster[0]
		self.__days = self.__buildRoster(self.__roster)

	def __getitem__(self,day):
		return self.showDay(day)

#//////////////////////////////////////////////////////////////////
# PUBLIC FUNCTIONS
# Callable by program to view/manipulate the class
# Prevents simple access to core methods and variables
#//////////////////////////////////////////////////////////////////
	#
	#//////////////////////////////////////////////////////////
	def showDay(self,xdate):
		day = self.__convertDate(xdate).strftime('%d/%m/%Y')
		return self.__days[day].working()

	def showPeriod(self, xstart, xfinish):
		arr = {}
		for n in range(1,len(self.__headers)):
			arr.update(self.__showMemberPeriod(self.__headers[n], xstart, xfinish))
		return arr

	def showMember(self, xstaff):
		return self.__showMember(xstaff)

	def showMemberPeriod(self, xstaff, xstart, xfinish):
		return self.__showMemberPeriod(xstaff, xstart, xfinish)

	def showShift(self,xdate,xstaff):
		day = self.__convertDate(xdate).strftime('%d/%m/%Y')
		return self.__days[day].returnShift(xstaff)

	def addMember(self,xstaff,**xdefault):
		if 'default' in xdefault:
			self.__addMember(xstaff,xdefault['default'])
		else:
			print("No default defined, setting as: '" + DEFAULTNEWSHIFT + "'" )
			self.__addMember(xstaff,DEFAULTNEWSHIFT)

	def removeMember(self,xstaff):
		self.__removeMember(xstaff)

	def updateShift(self,xstaff,xshift,xdate):
		self.__updateShift(xstaff,xdate,day)

	def updateShiftBatch(self,xstaff,xshift,xdate, ydate):
		dates = self.__getDateRange(xdate,ydate)
		for day in dates:
			updateShift(xstaff,xshift,day)

#//////////////////////////////////////////////////////////////////
# CORE FUNCTIONS
# Used to build the initial class
#//////////////////////////////////////////////////////////////////
	# FUNCTION: self.__returnArray
	# Returns a 2-Dimensional array from the nominated CSV file
	#
	# Parameter(s):
	#	csvfile: The filepath to the desired CSV
	#	-- Datatype: String
	# Returns:
	#	2-Dimensional Array
	#	- arr[x]: Each row of the CSV
	#	- arr[x][y]: Each column of the CSV per row
	#//////////////////////////////////////////////////////////
	def __returnArray(self,csvfile):
		try:
			with open(csvfile, 'r') as excel:
				contents = csv.reader(excel, dialect=CSVDIALECT)
				arr = list(contents)
			return arr
		except Exception as e:
			print("Unable to open CSV file:")
			print(str(e))

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__getIndex
	# Gets the column index of a string from the desired array
	#
	# Parameter(s):
	# 	string: String to locate within the array
	#	-- Datatype: String
	# 	arr: Array object to iterate through
	#	-- Dataype: Array
	# Returns:
	#	Integer with the index of the search string
	#//////////////////////////////////////////////////////////
	def __getIndex(self,string,arr):
		for i in range(0,len(arr)):
			if string == arr[i]:
				return i
		else:
			raise Exception(string + " not found!")

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__buildRoster
	# Converts the 2D array into a Dictionary Object
	#
	# Parameter(s):
	#	arr: 2D array returned from self.__returnArray()
	#	-- Datatype: Array
	# Returns:
	#	Dictionary of Day classes with embedded Person and Shift classes
	#	-- roster['DD/MM/YYYY']['StaffName']['Shift']
	#//////////////////////////////////////////////////////////
	def __buildRoster(self,arr):
		roster = {}
		for n in range(1,len(arr)):			#Skip the headers
			try:
				date = self.__convertDate(arr[n][0])
				shifts = self.__appendShiftsToStaff(arr[n],self.__headers)
				roster[date.strftime('%d/%m/%Y')] = day.Day(date,shifts)
			except Exception as e:
				#print("Failed to parse date '%s'" % arr[n][0])
				#print(str(e))
				continue
		return roster

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__appendShiftsToStaff
	# Called by self.__buildRoster to convert array rows into a dict
	#
	# Parameter(s):
	#	row: A row of shifts to be associated with headers
	#	-- Datatype: Array
	#	headers: Header cells to be associated with each corresponding column of the row
	#	-- Datatype: Array
	# Returns:
	#	A dictionary of row columns associated with corresponding headers
	#	{'HeaderA':'RowA', 'HeaderB':'RowB', 'HeaderC':'RowC'}
	#//////////////////////////////////////////////////////////
	def __appendShiftsToStaff(self,row,headers):
		shifts = {}
		for n in range(1,len(row)):			#Skip the date header
			shifts[headers[n]] = row[n]
		return shifts

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__convertDate
	# Regex matches a date string and converts to datetime object
	#
	# Parameter(s):
	#	xdate: Date string to match against
	#	-- Datatype: String
	# Returns:
	#	Python datetime.datetime Object
	#//////////////////////////////////////////////////////////
	def __convertDate(self,xdate):
		d = self.REMatcher(xdate)
		if d.match('([0-2][0-9]|3[0-1])[\/\-](0[1-9]|1[0-2])[\/\-](20[0-2][0-9])'):	#DD-MM-YYYY Format
			#print(datetime.date(d.group(3),d.group(2),d.group(1)))
			return datetime.date(int(d.group(3)),int(d.group(2)),int(d.group(1)))
		elif d.match('(20[0-2][0-9])[\/\-](0[1-9]|1[0-2])[\/\-]([0-2][0-9]|3[0-1])'):	#YYYY-MM-DD Format
			#print(datetime.date(d.group(1),d.group(2),d.group(3)))
			return datetime.date(int(d.group(1)),int(d.group(2)),int(d.group(3)))
		elif d.match('([3-5][0-9]{4})'):							#Excel number format
			#print(self.__getExcelDate(d.group(1)))
			return self.__getExcelDate(int(d.group(1)))
		else:
			pass

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__getExcelDate
	# Converts an Excel Date serial number into a datetime Object
	#
	# Parameter(s):
	#	xdate: Excel Date serial number
	#	-- Datatype: String, Float or Int
	# Returns:
	#	Python Datetime Object
	#//////////////////////////////////////////////////////////
	def __getExcelDate(self,xdate):
		xdate = int(float(xdate)) - 2	#Minus 2 days as Excel is inclusive
		base = datetime.date(1900,1,1)
		offset = datetime.timedelta(days=xdate)
		return base + offset

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__getDateRange
	# Returns an array of datetime objects between two dates
	#
	# Parameter(s):
	#	xdate,ydate: Start and Finish dates to compare
	#	-- Datatype: String
	# Returns:
	#	Array of datetime.datetime Objects between the two specified dates (inclusive)
	#//////////////////////////////////////////////////////////
	def __getDateRange(self,xdate,ydate):
		arr = []
		diff = self.__convertDate(xdate) - self.__convertDate(ydate)
		for n in range(0,(abs(diff.days) + 1)):		#+1 to be inclusive of final date
			arr.append(self.__convertDate(xdate) + datetime.timedelta(days=n))
		return arr

#//////////////////////////////////////////////////////////////////
# SECONDARY FUNCTIONS
# Called by the public functions to return and manipulate data
#//////////////////////////////////////////////////////////////////
	# FUNCTION: self.__asArr
	# Returns any non-array object within an array
	#
	# Parameter(s):
	#	obj: Any object
	#	-- Datatype: Any
	# Returns:
	#	array = [obj]
	#//////////////////////////////////////////////////////////
	def __asArr(self,obj):
		if isinstance(obj,list):
			return obj
		else:
			return list(obj)

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__showMember
	# Returns a dict of staff entries in each Day Object within the Roster
	#
	# Parameter(s):
	#	xstaff: Staff member for whom to search
	#	-- Datatype: String
	# Returns:
	#	Dictionary of {'xstaff':{'DD/MM/YYY':'Shift'},{'DD/MM/YYY':'Shift'}}
	#//////////////////////////////////////////////////////////
	def __showMember(self,xstaff):
		output = {}
		output[xstaff] = {}
		for day in self.__days:
			output[xstaff][day] = self.__days[day][xstaff]['shift']
		return output

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__showMemberPeriod
	# Returns a dict of staff entries in each Day Object within the requested date range
	#
	# Parameter(s):
	#	xstaff: Staff member for whom to search
	#	-- Datatype: String
	#	xstart,xfinish: Start and finish dates
	#	-- Datatype: String
	# Returns:
	#	Dictionary of {'xstaff':{'DD/MM/YYY':'Shift'},{'DD/MM/YYY':'Shift'}}
	#//////////////////////////////////////////////////////////
	def __showMemberPeriod(self,xstaff,xstart,xfinish):
		dates = self.__getDateRange(xstart,xfinish)
		output = {}
		output[xstaff] = {}
		for day in dates:
			try:
				output[xstaff][day.strftime('%d/%m/%Y')] = self.__days[day.strftime('%d/%m/%Y')][xstaff]['shift']
			except:
				continue
		return output

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__removeMember
	# Removes all instances of a nominated staff member from the Roster
	#
	# Parameter(s):
	#	xstaff: Keyname of staff membe to be removed
	#	-- Datatype: String
	#//////////////////////////////////////////////////////////
	def __removeMember(self,xstaff):
		for day in self.__days:
			self.__days[day].removeMember(xstaff)

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__addMember
	# Adds a new staff member key to each day with a default shift name
	#
	# Parameter(s):
	#	xstaff: Keyname of staff member to be added
	#	-- Dataype: String
	#	xdate: Optional. Default name of shift to be created for each day added
	#		Defaults to global var DEFAULTNEWSHIFT if not included
	#	-- Datatype: String
	#//////////////////////////////////////////////////////////
	def __addMember(self,xstaff,xdefault):
		for day in self.__days:
			self.__days[day].addMember(xstaff,xdefault)

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__updateShift
	# Creates a new Shift Object for a staff member on the specified date
	#
	# Parameter(s):
	#	xstaff: Keyname of the staff member to update
	#	-- Datatype: String
	#	xshift: Name of the Shift Object to be created
	#	-- Datatype: String
	#	xdate: Date of the day to update
	#	-- Datatype: String
	#//////////////////////////////////////////////////////////
	def __updateShift(self,xstaff,xshift,xdate):
		print("To Come...")

#//////////////////////////////////////////////////////////////////
# SUBCLASSES
# Internally used classes for various repetetive functions
#//////////////////////////////////////////////////////////////////
	# CLASS: REMatcher
	# Allows you to compare a string against regex and retain the matched groups
	# Similar to Perl's 'if(str ~= /regex/)' function
	#
	# Parameter(s):
	#	matchstring: The string which to compare regex against
	#	Datatype: String
	#//////////////////////////////////////////////////////////
	class REMatcher(object):
		def __init__(self,matchstring):
			self.matchstring = matchstring

		# Match the str against the desired regex
		def match(self,expr):
			self.rematch = re.match(expr, self.matchstring)
			return bool(self.rematch)

		# Returns group(i) of the strings that were 'match()'ed
		def group(self,i):
			return self.rematch.group(i)
