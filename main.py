import argparse
import sys

from month import Month
from utils import create_new_month, view_month, list_months, edit_month, save_data, load_data  

def main():

    months_dict = load_data()

    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Personal Budget Tracker - Track monthly expenses and utilities",
        epilog="""Examples:
  tracker -n                          Create a new month entry
  tracker --new-entry                 Create a new month entry
  tracker --new-entry 2025-01         Create a new month entry for January 2025
  
  tracker -e 2025-01 -t rent          Edit January 2025 rent  
  tracker --edit-month 2025-01 --edit-value rent    Edit January 2025 rent
  
  tracker -l                          List all tracked months
  tracker --list 2025-01              View January 2025 summary""",
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-n", "--new-entry", metavar="YYYY-MM", nargs="?", const="prompt",
            help="Create a new month entry. Optionally specify month (YYYY-MM)")
    parser.add_argument("-e", "--edit-month", metavar="YYYY-MM", 
                    help="Edit an existing month")
    parser.add_argument("-t", "--edit-value", choices=["rent", "heating", "electric", "water", "internet"], 
                    help="Which value to edit")
    parser.add_argument("-l", "--list", metavar="YYYY-MM", nargs="?", const=None,
                    help="List all months or show specific month summary (YYYY-MM)")
                   
    
    # Check if no arguments provided
    if len(sys.argv) == 1:
        parser.error("No command provided. Use --help for usage information.")
    
    args = parser.parse_args()
    
    try:
        if args.new_entry:
            new_month = create_new_month(args.new_entry if args.new_entry != "prompt" else None)
            if new_month:  
                months_dict[new_month.month_name] = new_month
                save_data(months_dict)

        elif args.edit_month:
            if not args.edit_value:
                parser.error("--edit-month requires --edit-value")
            edit_month(args.edit_month, args.edit_value, months_dict)
            save_data(months_dict)

        elif 'list' in vars(args):  # --list was used (with or without value)
            if args.list is None:  # Just --list (show all)
                list_months(months_dict)
            else:  # --list 2025-01 (show specific)
                view_month(args.list, months_dict)

        else:
            parser.error("Invalid command combination. Use --help for usage information.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        print("Use --help for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()