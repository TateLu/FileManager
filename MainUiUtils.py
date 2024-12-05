import os


def get_directory(self, path):
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    else:
        raise ValueError("The provided path is neither a file nor a directory.")