import os

from datetime import datetime

def group_by_extension(items):
    extensions = {}
    no_extension = []

    for src, filename in items:
        ext = os.path.splitext(filename)[1].lower()
        if ext:
            extensions.setdefault(ext, []).append((src, filename))
        else:
            no_extension.append((src, filename))

    return extensions, no_extension

def group_by_date_day(items):

    dates = {}

    for src,filename in items:
        time  = os.path.getmtime(src)
        file_date = (datetime.fromtimestamp(time)).strftime('%Y-%m-%d')
        dates.setdefault(file_date,[]).append((src,filename))

    return dates
