import os
import yaml
import appointments as appt

conf = yaml.load(open('/Users/sk/LocalFolder/Working_Directory/PyCharm/Nexus_booking/tempVariables.yml'),
                 Loader=yaml.FullLoader)
dir_path = os.path.expanduser(os.path.join("~", conf['local_file_path']))
print(dir_path)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    appt.appointments_booking()





