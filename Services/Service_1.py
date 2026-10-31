from sortify.console import flows

service_name = "File Organizer Extension Based - [recursive]"
service_uuid = "d4e5f6"
service_description = "Organizes all files recursively including those inside subfolders"


def run():
    flows.organize_by_extension(True)


service_method = run
