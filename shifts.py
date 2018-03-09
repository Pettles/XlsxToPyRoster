#!/usr/bin/env python

from datetime import datetime, date, time, timedelta
import os.path

#//////////////////////////////////////////////////////////////////
# CLASS: Shift
# A class for populating a 'Shift' object as part of a roster
#
# Parameter(s):
#	shiftdate: The day on which a shift begins.
#	Datatype: Integer
#		- This should be in the Excel date serial format - e.g. 430101
#	period: The 'shift' that the staff member is meant to work
#	Datatype: String
#		- Accepts any set of strings to convert into start/finish times
#		- Strings and shift times can be set in _getShiftTimes
#		- Outputs start/finish times as datetime objects
#//////////////////////////////////////////////////////////////////
class Shift:
	def __init__(self,shiftdate,period):
		self.__date = shiftdate #Start date of the shift
		self.__period = period #The shift "name"
		self.__start,self.__finish = self.__getShiftTimes(self.__date,self.__period) #Start time
		self.__hoursWorked = self.__getHours(self.__start,self.__finish) #Total hours worked
		self.__breaks = self.__calcBreaks(self.__hoursWorked) #Unpaid break time
		self.__hoursPayable = self.__getTotalHours(self.__hoursWorked,self.__breaks) #Total billable hours

	def __str__(self):
		string = "Date: %s \n" % self.__date
		string += "Start Time: %s \n" % self.__start
		string += "Finish Time: %s \n" % self.__finish
		string += "Total Hours Worked: %s \n" % self.__hoursWorked 
		string += "Total Break Time: %s \n" % self.__breaks
		string += "Total Payable Hours %s" % self.__hoursPayable
		return string

#//////////////////////////////////////////////////////////////////
# PUBLIC FUNCTIONS
# Functions to return the private variables externally
#//////////////////////////////////////////////////////////////////
	def date(self):
		return self.__date

	def shift(self):
		return self.__period

	def start(self):
		return self.__start

	def finish(self):
		return self.__finish

	def worked(self):
		return self.__hoursWorked

	def breaks(self):
		return self.__breaks

	def hours(self):
		return self.__hoursPayable

#//////////////////////////////////////////////////////////////////
# PRIVATE FUNCTIONS
# Used by Public functions to access and manipulate private variables
#//////////////////////////////////////////////////////////////////
	# FUNCTION: self.__getDate
	# Convert the Excel date serial number to Python datetime
	#
	# Parameter(s):
	#	xdate = Excel date serial number
	#		e.g. 430101 = 1/1/2018
	#	Note: Two days are deducted from this number
	#		This is because Python is exclusive of the start/finish dates in calculation
	#		Whereas Excel is inclusive of these dates
	#//////////////////////////////////////////////////////////
	def __getDate(self,xdate):
		xdate = xdate - 2
		base = date(1900,1,1)
		offset = timedelta(days=xdate)
		return base + offset

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__getShiftTimes
	# Converts a shift description to a start end time
	#
	# Parameter(s):
	#	xdate = datetime date object
	#	xshift = String type
	#		This is compared against the dictionary
	#		to return the start and finish times
	# Returns:
	#	Two datetime objects
	#//////////////////////////////////////////////////////////
	def __getShiftTimes(self,xdate,xshift):
		opts = {"D":[time(8,30),time(17)],
			"Day8":[time(8,30),time(17)],
			"Day":[time(7),time(19)],
			"Night":[time(19),time(7)],
			"Morning":[time(6),time(15,30)],
			"Evening":[time(14),time(23,20)],
			"Grave":[time(22),time(7,30)],
			"Off":[time(0),time(0)],
			"SS Off":[time(0),time(0)],
			"Ann Lve":[time(0),time(0)],
			"sick":[time(0),time(0)]}
		shift = opts.get(xshift,[time(0),time(0)]) #Defaults to 'Off Work'

		if shift[0] > shift[1]:
			#Sets finish time to following day
			shift[0] = datetime.combine(xdate,shift[0])
			shift[1] = datetime.combine((xdate + timedelta(days=1)),shift[1])
		else:
			shift[0] = datetime.combine(xdate,shift[0])
			shift[1] = datetime.combine(xdate,shift[1])

		return shift[0],shift[1]

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__getHours
	# Determines the total hours worked based on start and finish times
	#
	# Parameter(s):
	#	start = Starting time datetime object
	#	finish = Finishing time datetime object
	# Returns:
	#	timedelta object containing the time difference
	#//////////////////////////////////////////////////////////
	def __getHours(self,start,finish):
		worked = finish - start #returns timedelta object (only returns days/seconds/milliseconds)
		return worked

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__calcBreaks
	# Calculates the total break time based on total hours worked
	# Length of break and interval time between breaks can be altered as required
	#
	# Parameter(s):
	#	wtime = timedelta object of total time worked
	# Returns:
	#	timedelta object of total allocated break time
	#//////////////////////////////////////////////////////////
	def __calcBreaks(self,wtime):
		lunchTime = 30 * 60 #30-minute break
		breakInterval = (6 * 60) * 60 #Every 6 hours

		breaks = wtime.seconds // breakInterval #Number of breaks
		return timedelta(seconds=(breaks * lunchTime)) #Total unpaid time @ lunch

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__getTotalHours
	# Calculates the total amount of billable hours
	#
	# Parameter(s):
	#	wtime = datetime object of total hours worked
	#	breaks = datetime object of total breaks allocated
	# Returns:
	#	timedelta object of total billable hours
	#//////////////////////////////////////////////////////////
	def __getTotalHours(self,wtime,breaks):
		return wtime - breaks
