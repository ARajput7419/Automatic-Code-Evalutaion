import re
import requests as req
import os


def get_metadata(language='java', version_index=0, std_in='', script=''):
    metadata = {'clientId': '26558e6412ef9b47e68c356c08e24eb7',
                'clientSecret': '43c73c299f602fbb7dacb3023bd0e64a6068a0f18ffbd81f327b840e959a187',
                'language': language,
                'versionIndex': version_index,
                'stdin': std_in,
                'script': script
                }
    return metadata


def read_file(filename):
    text = None
    with open(filename, 'r') as file:
        text = file.read()
    return text


def get_name_roll(filename):
    if is_valid_filename(filename):
        prefix_compo = filename.split("_")
        name = prefix_compo[0].strip()
        roll_no = prefix_compo[1].strip()
        return [name, roll_no]
    else:
        return None


def supported_ext() -> list:
    return ['py', 'java', 'cpp', 'c', 'js']


def ext_to_lang() -> dict:
    return {'py': ('python3', 4), 'java': ('java', 4), 'cpp': ('cpp', 5), 'c': ('c', 5), 'js': ('rhino', 2)}


def is_roll(roll):
    obj = re.compile(r"[0-9]+")
    return bool(obj.fullmatch(roll))


def isname(name):
    obj = re.compile(r"[a-zA-Z ]+")
    return bool(obj.fullmatch(name))


def is_valid_filename(filename: str) -> bool:
    prefix_compo = filename.split("_")
    if len(prefix_compo) != 2:
        return False
    name = prefix_compo[0].strip()
    roll_no = prefix_compo[1].strip()
    return isname(name) and is_roll(roll_no)


def verify_file(filename: str) -> bool:
    file_components = filename.split(".")
    if len(file_components) != 2:
        return False
    main_name = file_components[0].strip()
    extension = file_components[1].strip()
    if (extension not in supported_ext()) or (not is_valid_filename(main_name)):
        return False
    return True


def execute(metadata):
    response = req.post("https://api.jdoodle.com/v1/execute", json=metadata)
    return response.json()


def any_error(response):
    return response['statusCode'] != 200


def get_time_memory(response):
    return response['cpuTime'] + " s", response['memory'] + " kb"


def get_ex(filename):
    temp = filename.split(".")
    if len(temp) != 2:
        return None
    else:
        return temp[1].strip()


def get_testcases(filename, std_in='', automated=False):
    data = read_file(filename)
    if not automated:
        return data
    else:
        return output(filename, std_in)


def output(filename, std_in=''):
    data = read_file(filename)
    extension = get_ex(filename)
    if extension not in supported_ext():
        raise Exception(extension, " is not supported ")
    else:
        language_details = ext_to_lang()[extension]
        metadata = get_metadata(language=language_details[0], version_index=language_details[1], std_in=std_in,
                                script=data)
        response = execute(metadata)
        if any_error(response):
            raise Exception(response['error'])
        else:
            return [response['output'], get_time_memory(response)]


if __name__ == '__main__':
    code_file = input("Enter your code file absolute path\n")
    testcase_file = input("Enter test case file absolute path\n")
    automated = input(" Do you want to automate test cases [Y/N]\n")
    if automated in ['y', 'Y']:
        automated = True
    else:
        automated = False

    std_in = ''
    if automated:
        choice = input("Any input to test case file [Y/N]\n")
        if choice in ['y', 'Y']:
            std_in = input("Give Input\n")
    testcases = get_testcases(testcase_file, std_in, automated)

    actual_output = output(code_file, testcases)

    # student processing is left only
