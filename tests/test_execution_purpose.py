from src.review import __validations_by_type


def test_when_execution_purpose_is_missing_validation_with_purpose_is_not_skipped():
    validations = [
        {
            "type": "MERGE_TITLE",
            "executionPurpose": ["merge_request_review", "source_code_review"],
            "regex": ["^feature"],
            "message": "invalid title",
        }
    ]

    result = __validations_by_type("MERGE_TITLE", validations, None)

    assert result == validations


def test_when_config_execution_purpose_does_not_match_validation_list_it_is_skipped():
    validations = [
        {
            "type": "MERGE_TITLE",
            "executionPurpose": ["merge_request_review"],
            "regex": ["^feature"],
            "message": "invalid title",
        }
    ]

    result = __validations_by_type("MERGE_TITLE", validations, "source_code_review")

    assert result == []
