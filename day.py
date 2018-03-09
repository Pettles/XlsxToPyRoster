#!/usr/bin/env python

import person
import datetime

#//////////////////////////////////////////////////////////////////
# CLASS: Day
# Used to create a 'Day' Object within the Roster Class
# Each day is assigned a number of staff via the Person Class
#
# Parameter(s):
#	date: Python datetime.datetime object
#		- Set as self.__date
#		- Parsed to 'Person' object to set shift dates
#	shifts: A Python dictionary of Staff Names (key) and Shift Names (value)
#		- Staff names used to create 'Person' object names
#		- Shift names used to create 'Shift' object details
#//////////////////////////////////////////////////////////////////
class Day:
	def __init__(self,date,shifts):
		self.__date = date
		self.__working = self.__getStaff(self.__date,shifts)

	def __getitem__(self,name):
		try:
			return self.__working[name]
		except KeyError:
			print("Keyname %s does not exist" % name)

#//////////////////////////////////////////////////////////////////
# PUBLIC FUNCTIONS
# Returns values of private variables belonging to the class
#//////////////////////////////////////////////////////////////////
	def working(self):
		working = {}
		for staff in self.__working.keys():
			working[self.__working[staff].name()] = self.__working[staff].shift()
		return working

	def date(self):
		return self.__date

	def removeMember(self, xstaff):
		self.__removeMember(xstaff)

	def addMember(self,xstaff,xdefault):
		self.__addMember(xstaff,xdefault)

	def showMember(self,xstaff):
		return self.__showMember(xstaff)

#//////////////////////////////////////////////////////////////////
# CORE FUNCTIONS
# Required to build the core variables of the Class
#//////////////////////////////////////////////////////////////////
	# FUNCTION: self.__getStaff
	# Returns a dictionary of Staff Members and Shift Objects
	#
	# Parameter(s):
	#	date: Used to set the self.__date in the 'Shift' object class
	#	-- Datatype: Python datetime.datetime Object
	# Returns:
	#	Dictionary Object
	#		key: Staff Name
	#		value: Person Object
	#//////////////////////////////////////////////////////////
	def __getStaff(self,date,shifts):
		staff = {}
		for name,shift in shifts.items():
			staff[name] = person.Person(date,name,shift)
		return staff

#//////////////////////////////////////////////////////////////////
# PRIVATE FUNCTIONS
# Used by the Public functions to access and manipulate private variables
#//////////////////////////////////////////////////////////////////
	# FUNCTION: self.__removeMember
	# Removes a desired staff member from the self.__working dict
	#
	# Parameter(s):
	#	xstaff: Name of the staff member to remove
	#	-- Datatype: String
	#//////////////////////////////////////////////////////////
	def __removeMember(self,xstaff):
		try:
			del self.__working[xstaff]
			#print(xstaff + " deleted from " + self.__date.strftime('%d/%m/%Y'))
		except:
			print("Unable to locate " + xstaff + " on " + self.__date.strftime('%d/%m/%Y'))

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__addMember
	# Adds a new Staff:Shift entry into the self.__working variable
	#
	# Parameter(s):
	#	xstaff: Name of staff member to add
	#	-- Dataype: String
	#	xdefault: The name of the shift to create for the staff member
	#	-- Datatype: String
	#//////////////////////////////////////////////////////////
	def __addMember(self,xstaff,xdefault):
		self.__working[xstaff] = person.Person(self.__date,xstaff,xdefault)

	#//////////////////////////////////////////////////////////
	# FUNCTION: self.__showMember
	# Returns a the shift name of the desired staff member as a dict object
	#
	# Parameter(s):
	#	xstaff: Staff name who you wish to have returned
	#	-- Datatype: String
	# Returns:
	#	Dictionary object of {StaffName:ShiftName}
	#//////////////////////////////////////////////////////////
	def __showMember(self,xstaff):
		staff = {}
		staff[xstaff] = self.__working[xstaff].shift()
		return staff
