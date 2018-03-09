#!/usr/bin/env python

import processRoster
import sys

myroster = processRoster.Roster()

myroster.process()

#Force quit
#To ensure kill during automation
sys.exit()