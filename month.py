class Month:
    def __init__(self, month_name, rent, heating, electric, water, internet, additional_costs: list):
        
        self.month_name = month_name
        self.rent = rent
        self.heating = heating
        self.electric = electric
        self.water = water
        self.internet = internet
        self.additional_costs = additional_costs

        #for validation 
        costs = {
            'rent': rent,
            'heating': heating,
            'electric': electric,
            'water': water,
            'internet': internet,
            
        }

        for cost_name, cost_value in costs.items():
            if cost_value < 0:
                raise ValueError(f"{cost_name} cost cannot be negative")

        if not isinstance(additional_costs, list):
         raise ValueError("additional_costs must be a list")

    def calculate_total_utilities(self):
        return self.heating + self.electric + self.water + self.internet
    
    def calculate_utilities_per_roommate(self):
        total_utilities = self.calculate_total_utilities()
        return total_utilities / 2                             # ADD: number of roommates adjustment in settings?
          
    def calculate_total_housing_month_due(self):
        utilities_per_roommate = self.calculate_utilities_per_roommate()
        return self.rent + utilities_per_roommate
                       
    def calculate_total_month_due(self): 
        total_housing_month_due = self.calculate_total_housing_month_due()
        sum_of_additional_costs =  self.calculate_total_additional_costs()
        return sum_of_additional_costs + total_housing_month_due
    
    def calculate_total_additional_costs(self):
        return sum(cost["amount"] for cost in self.additional_costs)

    def add_additional_cost(self, amount, description):
        self.display_additional_costs()
        cost_entry = {"amount": amount, "description": description}
        self.additional_costs.append(cost_entry)
        print(f"Added: ${amount:.2f} - {description}")
        self.display_additional_costs()

    def edit_additional_cost(self, number_to_edit):
        try: 
            number = int(number_to_edit) 
        except ValueError:
            print(f"Invalid entry number: {number_to_edit}")
            return False
        
        if number < 1 or number > len(self.additional_costs):
            print(f"no entry found for {number}")
            return False

        index = number - 1

        new_amount_input = input(f"New amount for entry {number_to_edit}: ")
        try:
            amount_to_edit = float(new_amount_input)
        except ValueError:
            print("Invalid amount entered")
            return False
        
        description_to_edit = input(f"New description for entry {number_to_edit}: ")

        cost_entry = {"amount": amount_to_edit, "description": description_to_edit}
        self.additional_costs[index] = cost_entry
        print(f"Updated Entry {number_to_edit}: ${amount_to_edit:.2f} - {description_to_edit}")
        return True

    def delete_additional_cost(self, number_to_delete):
        try: 
            number = int(number_to_delete) 
        except ValueError:
            print(f"Invalid entry number: {number_to_delete}")
            return False
        
        if number < 1 or number > len(self.additional_costs):
            print(f"no entry found for {number}")
            return False
        
        index = number - 1
        
        deleted_item = self.additional_costs[index]
        self.additional_costs.pop(index)
        print(f"Deleted entry {number}: ${deleted_item['amount']:.2f} - {deleted_item['description']}")
        self.display_additional_costs()
        return True

    def display_additional_costs(self):
        print(f"\n ADDITIONAL COSTS:")
        if not self.additional_costs:
            print("No additional costs stored")
        else:
            for i, cost in enumerate(self.additional_costs, 1):
                print(f"   {i}. {cost['description']}: ${cost['amount']:.2f}")
            print("-" * 35)
            print(f"   Total Additional:    ${self.calculate_total_additional_costs():.2f}")

    def display_summary(self):
        print("=" * 50)
        print(f"MONTH SUMMARY: {self.month_name}")
        print("=" * 50)
        
        # Fixed Monthly Costs
        print("\n FIXED MONTHLY COSTS:")
        print(f"   Rent:                ${self.rent:.2f}")
        print(f"   Heating:             ${self.heating:.2f}")
        print(f"   Electric:            ${self.electric:.2f}")
        print(f"   Water:               ${self.water:.2f}")
        print(f"   Internet:            ${self.internet:.2f}")
        print("-" * 35)
        print(f"   Total Utilities:     ${self.calculate_total_utilities():.2f}")
        print(f"   Your Utilities Share: ${self.calculate_utilities_per_roommate():.2f}")
        
        # Housing Total
        print(f"\n TOTAL HOUSING:       ${self.calculate_total_housing_month_due():.2f}")
        
        self.display_additional_costs()
        
        # Grand Total
        print("\n" + "=" * 50)
        print(f" TOTAL MONTH DUE:     ${self.calculate_total_month_due():.2f}")
        print("=" * 50)
        