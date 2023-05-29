import hashlib
import os
import re


def review(config):
    validations = config['data']
    path_source = config['path_source']

    comments = []

    comments.extend(
        __review_merge_title(
            merge_title=config['merge']['title'],
            validations=__validations_by_type("MERGE_TITLE", validations),
        )
    )

    comments.extend(
        __review_file_content(
            path_code=path_source,
            validations=__validations_by_type("MERGE_FILE_CONTENT", validations),
            path_code_origin=path_source,
        )
    )

    return comments


def __validations_by_type(tp_validation, validations):
    validations_filtered = []

    for validation in validations:
        if validation["type"] == tp_validation:
            validations_filtered.append(validation)

    return validations_filtered


def __review_merge_title(merge_title, validations):
    comments = []

    for validation in validations:
        if not __validate_regex_list(validation['regex'], content=merge_title):
            comment = validation['message']
            comments.append(__create_comment(__generate_md5(comment), comment))

    return comments


def __review_file_content(path_code, validations, path_code_origin):
    comments = []

    for content in os.listdir(path_code):
        path_content = os.path.join(path_code, content)

        if os.path.isfile(path_content):
            comments.extend(__review_file_content_by_file(path_content, validations, path_code_origin))

        elif os.path.isdir(path_content):
            comments.extend(__review_file_content(path_content, validations, path_code_origin))

    return comments


def __review_file_content_by_file(path_content, validations, path_code_origin):
    comments = []

    with open(path_content, 'r') as arquivo:
        content_code = arquivo.read()

        for validation in validations:
            if not __validate_regex_list(validation['regexFile'], path_content):
                continue

            if __verify_if_add_comment(validation, content_code):
                path_to_comment = str(path_content).replace(path_code_origin + '/', '')
                comment = validation['message'].replace("${FILE_PATH}", path_to_comment)
                comments.append(__create_comment(__generate_md5(comment), comment))

    return comments


def __create_comment(comment_id, comment):
    return {
        "id": comment_id,
        "comment": comment,
    }


def __validate_regex(regex, content):
    return re.search(regex, content)


def __validate_regex_list(regex_list, content):
    for regex in regex_list:
        if __validate_regex(regex=regex, content=content):
            return True

    return False


def __generate_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()


def __verify_if_add_comment(validation, content_code):
    found_by_regex = __validate_regex_list(validation['regex'], content_code)

    if 'inverted' in validation and validation['inverted']:
        return not found_by_regex

    return found_by_regex
