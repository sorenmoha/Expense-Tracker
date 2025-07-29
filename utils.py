import datetime
from month import Month
import json


def create_new_month(month_name = None):

    print("Creating new month...")
       
    # If month_name not provided or is None, ask for it
    if month_name is None:
        month_name = get_month_input()
    else:
        # Validate the provided month format
        try:
            datetime.datetime.strptime(month_name, "%Y-%m")
            print(f"Using month: {month_name}")  # Confirm we're using the provided month
        except ValueError:
            print("Invalid month format. Please use YYYY-MM format.")
            return None
 
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

def get_dollar_input(type):  #type is what to take dollar input for (ex: the rent, an additional cost) 
    while True:
        try:
            amount = float(input(f"Enter Amount for {type}: "))
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid dollar amount")

def delete_month(month_date_to_delete, months_dict):
    print(f"deleting {month_date_to_delete}")
    if month_date_to_delete not in months_dict:
        print(f"No month found for {month_date_to_delete} ")
        return
    
    if input("Are you sure? (y/n): ").lower() == 'y':
        del months_dict[month_date_to_delete]
        print(f"deleted {month_date_to_delete}")
        save_data(months_dict)
    else:
        print("cancelled")

def edit_month(month_date, utility_to_edit, months_dict):
    if month_date not in months_dict:
        print(f"No month found for {month_date}")
        return

    new_value = get_dollar_input(f"{utility_to_edit}")  # Uses your validation
    month_object = months_dict[month_date]
    setattr(month_object, utility_to_edit, new_value)
    print(f"Updated {utility_to_edit} to ${new_value:.2f}")
    save_data(months_dict)

def list_months(months_dict):
    print("Listing all months...")

    if not months_dict:
        print("No months have been added yet")
        return
        
    for date, month_obj in months_dict.items():
        total = month_obj.calculate_total_month_due()
        print(f"  {date}: ${total:.2f}")

def add_additional_cost_interactive(month_date, months_dict):
    if month_date not in months_dict:
        print(f"No month found for {month_date}")
        return
    months_dict[month_date].display_additional_costs()
    amount = get_dollar_input("Additional cost")
    description = input("Enter the description: ")

    if not description: 
        print("description cannot be empty")
        return
    months_dict[month_date].add_additional_cost(amount, description)
    print(f"added: {amount} description: {description}" )
    save_data(months_dict)

def delete_additional_cost_interactive(date_selected, months_dict):
    try:
        datetime.datetime.strptime(date_selected, "%Y-%m")
        print(f"Using month: {date_selected}")  # Confirm we're using the provided month
    except ValueError:
        print("Invalid month format. Please use YYYY-MM format.")
        return 
    
    if date_selected not in months_dict:
        print(f"No month found for {date_selected}")
        return

    if not months_dict[date_selected].additional_costs:
        print("No additional costs to delete.")
        return
    
    months_dict[date_selected].display_additional_costs()
        
    number_to_delete = input("Which additional cost to delete? (Enter #): ")
    months_dict[date_selected].delete_additional_cost(number_to_delete)
    save_data(months_dict)

    
# IO helpers 
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