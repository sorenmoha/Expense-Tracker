# Personal Budget Tracker

A simple command-line utility for tracking my monthly housing expenses and utilities. Built to practice Python fundamentals including file I/O, JSON serialization, and argument parsing. 

## What it does

This tool helps track monthly expenses like rent, utilities, and additional costs. It automatically calculates utility splits between roommates and provides monthly summaries. Data is stored locally in JSON format.

## Usage

### Create a new month entry
```bash
python tracker.py -n                    # Prompts for month and all values
python tracker.py --new-entry 2025-01   # Creates entry for January 2025
```
```
python tracker.py -l                    # Lists all tracked months
python tracker.py --list 2025-01        # Shows detailed summary for January 2025
```
```
python tracker.py -e 2025-01 -t rent    # Edit January 2025 rent amount
python tracker.py --edit-month 2025-01 --edit-utility electric
```
```
python tracker.py -d 2025-01            # Delete January 2025 entry
```


#### Requirements

Python 3.6+
