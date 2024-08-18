This code package is a rudimentary implementation to monitor and book NEXUS interview appointments automatically on your local laptop/desktop. 
The appointment monitoring part of the code was taken from internet research and modified as needed in this package. So credit goes to the orginal owner for that part  

Things to Consider before dowloading and using the package:
1) The package is tested and used to book my own appoinmtment on MacBook Pro with M1 chipset
2) Module versions used to test the code are mentioned in 'requirements' file
3) This code package only supports NEXUS appointment booking at BLAINE, WA location
   
    a) If you want to use the code for a different location, you need to edit 'time_element_id_map_blaine.csv' file and provide location specific time slot mappings
   
    b) This can be done by manually navigating and inspecting the html code on Appointment Time webpage
   
    c) Also, in tempVariables.yml file update location_id, location_name and loc_element (you need to do a bit research for this on the html code)
   
5) The code assumes that you have 2-FACTOR AUTHENTICATION ENABLED on your ttp portal account
6) For obvious reasons, this script uses backup codes downloaded from ttp portal to satisfy 2-factor auth
7) For the code to work properly you need to login to https://secure.login.gov and disable all of the following authentication methods
   
   a) Add phone number
   
   b) Add authentication apps
   
   c) Add face or touch unlock
   
   d) Add security key
   
   e) Add your government employee ID
   
9) Then Generate backup codes, download the codes and add them to 'ttp_backup_codes.csv' file in the package

   a) As a good practice only add 7 of the 10 generated codes to the 'ttp_backup_codes.csv' file

   b) Save the remaining 3 in a different file so that you can use them when logging in manually

11) This would force the ttp portal (https://ttp.cbp.dhs.gov) to default to using backup codes
12) 'tempVariables.yml' file has the ttp login credentials, configuration variables and directory paths used in the package. Make sure you update this file before executing the code

    a) In all .py files (except __init__) update the yaml file location based on your local directory structure

13) Lastly if 2-FACTOR AUTHENTICATION IS NOT ENABLED on your ttp portal account,

    a) comment out code in interview_booking.py file -> Under the comment "#4: Two Factor Auth Page" (lines 114-121)

    b) This is not tested but I believe it would support your use-case
