from sortify.console import flows

service_name = "Files Organizer Date Based(Days) - [flat]"
service_uuid = "a1l2n4"
service_description = "Organizing files based on their date(days) excluding subfolders"


def run():
    flows.organize_by_date(False)


service_method = run
