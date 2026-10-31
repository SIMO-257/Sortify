from Tasks import flows

service_name = "Files Cleaner Extension Based - [recursive]"
service_uuid = "a2b2c3"
service_description = "Delete files in a folder by their extensions including subfolders"


def run():
    flows.clean_by_extension(True)


service_method = run
