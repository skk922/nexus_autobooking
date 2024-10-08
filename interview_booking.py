from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd
import yaml
import math
import os
import time

conf = yaml.load(open('/Users/sk/LocalFolder/Working_Directory/PyCharm/Nexus_booking/tempVariables.yml'), Loader=yaml.FullLoader)
dir_path = os.path.expanduser(os.path.join("~", conf['local_file_path']))

myId = conf['username']
myPassword = conf['pwd']
myLocElement = conf['loc_element']

url = conf['url'] 
auth_codes = os.path.join(dir_path, conf['ttp_2f_auth_codes_path'])
used_ttp_auth_codes = os.path.join(dir_path, conf['used_ttp_auth_codes_path'])
active_ttp_auth_codes = os.path.join(dir_path, conf['active_ttp_auth_code_path'])

time_elem_id_map_path = os.path.join(dir_path, conf['time_elem_id_map_path'])

print(pd.read_csv(time_elem_id_map_path))



org_2f_auth_codes = pd.read_csv(auth_codes,header=None, names=['codes'])['codes'].tolist()
try:
    unused_2f_auth_codes = pd.read_csv(active_ttp_auth_codes)['0'].tolist()
except:
    unused_2f_auth_codes=[]

if len(unused_2f_auth_codes) == 0:
    ttp_2f_auth_codes = org_2f_auth_codes
else:
    ttp_2f_auth_codes = unused_2f_auth_codes
    
print(ttp_2f_auth_codes)


def pull_2fcode(codes):
    use_code = codes.pop(0)
    #with open('/Users/sk/LocalFolder/Working_Directory/NEXUS_Autobooking/used_ttp_backup_codes.csv','a') as fd:
    with open(used_ttp_auth_codes, 'a') as fd:
        fd.write("\n" + use_code)
        fd.close()
        
    # pd.DataFrame(codes,index=None).to_csv("/Users/sk/LocalFolder/Working_Directory/NEXUS_Autobooking/remaining_ttp_backup_codes.csv")
    pd.DataFrame(codes,index=None).to_csv(active_ttp_auth_codes)
    return use_code



def wait_for_next_page(ele):
    try:
        element_present = EC.presence_of_element_located((By.XPATH, ele))
        WebDriverWait(driver, 60).until(element_present)
    finally:
        print("Timed out waiting for page to load")
        
      
        
def get_cal_format_row_col_values(dt):
    month_srt_dt = dt.replace(day=1)
    month_st_day_of_week = (month_srt_dt.weekday() + 1)%7


    dt_row_num = math.floor((dt.day + month_st_day_of_week - 1)/7)
    dt_col_num = (dt.weekday() + 1)%7
    
    day_ext = dt.day
    mon_str = dt.strftime("%B").upper()

    return (mon_str, dt_row_num, dt_col_num, day_ext)



def create_time_id(slot, day, time_elem_map_path):
    print(slot, day, time_elem_map_path)
    time_elem_map = pd.read_csv(time_elem_map_path)
    time_elem_map = time_elem_map.astype({'slot_number': object})
    time_elem_map_lst = time_elem_map.loc[time_elem_map['time_slot'] == slot, ['prefix_str','day','slot_number','sufix_str']].values.flatten().tolist()

    print(time_elem_map_lst)
    
    time_ele_id = ''.join([str(i) for i in time_elem_map_lst]).format(day)
    print(time_ele_id)
    return time_ele_id

