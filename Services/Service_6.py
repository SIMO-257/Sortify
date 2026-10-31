from sortify.console import flows

service_name = "Files Replacer Extension Based - [flat]"
service_uuid = "a1l2n1"
service_description = "Moving files from a folder to another based on extension excluding subfolders"


def run():
    flows.move_by_extension(False)


service_method = run
