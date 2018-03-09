#!/usr/bin/env python

import shifts

#//////////////////////////////////////////////////////////////////
# CLASS: Person
# Used to create a 'Person' Object that is then assigned a shift
#
# Parameter(s):
#	date: Parsed to the Shift object to set the date of the shift
#	Datatype: Python datetime.datetime object
#
#	name: Set as self.__name
#	-- Datatype: String
#	shift: Parsed to the Shift object to determine shift times
#	-- Datatype: String
#//////////////////////////////////////////////////////////////////
class Person:
	def __init__(self,date,name,shift):
		self.__name = name
		self.__shift = shifts.Shift(date,shift)		

	def __getitem__(self,name):
		return self.__shift.shift()

#//////////////////////////////////////////////////////////////////
# PUBLIC FUNCTIONS
# Returns values of private variables belonging to the class
#//////////////////////////////////////////////////////////////////
	def name(self):
		return self.__name

	#//////////////////////////////////////////////////////////
	# Returns the 'self.__period' variable of the Shift class object
	#//////////////////////////////////////////////////////////
	def shift(self):
		return self.__shift.shift()
