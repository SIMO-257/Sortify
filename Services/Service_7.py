from Tasks import flows

service_name = "Files Replacer Extension Based - [recursive]"
service_uuid = "a1l2n3"
service_description = "Moving files from a folder to another based on extension including subfolders"


def run():
    flows.move_by_extension(True)


service_method = run
