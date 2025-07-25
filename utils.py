import datetime
from month import Month


def create_new_month():
    print("Creating new month...")

    month_name = get_month_input() 
    rent = get_dollar_input("rent")
    heating = get_dollar_input("heating")
    electric = get_dollar_input("electric")
    water = get_dollar_input("water")
    internet = get_dollar_input("internet")

    new_month = Month(month_name, rent, heating, electric, water, internet, [])
    return new_month
 
def get_month_input():
    while True:
        try:
            month_str = input("Enter month/year (YYYY-MM): ")
            # validate the format
            date_obj = datetime.datetime.strptime(month_str, "%Y-%m")
            return month_str
        except ValueError:
            print("Please enter valid format YYYY-MM")

def get_dollar_input(type):
    while True:
        try:
            amount = float(input(f"Enter Amount for {type}: "))
            if amount < 0:
                print("Amount cannot be negative")
                continue
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid dollar amount")


def view_month(month_date, months_dict):
    print(f"displaying summary for {month_date}")

    if month_date not in months_dict:
        print(f"No month found for {month_date} ")
        return
    
    months_dict[month_date].displaySummary()

    
def list_months(months_dict):
    print("Listing all months...")

    if not months_dict:
        print("No months have been added yet")
        return
        
    for date, month_obj in months_dict.items():
        total = month_obj.calculate_total_month_due()
        print(f"  {date}: ${total:.2f}")