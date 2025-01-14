"""Test the summary_of_datasets_by_user helper function."""


def test_summary_of_datasets_by_user(tmp_app_with_data_client):  # NOQA

    from dserver.utils import summary_of_datasets_by_user

    summary = summary_of_datasets_by_user("grumpy")
    exected_output = {
        "number_of_datasets": 3,
        "creator_usernames": ["queen"],
        "base_uris": ["s3://mr-men", "s3://snow-white"],
        "datasets_per_creator": {"queen": 3},
        "datasets_per_base_uri": {"s3://mr-men": 1, "s3://snow-white": 2},
        "tags": ["evil", "fruit", "good"],
        "datasets_per_tag": {"good": 1, "evil": 2, "fruit": 3}
    }
    assert summary == exected_output
