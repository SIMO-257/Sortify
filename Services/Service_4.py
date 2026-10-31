from sortify.console import flows

service_name = "Files Cleaner By Name - [Flat]"
service_uuid = "a2b2d3"
service_description = "Delete all files based on the file name excluding sub folders"


def run():
    flows.clean_by_name(False)


service_method = run
