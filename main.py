import argparse
import sys

from month import Month
from utils import create_new_month, get_month_input, get_dollar_input, view_month, list_months

def main():

    months_dict = {}
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Personal Budget Tracker - Track monthly expenses and utilities",
        epilog="""Examples:
  tracker --new-entry                 Create a new month entry
  tracker --edit-entry 2025-01        Edit January 2025 expenses  
  tracker --view 2025-01              View January 2025 summary
  tracker --list                      List all tracked months""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--new-entry", action="store_true", 
                       help="Create a new month entry")
    parser.add_argument("--view", metavar="YYYY-MM", 
                       help="View month summary (format: YYYY-MM)")
    parser.add_argument("--list", action="store_true", 
                       help="List all tracked months")
    
    # Check if no arguments provided
    if len(sys.argv) == 1:
        parser.error("No command provided. Use --help for usage information.")
    
    args = parser.parse_args()
    
    try:
        if args.new_entry:
            new_month = create_new_month()
            months_dict[new_month.month_name] = new_month    ## adds the month name (2025-04) to the months dictionary

        elif args.view:
            view_month(args.view, months_dict)

        elif args.list:
            list_months(months_dict)

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