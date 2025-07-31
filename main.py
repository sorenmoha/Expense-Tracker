import argparse
import sys

from month import Month
from utils import create_new_month, list_months, delete_month, edit_month, save_data, load_data, add_additional_cost_interactive, add_payment_cost_interactive, edit_additional_cost_interactive, delete_additional_cost_interactive  

def main():

    months_dict = load_data()

    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Personal Budget Tracker - Track monthly expenses and utilities",
        epilog="""Examples:
  tracker -n                                           Create new month entry
  tracker --new-entry                                  Create new month entry
  tracker --new-entry YYYY-MM                          Create new month entry for specified month
  
  tracker -e YYYY-MM -t rent                           Edit a months rent  
  tracker --edit-month YYYY-MM --edit-utility rent     Edit a months rent
  
  tracker -l                                           List all tracked dates
  tracker --list YYYY-MM                               View summary
  
  tracker -d 2025-01                                   Delete a month entry 
  tracker --delete-month                               Delete a month entry
  
  tracker -a                                           Add additional cost 
  tracker --add-cost                                   Add additional cost 

  tracker -dc 2025-01                                  Delete an additional cost for specified month
  tracker --delete-cost 2025-01                        Delete an additional cost for specified month   
  
  tracker -p 2025-01                                   Add payment for specified month
  tracker --paid 2025-01                               Add payment for specified month
  """,
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-n", "--new-entry", metavar="YYYY-MM", nargs="?", const="prompt",
            help="Create a new month entry. Optionally specify month (YYYY-MM)")
    parser.add_argument("-d", "--delete-month", metavar="YYYY-MM",
                        help="Delete an existing month")
    parser.add_argument("-e", "--edit-month", metavar="YYYY-MM", 
                    help="Edit an existing month")
    parser.add_argument("-t", "--edit-utility", choices=["rent", "heating", "electric", "water", "internet"], 
                    help="Which value to edit")
    parser.add_argument("-l", "--list", metavar="YYYY-MM", nargs="?", const=None,
                    help="List all months or show specific month summary (YYYY-MM)")
    parser.add_argument("-a", "--add-cost", metavar="YYYY-MM",
                    help="Add additional cost to an existing month (interactive)")
    parser.add_argument("-ca", "--cost-amount", type=float, metavar="AMOUNT",
                    help="Amount for the additional cost")
    parser.add_argument("-cd", "--cost-description", metavar="DESCRIPTION",
                    help="Description for the additional cost")
    parser.add_argument("-dc", "--delete-cost", metavar="YYYY-MM",
            help="Delete an additional cost entry for (required) specified date")
    parser.add_argument("-ec", "--edit-cost", metavar="YYYY-MM",
            help="Edit an additional cost entry for (required) specified date")
    parser.add_argument("-p", "--paid", metavar="YYYY-MM",
            help="Add amount paid for the month")
    
    if len(sys.argv) == 1:
        parser.error("No command provided. Use --help for usage information.")
    
    args = parser.parse_args()
    
    try:
        if args.new_entry:
            if args.new_entry != "prompt" and args.new_entry in months_dict:
                print (f"Existing entry detected for {args.new_entry}")
                return
            else:
                new_month = create_new_month(args.new_entry if args.new_entry != "prompt" else None)
                if new_month:  
                    months_dict[new_month.month_name] = new_month
                    save_data(months_dict)

        elif args.edit_month:
            if not args.edit_utility:
                parser.error("--edit-month requires --edit-utility")
            edit_month(args.edit_month, args.edit_utility, months_dict)
            
        elif args.delete_month:
            delete_month(args.delete_month, months_dict)
            
        elif args.add_cost:
            add_additional_cost_interactive(args.add_cost, months_dict)

        elif args.edit_cost:
            edit_additional_cost_interactive(args.edit_cost, months_dict)

        elif args.delete_cost:
            delete_additional_cost_interactive(args.delete_cost, months_dict)
            
        elif args.paid:
            add_payment_cost_interactive(args.paid, months_dict)
            
        elif 'list' in vars(args):  
            if args.list is None:  
                list_months(months_dict)
            else:  
                print(f"displaying summary for {args.list}")
                if args.list in months_dict:
                    months_dict[args.list].display_summary()
                else:
                    print(f"No month found for {args.list}")
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        print("Use --help for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()