# XlsxToPyRoster
A group of classes that convert an Excel Spreadsheet into a Python Object for manipulation and output.
- Requires the following non-standard packages: xlrd, requests

Instructions to get the 'processRoster.py' to execute:
- Open 'processRoster.py'
- Set the following Global Variables:
- FILEURL = The web URL of the file to download
- WORKSHEET = The worksheet on the *.xlsx file on which the roster is located
- ROSTERNAME = Defines the base naming convention of the output files. e.g. roster = rosterYYYYMMDD.xlsx
- MAILSERVER = The mail server to send outbound emails from
- FROMEMAIL = The address to send outbound emails from
- MAILRECIPS = Dictionary of Member headers of roster to check against
- # Key: Column header of staff member (e.g. 'Pettles')
- # Value: Email address to send result to for that member (e.g. pettles@github.com)
- # e.g. {'Pettles':'pettles@github.com','Kevin':'kevin@example.com'}

If running automatically (via cron/event/init/task scheduler):
- Unhash and set AUTHUSER, AUTHPASS globals (Hard-coding to be removed in a future update)
- Under _download, unhash the 'user','pwd' lines that are using the globals and hash out the lines that request manual input

To set your shift names and time ranges:
- Open 'shifts.py'
- Under '__getShiftTimes', edit the 'opts' dict to contain {'shiftName':[time(startHour,startMin),time(endHour,endMin)]}

Examples already exist for all of the above.
This is still a work-in-progress. Further changes to be made can be found in the ToDo.txt.