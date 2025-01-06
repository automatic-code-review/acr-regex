import os
import re

import automatic_code_review_commons as commons


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

    if 'commits' in merge:
        comments.extend(
            __review_merge_commit(
                merge_commits=merge['commits'],
                validations=__validations_by_type("COMMIT_TITLE", validations),
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
        found, _ = __validate_regex_list(validation['regex'], content=merge_title)

        if not found:
            description_comment = validation['message']
            comment = __review_merge_create_comment(description_comment)
            if 'processorArgs' in validation:
                comment['processorArgs'] = validation['processorArgs']
            comments.append(comment)

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
        found, _ = __validate_regex_list(validation['regexFile'], path_content)

        if not found:
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

        add_comment, regex = __verify_if_add_comment(validation, content_code)

        if add_comment:
            if regex is None:
                groups_line = [(1, 1)]
            else:
                groups_line = __find_occurrences_with_lines(content_code, regex)

            for group in groups_line:
                end_line = group[1]
                start_line = group[0]

                comment_description = validation['message'].replace("${FILE_PATH}", path_to_comment)
                comment_description = comment_description.replace("${LINE_START}", str(start_line))
                comment_description = comment_description.replace("${LINE_END}", str(end_line))
                comment_unique_id = f"{comment_description} - {path_to_comment} - {start_line} - {end_line}"
                comment = commons.comment_create(
                    comment_id=commons.comment_generate_id(comment_unique_id),
                    comment_path=path_to_comment,
                    comment_description=comment_description,
                    comment_snipset=False,
                    comment_end_line=end_line,
                    comment_start_line=start_line,
                    comment_language=None,
                )
                if 'processorArgs' in validation:
                    comment['processorArgs'] = validation['processorArgs']
                comments.append(comment)

    return comments


def __validate_regex(regex, content):
    return re.search(regex, content)


def __validate_regex_list(regex_list, content):
    for regex in regex_list:
        if __validate_regex(regex=regex, content=content):
            return True, regex

    return False, None


def __verify_if_add_comment(validation, content_code):
    found_by_regex, regex = __validate_regex_list(validation['regex'], content_code)

    if 'inverted' in validation and validation['inverted']:
        return not found_by_regex, regex

    return found_by_regex, regex


def __find_occurrences_with_lines(content, pattern):
    matches = list(re.finditer(pattern, content))

    lines = content.splitlines(keepends=True)

    results = []
    current_line = 1
    current_pos = 0

    for match in matches:
        start_pos, end_pos = match.span()

        while current_pos < start_pos:
            current_pos += len(lines[current_line - 1])
            current_line += 1

        line_start = current_line

        while current_pos < end_pos:
            current_pos += len(lines[current_line - 1])
            current_line += 1

        line_end = current_line - 1

        if line_end < line_start:
            line_end = line_start

        results.append((line_start, line_end))

    return results

def __review_merge_commit(merge_commits, validations):
    comments = []
    group_description_comment = []

    for commit in merge_commits:
        title = commit['title']
        
        for validation in validations:
            is_group_message = validation['groupMessage']
            found, _ = __validate_regex_list(validation['regex'], content=title)

            if not found:                
                description_comment = validation['message']
                comment_description = comment_description.replace("${COMMIT_TITLE}", str(title))
                if is_group_message:
                    group_description_comment.append(comment_description)
                    continue
                comment = __review_merge_create_comment(description_comment)
                if 'processorArgs' in validation:
                    comment['processorArgs'] = validation['processorArgs']
                comments.append(comment)

    if group_description_comment:
        description_comment = '\n'.join(group_description_comment)
        comment = __review_merge_create_comment(description_comment)
        comments.append(comment)

    return comments

def __review_merge_create_comment(description_comment):
    return commons.comment_create(
                    comment_id=commons.comment_generate_id(description_comment),
                    comment_path=None,
                    comment_description=description_comment,
                    comment_snipset=False,
                    comment_end_line=None,
                    comment_start_line=None,
                    comment_language=None,
                )