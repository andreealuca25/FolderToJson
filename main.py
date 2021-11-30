import datetime
import json
import os
import sys

folders_and_files_dict = {  # 'folder_path' :
    # { 'level': the depth level of the  directory hierarchy ,
    # 'parent': the parent of the current folder ,
    # 'sub_dirs': a list of subfolders of the current folder,
    # 'sub_files': a list of subfiles of the current folder}
}


def remove_escape_characters(path):
    return path.replace("\\", "/")


def get_size(start_path):  # returns the total size in bytes of all the subfolders and subfiles of a directory
    total_size = 0
    for dir_path, dir_names, file_names in os.walk(start_path):
        for file in file_names:
            fp = os.path.join(dir_path, file)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def non_recursive_search(dir_path):
    try:
        entries = os.listdir(dir_path)
    except OSError:
        print(dir_path, "is not a directory")
        sys.exit()
    files_list = list()
    dirs_list = list()
    for sub_element in entries:
        full_path_element = os.path.join(dir_path, sub_element)
        if os.path.isfile(full_path_element):
            files_list.append(full_path_element)
        elif os.path.isdir(full_path_element):
            dirs_list.append(full_path_element)

    temp_dict = dict()
    temp_dict['level'] = 0
    temp_dict['parent'] = 'none'
    temp_dict['sub_dirs'] = dirs_list
    temp_dict['sub_files'] = files_list
    folders_and_files_dict[dir_path] = temp_dict


def DFS_folder_search(level, dir_path):
    try:
        entries = os.listdir(dir_path)
    except OSError:
        print(dir_path, "is not a directory")
        sys.exit()
    level += 1
    for element in entries:
        sub_dir = os.path.join(dir_path, element)
        if os.path.isdir(sub_dir):  # if the sub_element of the current director is a director
            files_list = list()
            dirs_list = list()
            for sub_element in os.listdir(sub_dir):
                full_path_element = os.path.join(sub_dir, sub_element)
                if os.path.isfile(full_path_element):
                    files_list.append(full_path_element)
                elif os.path.isdir(full_path_element):
                    dirs_list.append(full_path_element)

            temp_dict = dict()
            temp_dict['level'] = level
            temp_dict['sub_dirs'] = dirs_list
            temp_dict['sub_files'] = files_list
            temp_dict['parent'] = dir_path
            folders_and_files_dict[sub_dir] = temp_dict  # adds all the sub_elements
            # of the current director into the folders_and_files_dict
            DFS_folder_search(level, sub_dir)


def generate_info_dict(options, ext_list, dir_path):
    info_dir_dict = {}

    if '0' in options:
        non_recursive_search(dir_path)  # for recursive search in folder
        DFS_folder_search(0, dir_path)
    elif '0' not in options:
        non_recursive_search(dir_path)  # for non-recursive search in folder
    folders = folders_and_files_dict.keys()
    for folder in folders:
        info_dict = {'parent': folders_and_files_dict[folder]['parent'],
                     'level': folders_and_files_dict[folder]['level']}
        if '1' in options:  # total size of the folder
            info_dict['total_size'] = str(get_size(folder)) + ' bytes'
        if '2' in options:  # number of files
            info_dict['nr_of_files'] = len(folders_and_files_dict[folder]['sub_files'])
        if '3' in options:  # number of files with extension
            only_files = [os.path.splitext(x)[1] for x in folders_and_files_dict[folder]['sub_files']]
            only_files_with_ext = [x[1:] for x in only_files if x[1:] in ext_list]  # removes the '.' from the extension
            info_dict['nr_of_files_with_ext'] = len(only_files_with_ext)
        if '4' in options:  # list of subfolders
            info_dict['subfolders'] = [os.path.basename(x) for x in folders_and_files_dict[folder]['sub_dirs']]
        if '5' in options:  # info about each file in the current folder
            files_info = {}
            for file in folders_and_files_dict[folder]['sub_files']:
                stats = os.stat(file)
                file_info = {
                    'file_size': os.path.getsize(file),
                    'creation_time': str(datetime.datetime.fromtimestamp(os.path.getctime(file))),
                    'modified_time': str(datetime.datetime.fromtimestamp(os.path.getmtime(file))),
                    'file_type_and_permissions': stats.st_mode,
                    'device_id': stats.st_dev,
                    'file_owner_id': stats.st_uid,
                    'file_group_id': stats.st_gid,
                }
                files_info[os.path.basename(file)] = file_info
            info_dict['sub_files'] = files_info

        info_dir_dict[os.path.basename(folder)] = info_dict  # adds every required information for each folder
    return info_dir_dict


def generate_json(options, ext_list, dir_path, output_f_name):
    dir_dict = generate_info_dict(options, ext_list, dir_path)
    json_object = json.dumps(dir_dict, indent=4)
    with open(dir_path + '/' + output_f_name, "w") as outfile:
        outfile.write(json_object)
        print("Data successfully written to: ", dir_path + '/' + output_f_name)


if __name__ == '__main__':
    folder_path = input("Enter the path for the folder: ")
    clean_path = remove_escape_characters(folder_path)

    output_file_name = input("Enter the name for the output file (For example: output.json or output.txt) : ")
    extensions = input("Enter the extensions that you want statistics on (For example: txt,pdf,mp3) : ")
    extensions_list = extensions.split(",")
    print("Available options: \n "
          "0. Recursive search \n "
          "1. Total size of the folder \n "
          "2. Number of files \n "
          "3. Number of files with extension \n "
          "4. List of subfolders \n "
          "5. List of subfiles with info about them \n")
    picked_options = input("Enter your options from the above list using the format (For example: 0,2,3,4) : ")
    picked_options_list = picked_options.split(",")
    generate_json(picked_options_list, extensions_list, clean_path, output_file_name)
