# Personal Budget Tracker

A simple command-line utility for tracking my monthly housing expenses and utilities. Built to practice Python fundamentals including file I/O, JSON serialization, and argument parsing. 

## What it does

This tool helps track monthly expenses like rent, utilities, and additional costs. It automatically calculates utility splits between roommates and provides monthly summaries. Data is stored locally in JSON format.

## Usage

  ```tracker -n                                        #Create new month entry
  tracker --new-entry                                  #Create new month entry
  tracker --new-entry YYYY-MM                          #Create new month entry for specified month```
  
  ```tracker -e YYYY-MM -t rent                        #Edit a months rent  
  tracker --edit-month YYYY-MM --edit-utility rent     #Edit a months rent```
  
  ```tracker -l                                        #List all tracked dates
  tracker --list YYYY-MM                               #View summary```
  
  ```tracker -d 2025-01                                #Delete a month entry 
  tracker --delete-month                               #Delete a month entry```
  
  ```tracker -a                                        #Add additional cost 
  tracker --add-cost                                   #Add additional cost``` 

  ```tracker -dc 2025-01                               #Delete an additional cost for specified month
  tracker --delete-cost 2025-01                        #Delete an additional cost for specified month```            


#### Requirements

Python 3.6+
