from sortify.console import flows

service_name = "Empty Directories Cleaner"
service_uuid = "a1b2c7"
service_description = "Delete empty folders in the given path"


def run():
    flows.clean_empty_folders()


service_method = run
