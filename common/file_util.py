import os
import pickle


def check_if_exists(file_path):
    return file_path is not None and os.path.exists(file_path)


def get_file_path_list(dir_path, is_recursive=False, is_sorted=False):
    file_list = list()
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file)
        if os.path.isfile(path):
            file_list.append(path)
        elif is_recursive:
            file_list.extend(get_file_path_list(path, is_recursive))
    return sorted(file_list) if is_sorted else file_list


def get_dir_path_list(dir_path, is_recursive=False, is_sorted=False):
    dir_list = list()
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file)
        if os.path.isdir(path):
            dir_list.append(path)
        elif is_recursive:
            dir_list.extend(get_dir_path_list(path, is_recursive))
    return sorted(dir_list) if is_sorted else dir_list


def make_dirs(dir_path):
    if len(dir_path) > 0 and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def make_parent_dirs(file_path):
    dir_path = os.path.dirname(file_path)
    make_dirs(dir_path)


def save_pickle(entity, file_path):
    make_parent_dirs(file_path)
    with open(file_path, 'wb') as fp:
        pickle.dump(entity, fp)


def load_pickle(file_path):
    with open(file_path, 'rb') as fp:
        return pickle.load(fp)
