from sortify.console import flows

service_name = "Undo a previous run"
service_uuid = "u1n2d3"
service_description = "Put back the files moved, renamed or deleted by one of the last runs"


def run():
    flows.undo_last_run()


service_method = run
