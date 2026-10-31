from sortify.console import flows

service_name = "File Cleaner Extension Based - [flat]"
service_uuid = "a1b2c8"
service_description = "Delete files in a folder by their extensions excluding subfolders"


def run():
    flows.clean_by_extension(False)


service_method = run
