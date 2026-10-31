from sortify.console import flows

service_name = "Files Cleaner By Name - [recursive]"
service_uuid = "a2h2d3"
service_description = "Delete all files based on the file name including sub folders"


def run():
    flows.clean_by_name(True)


service_method = run
