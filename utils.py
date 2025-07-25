import datetime
from month import Month
import json


def create_new_month(month_name=None):
    print("Creating new month...")

    # If month_name not provided or is "prompt", ask for it
    if month_name is None or month_name == "prompt":
        month_name = get_month_input()
    else:
        # Validate the provided month format
        try:
            datetime.datetime.strptime(month_name, "%Y-%m")
            print(f"Using month: {month_name}")  # Confirm we're using the provided month
        except ValueError:
            print("Invalid month format. Please use YYYY-MM format.")
            return None



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

def edit_month(month_date, value_to_edit, months_dict):
    if month_date not in months_dict:
        print(f"No month found for {month_date}")
        return

    new_value = get_dollar_input(f"{value_to_edit}")  # Uses your validation
    month_object = months_dict[month_date]
    setattr(month_object, value_to_edit, new_value)
    print(f"Updated {value_to_edit} to ${new_value:.2f}")
    
def list_months(months_dict):
    print("Listing all months...")

    if not months_dict:
        print("No months have been added yet")
        return
        
    for date, month_obj in months_dict.items():
        total = month_obj.calculate_total_month_due()
        print(f"  {date}: ${total:.2f}")

        import json

# saves to a static file
def save_data(months_dict):
    """Save months_dict to tracker_data.json"""
    json_data = months_dict_to_json(months_dict)  # Convert objects to dict
    with open("tracker_data.json", "w") as f:
        json.dump(json_data, f, indent=2)
    print("Data saved successfully!")

def load_data():
    """Load data from tracker_data.json and return months_dict"""
    try:
        with open("tracker_data.json", "r") as f:
            json_data = json.load(f)
            return json_to_months_dict(json_data)  # Convert dict back to objects
    except FileNotFoundError:
        return {}  # Return empty dict if file doesn't exist
    

def months_dict_to_json(months_dict):
    """Convert months_dict with Month objects to JSON-serializable format"""
    json_data = {}
    for month_name, month_obj in months_dict.items():
        json_data[month_name] = {
            'month_name': month_obj.month_name,
            'rent': month_obj.rent,
            'heating': month_obj.heating,
            'electric': month_obj.electric,
            'water': month_obj.water,
            'internet': month_obj.internet,
            'additional_costs': month_obj.additional_costs
        }
    return json_data    


def json_to_months_dict(json_data):
    """Convert JSON data back to months_dict with Month objects"""
    months_dict = {}
    for month_name, month_data in json_data.items():
        month_obj = Month(
            month_data['month_name'],
            month_data['rent'],
            month_data['heating'], 
            month_data['electric'],
            month_data['water'],
            month_data['internet'],
            month_data['additional_costs']
        )
        months_dict[month_name] = month_obj
    return months_dict