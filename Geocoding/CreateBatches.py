## Expands addresses and creates batch files of addresses for Census geocoding API
## Addresses that are a range of numbers e.g: 5712 16 will be expanded to multiple rows such as 5712, 5713, 5714, etc.
## Saves batches of 10,000 rows including headers.

import pandas as pd
import numpy as np
import os    

# Set current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load service line data
service_line = pd.read_csv("../T096318_Responsive_Document.csv")

# Drop exact duplicates. Ex: 671 75 N Michigan Ave appears twice with same information
# Some address duplicates contain differing service line information. One might say suspected lead while the other says Galvanized needs replacement
service_line = service_line.drop_duplicates()

#Arrays containing the addresses that are expandable and not expandable for future reference
unexpandable = []
expandable= []

# Function to create ending range value when ending number is just last digits
# For example the address 6355 57 S WASHTENAW AVE. We will take the ending range value 57 and return the value 6357.
# This lets us iterate the range and expand addresses easier.
def ReplaceLastNum(start, end):
    length = len(str(end))
    num = str(start)[:-length]
    num= num + str(end)
    #print(start, end, num)

    return int(num)
    
# Function to generate individual addresses from an address range ex: 63 65 E 79TH ST
# This should return 63 E 79TH ST, 64 E 79TH ST, 65 E 79TH ST
def ExpandAddresses(address):
    address_parts = address.split()
    
    # Check if there are two numbers separated by a space (e.g., "63 65")
    # This means the address is expandable
    if len(address_parts) >= 3 and address_parts[0].isdigit() and address_parts[1].isdigit():

        #print(address)
        #First and second numbers of range
        start_num = int(address_parts[0])  
        end_num = int(address_parts[1])    

        # Rest of the address (e.g., "E 79TH ST AVE")
        base_address = ' '.join(address_parts[2:])  

        # If the end of the range is larger than the beginning of the range we can simply iterate from the beginning and add one till we get
        # till the end of the range
        if end_num > start_num:
            #Add address to expandable address list
            expandable.append(address)  
            exp=  [f"{i} {base_address}" for i in range(start_num, end_num + 1, 2)]
            #print(address, exp)
            return exp
        
        # If the end of the range is smaller than the beginning of the range such as 6355 and 57 then we need to make the end larger so we can 
        # iterate all the addresses. We will convert 57 to 6357 59 Stree
        elif start_num > end_num and end_num != 0:
            #Call function to get end of range number
            end = ReplaceLastNum(start_num, end_num)
            #Add address to expandable address list
            expandable.append(address)
            exp = [f"{i} {base_address}" for i in range(start_num, end + 1, 2)]
            #print(address, exp)
            return exp
        
        # These are addresses where the end num is 00. From my research this appears to represent a block but I do not know how to expand this
        else:
            #Add address to unexpandable address list
            unexpandable.append(address)
            #print(address)
            return [address]
            
    # These are normal addresses without a range
    else:
        #Add address to unexpandable address list
        unexpandable.append(address)
        #print(address)
        return [address]


#Drop duplicates, keep last instance since that is usually the one to contain more information
#service_line.drop_duplicates(subset=["Address"], keep= "last")

# Create an empty list to hold all the expanded addresses with their corresponding data
expanded_addresses = []
# Loop over each row and expand addresses with ranges
for index, row in service_line.iterrows():
    expanded_addresses.extend(ExpandAddresses(row['Address']))
    #print(address, expanded_address_list)

# Create a new DataFrame for expanded addresses with their corresponding data
expanded_df = pd.DataFrame(expanded_addresses)

# Add column name for address. Add other data that the census geocoder requires
expanded_df.reset_index(drop= True, inplace= True)
expanded_df= expanded_df.rename(columns={0: "address"})
expanded_df["Unique ID"] = expanded_df.index+1
expanded_df['City'] = 'Chicago'
expanded_df['State'] = 'IL'
expanded_df['ZIP'] = np.nan

#Reorganize columns so unique id is first
column_order = ["Unique ID"] + [col for col in expanded_df.columns if col != "Unique ID"]
expanded_df = expanded_df[column_order]

# Save the expanded data to a CSV file
expanded_df.to_csv("./ExpandedAddressBatches/geocode_addresses.csv", index=False)

#Create batches of size 10,000 for census geocoder

batch_size = 9999
for i in range(0, len(expanded_df), batch_size):
    batch = expanded_df.iloc[i:i+batch_size]
    batch.to_csv(f"./ExpandedAddressBatches/geocode_address_batch_{i//batch_size + 1}.csv", index=False)
