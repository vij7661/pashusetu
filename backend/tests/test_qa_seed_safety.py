from types import SimpleNamespace

import pytest

from app.db import qa_seed


class IdentityDB:
    def __init__(self, actual_database):
        self.actual_database = actual_database

    def scalar(self, _query):
        return self.actual_database


@pytest.mark.parametrize(
    ("app_env", "isolated", "otp_mode", "url_database", "actual_database"),
    [
        ("production", True, True, "pashusetu_qa", "pashusetu_qa"),
        ("pilot", True, True, "pashusetu_qa", "pashusetu_qa"),
        ("qa", False, True, "pashusetu_qa", "pashusetu_qa"),
        ("qa", True, False, "pashusetu_qa", "pashusetu_qa"),
        ("qa", True, True, "pashusetu", "pashusetu"),
        ("qa", True, True, "pashusetu_qa", "pashusetu"),
    ],
)
def test_qa_mutations_refuse_unsafe_or_ambiguous_targets(
    monkeypatch, app_env, isolated, otp_mode, url_database, actual_database
):
    monkeypatch.setattr(
        qa_seed,
        "get_settings",
        lambda: SimpleNamespace(
            app_env=app_env,
            database_isolated_for_qa=isolated,
            otp_test_mode=otp_mode,
            database_url=(
                f"postgresql+psycopg://qa:qa@db:5432/{url_database}"
            ),
        ),
    )
    with pytest.raises(RuntimeError, match="Refusing QA mutation"):
        qa_seed.assert_safe_qa_database(IdentityDB(actual_database))


def test_qa_mutations_accept_only_exact_isolated_qa_identity(monkeypatch):
    monkeypatch.setattr(
        qa_seed,
        "get_settings",
        lambda: SimpleNamespace(
            app_env="qa",
            database_isolated_for_qa=True,
            otp_test_mode=True,
            database_url="postgresql+psycopg://qa:qa@db_qa:5432/pashusetu_qa",
        ),
    )
    qa_seed.assert_safe_qa_database(IdentityDB("pashusetu_qa"))
