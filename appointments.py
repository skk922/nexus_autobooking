import requests
import time
import sys
from datetime import datetime, timedelta
import os
import yaml
import interview_booking as ib
from selenium import webdriver
import time

conf = yaml.load(open('/Users/sk/LocalFolder/Working_Directory/PyCharm/Nexus_booking/tempVariables.yml'), Loader=yaml.FullLoader)
dir_path = os.path.expanduser(os.path.join("~", conf['local_file_path']))

appointments_url = conf['appointments_url']
time_wait = conf['appt_check_wait_time']

# List of Global Entry locations
LOCATION_IDS = {
    # 'Blaine_WA': 5020  # 'Champlain_NY': 5021 -- Test Location
    conf['location_name']: conf['location_id']
}


# Dates
now = datetime.strptime(conf['start_date'], '%Y-%m-%dT%H:%M')
future_date = datetime.strptime(conf['end_date'], '%Y-%m-%dT%H:%M')
print(now, future_date)

# Number of days into the future to look for appointments
days_out = (future_date - now).days


def check_appointments(loc_id):
    url = appointments_url.format(loc_id)
    appointments = requests.get(url).json()
    return appointments


def appointment_in_timeframe(now, future_date, appt_datetime):
    if (now <= appt_datetime <= future_date):
        return True
    else:
        return False


def displayNotification(message, title="NEXUS APPT AVAILABLE", subtitle=None, soundname="Crystal"):
    """
        Display an OSX notification with message title an subtitle
        sounds are located in /System/Library/Sounds or ~/Library/Sounds
    """
    titlePart = ''
    if (not title is None):
        titlePart = 'with title "{0}"'.format(title)
    subtitlePart = ''
    if (not subtitle is None):
        subtitlePart = 'subtitle "{0}"'.format(subtitle)
    soundnamePart = ''
    if (not soundname is None):
        soundnamePart = 'sound name "{0}"'.format(soundname)

    appleScriptNotification = 'display notification "{0}" {1} {2} {3}'.format(message, titlePart, subtitlePart,
                                                                              soundnamePart)
    os.system("osascript -e '{0}'".format(appleScriptNotification))

def appointments_booking():
    old_appt_avbl_msg = None
    old_no_appt_for_x_days__msg = None
    old_no_appt_msg = None
    appt_book_successs = ''
    try:
        while True:
            for city, loc_id in LOCATION_IDS.items():
                try:
                    appointments = check_appointments(loc_id)

                except Exception as e:
                    print("Could not retrieve appointments from API.")
                    appointments = []

                if appointments:
                    appt_datetime = datetime.strptime(appointments[0]['startTimestamp'], '%Y-%m-%dT%H:%M')
                    print("appt_datetime: ", appt_datetime)

                # # #TESTING
                # if True:
                #     appt_datetime = datetime.strptime('2024-08-02T00:00', '%Y-%m-%dT%H:%M')

                    if appointment_in_timeframe(now, future_date, appt_datetime):
                        message = datetime.now().strftime("%Y-%m-%d %H:%M") \
                                  + "\t {}: Found an appointment at {}!".format(city, appt_datetime)  # appointments[0]['startTimestamp'])

                        if message != old_appt_avbl_msg:
                            old_appt_avbl_msg = message
                            displayNotification(message)
                            print(message)

                            ## Calling Auto Booking Function
                            try:
                                # if appointments[0]['locationId'] == 5020:
                                print("Trying to book the Blaine appointment automatically")
                                driver = webdriver.Firefox()
                                final_message = ib.automatic_booking(appt_datetime, driver)
                                print(final_message[0], "New Appointment Time: ".format(final_message[1]))

                                appt_book_successs = 1
                                displayNotification(final_message)
                                break
                            except Exception as e:
                                print(e)
                                continue
                    else:
                        no_appt_x_day_msg = datetime.now().strftime("%Y-%m-%d %H:%M") + " {}: No appointments during the next {} days.".format(city, days_out)
                        if no_appt_x_day_msg != old_no_appt_for_x_days__msg:
                            print(no_appt_x_day_msg + "\t But - " + "{}: Found an appointment at {}!".format(city, appointments[0]['startTimestamp']))
                else:
                    if datetime.now().time().minute % 2 == 0:
                        no_appt_msg = datetime.now().strftime("%Y-%m-%d %H:%M") + " {}: No appointments during the next {} days.".format(city, days_out)
                        if no_appt_msg != old_no_appt_msg:
                            print(no_appt_msg)
                            old_no_appt_msg = no_appt_msg

            if appt_book_successs == 1:
                break

            time.sleep(time_wait)
    except KeyboardInterrupt:
        sys.exit(0)

