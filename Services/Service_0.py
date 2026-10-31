from sortify.console import flows

service_name = "File Organizer Extension Based - [flat]"
service_uuid = "a1b2c3"
service_description = "Organizes files in a folder by their extensions excluding subfolders"


def run():
    flows.organize_by_extension(False)


service_method = run