def login(myurl, username, password, appt_date, driver, time_id_map_path=time_elem_id_map_path):

    driver.get(myurl)

    #1: TTP Home Page - Click Login Button
    login_button_ele_path = "//*[@id='app-navbar']/ul[2]/li[2]/input"
    time.sleep(0.3)
    
    driver.find_element(By.XPATH, login_button_ele_path).click()


    #2: Consent pop page - Click 'Consent & Continue' Button
    driver.find_element(By.XPATH, "//*[@id='security-warn']/div/div/div[3]/div/div[1]/button").click()


    #3: Login.gov Page
    driver.find_element(By.ID, "user_email").send_keys(username)
    driver.find_element(By.NAME, "user[password]").send_keys(password)
    driver.find_element(By.XPATH, "//*[@id='new_user']/lg-submit-button/button").click()


    #4: Two Factor Auth Page
    new_auth_code = pull_2fcode(ttp_2f_auth_codes)
    print(new_auth_code)
    
    #next_ele_xpath = "/html/body/main/div/form/lg-one-time-code-input/lg-validated-field/div/input[2]"
    next_ele_xpath_bc = "//*[@id='backup_code_verification_form_backup_code']"
    wait_for_next_page(next_ele_xpath_bc)
    driver.find_element(By.XPATH, next_ele_xpath_bc).send_keys(new_auth_code)
    driver.find_element(By.XPATH, "/html/body/main/div/form/lg-submit-button/button").click()


    #5: Dashboard Page - Reschedule Interview Button Click
    next_ele_xpath_ri = "/html/body/go-app/div/go-dashboard/div/div/div[2]/div/div/div/div/div/div[2]/div[1]/div/div/div/div[1]/div/div[4]/div/div[1]/button"
    wait_for_next_page(next_ele_xpath_ri)
    # driver.find_element(By.XPATH, next_ele_xpath_ri).click()
    element9 = driver.find_element(By.XPATH, next_ele_xpath_ri)
    driver.execute_script("arguments[0].click();", element9)
    
    
    #6: Schedule Appointment - Select 'In-Person' and click 'Apply'
    next_ele_xpath_ip = "//*[@id='inPerson']"
    wait_for_next_page(next_ele_xpath_ip)
    time.sleep(1.5)
    # driver.find_element(By.XPATH, next_ele_xpath_ip).click()
    element8 = driver.find_element(By.XPATH, next_ele_xpath_ip)
    driver.execute_script("arguments[0].click();", element8)

    next_ele_xpath_ap = "//*[@id='next']"
    wait_for_next_page(next_ele_xpath_ap)
    # driver.find_element(By.XPATH, next_ele_xpath_ap).click()
    element7 = driver.find_element(By.XPATH, next_ele_xpath_ap)
    driver.execute_script("arguments[0].click();", element7)
    
    
    #7: Location and Date - Click on location of interest and if Date is available click CHoose This Date
    next_ele_xpath_loc = "//*[@id='centerDetails{}']".format(myLocElement) # <<<---- 
    wait_for_next_page(next_ele_xpath_loc)
    # driver.find_element(By.XPATH, next_ele_xpath_loc).click()
    element5 = driver.find_element(By.XPATH, next_ele_xpath_loc)
    driver.execute_script("arguments[0].click();", element5)

    time.sleep(1.5)
    next_ele_xpath_ctloc = "//*[@id='popover{}']/div/div/div[2]/button".format(myLocElement) # <<<---- 
    wait_for_next_page(next_ele_xpath_ctloc)
    # driver.find_element(By.XPATH, next_ele_xpath_ctloc).click()
    element6 = driver.find_element(By.XPATH, next_ele_xpath_ctloc)
    driver.execute_script("arguments[0].click();", element6)
   
    
    #8: Appointment DATE Page: Choose a date and click on 'Choose This Date Button' 
    dt_attr = get_cal_format_row_col_values(appt_date)
    reusable_string_uisng_dates = "GENERAL_REUSABLE.MONTHS." + dt_attr[0] + str(dt_attr[1]) + '_' + str(dt_attr[2]) + '_' + str(dt_attr[3])

    next_ele_id_dt = "day" + reusable_string_uisng_dates
    next_ele_xpath_dt = "//*[@id='{}']".format(next_ele_id_dt)
    print(next_ele_xpath_dt)
    wait_for_next_page(next_ele_xpath_dt)
    #driver.find_element(By.XPATH, next_ele_xpath_dt).click()
    element3 = driver.find_element(By.XPATH, next_ele_xpath_dt)
    driver.execute_script("arguments[0].click();", element3)

    partial_xpath1 = "popover" + reusable_string_uisng_dates
    next_ele_xpath_choose_button = "//*[@id='{}']/div/div/div[3]/button".format(partial_xpath1)
    print(next_ele_xpath_choose_button)
    wait_for_next_page(next_ele_xpath_choose_button)
    # driver.find_element(By.XPATH, next_ele_xpath_choose_button).click()
    element4 = driver.find_element(By.XPATH, next_ele_xpath_choose_button)
    driver.execute_script("arguments[0].click();", element4)
    
    
    #9: Appointment TIME Page: Choose a time and click on 'Choose This TIme' button
    time_attr = create_time_id(str(appt_date.hour) + ':' + str(appt_date.minute), appt_date.day, time_id_map_path)
    print("time_attr: ", time_attr)
    
    next_ele_xpath_time = "//*[@id='{}']".format(time_attr)
    print(next_ele_xpath_time)
    wait_for_next_page(next_ele_xpath_time)
    time.sleep(0.3)
    #driver.find_element(By.XPATH, next_ele_xpath_time).click()
    element1 = driver.find_element(By.XPATH, next_ele_xpath_time)
    driver.execute_script("arguments[0].click();", element1)
    
    partial_xpath2 = time_attr.replace("btn", "popover")
    next_ele_xpath_time_choose_button = "//*[@id='{}']/div/div/div[4]/button".format(partial_xpath2)
    print(next_ele_xpath_time_choose_button)
    wait_for_next_page(next_ele_xpath_time_choose_button)
    time.sleep(0.15)
    #driver.find_element(By.XPATH, next_ele_xpath_time_choose_button).click()
    element2 = driver.find_element(By.XPATH, next_ele_xpath_time_choose_button)
    driver.execute_script("arguments[0].click();", element2)
    
    
    #10: Submission Page: Give reason and submit
    next_ele_xpath_reason = "//*[@id='reason']"
    wait_for_next_page(next_ele_xpath_reason)
    driver.find_element(By.XPATH, next_ele_xpath_reason).send_keys("Earlier Appointment")

    # SUBMIT Button Click
    driver.find_element(By.XPATH, "//*[@id='submitAppointment']").click()

    return ["Completed booking successfully", appt_date]


def automatic_booking(appt_time, driver):
    message = login(url, myId, myPassword, appt_time, driver, time_elem_id_map_path)
    return message



# TESTING ONLY
# from selenium import webdriver
# appt_time = datetime.strptime('2024-10-16T08:40', '%Y-%m-%dT%H:%M')
# driver = webdriver.Firefox()
# final_message = automatic_booking(appt_time, driver)




    

