import os


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
