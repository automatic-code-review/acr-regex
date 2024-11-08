import hashlib
import os
import re


def review(config):
    validations = config['data']
    path_source = config['path_source']
    merge = config['merge']
    diffs = merge['changes']

    comments = []

    if 'title' in merge:
        comments.extend(
            __review_merge_title(
                merge_title=merge['title'],
                validations=__validations_by_type("MERGE_TITLE", validations),
            )
        )

    validations_file_content = __validations_by_type("MERGE_FILE_CONTENT", validations)

    for change in diffs:
        if change['deleted_file']:
            continue

        path_code = os.path.join(path_source, change['new_path'])

        comments.extend(
            __review_file_content_by_file(
                path_code,
                validations_file_content,
                path_source,
                diffs,
                merge
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
            comments.append(__create_comment(__generate_md5(comment), comment, None))

    return comments


def __validate_diff_type(validation, path_final, diffs):
    if 'diffType' not in validation:
        return True

    diff = None

    for diff_it in diffs:
        if diff_it['new_path'] == path_final:
            diff = diff_it
            break

    if diff is None:
        return False

    if diff['new_file'] and 'CREATE' not in validation['diffType']:
        return False

    if not diff['new_file'] and 'UPDATE' not in validation['diffType']:
        return False

    return True


def __review_file_content_by_file(path_content, validations, path_code_origin, diffs, merge):
    comments = []
    content_code = None
    project_name = merge['project_name']

    for validation in validations:
        if not __validate_regex_list(validation['regexFile'], path_content):
            continue

        if 'projects' in validation and project_name not in validation['projects']:
            continue

        path_to_comment = str(path_content).replace(path_code_origin + '/', '')

        if not __validate_diff_type(validation, path_to_comment, diffs):
            continue

        if content_code is None:
            try:
                with open(path_content, 'r') as arquivo:
                    content_code = arquivo.read()
            except UnicodeDecodeError as _:
                content_code = ""
                print(f"Read error {path_content}")

        if __verify_if_add_comment(validation, content_code):
            comment = validation['message'].replace("${FILE_PATH}", path_to_comment)
            comments.append(__create_comment(__generate_md5(comment + path_to_comment), comment, path_to_comment))

    return comments


def __create_comment(comment_id, comment, path):
    return {
        "id": comment_id,
        "comment": comment,
        "position": {
            "language": None,
            "path": path,
            "startInLine": 1,
            "endInLine": 1,
            "snipset": False
        }
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
