from sortify.console import flows

service_name = "Files Organizer Date Based(Days) - [recursive]"
service_uuid = "a1l6n4"
service_description = "Organizing files based on their date(days) including subfolders"


def run():
    flows.organize_by_date(True)


service_method = run
