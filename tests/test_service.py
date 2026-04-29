from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models import TokenMapping
from app.service import MAX_GENERATION_ATTEMPTS, TOKEN_LENGTH, TokenizationService


def _mock_query(db: MagicMock, first_side_effect):
    query = db.query.return_value
    filtered = query.filter.return_value
    filtered.first.side_effect = first_side_effect
    return filtered


def test_tokenize_rejects_empty_body():
    service = TokenizationService(MagicMock())

    with pytest.raises(HTTPException) as exc_info:
        service.tokenize([])

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Request body must be a JSON array of account numbers"


def test_detokenize_rejects_blank_token():
    service = TokenizationService(MagicMock())

    with pytest.raises(HTTPException) as exc_info:
        service.detokenize(["   "])

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Token must not be blank"


def test_tokenize_strips_whitespace_before_lookup():
    db = MagicMock()
    _mock_query(db, [TokenMapping(token="A" * TOKEN_LENGTH, account_number="4111-1111")])
    service = TokenizationService(db)

    result = service.tokenize(["  4111-1111  "])

    assert result == ["A" * TOKEN_LENGTH]
    lookup = db.query.return_value.filter.call_args.args[0]
    assert str(lookup) == str(TokenMapping.account_number == "4111-1111")


def test_detokenize_strips_whitespace_before_lookup():
    token = "B" * TOKEN_LENGTH
    db = MagicMock()
    _mock_query(db, [TokenMapping(token=token, account_number="4111-1111")])
    service = TokenizationService(db)

    result = service.detokenize([f"  {token}  "])

    assert result == ["4111-1111"]
    lookup = db.query.return_value.filter.call_args.args[0]
    assert str(lookup) == str(TokenMapping.token == token)


def test_create_new_mapping_retries_when_generated_token_already_exists(monkeypatch):
    db = MagicMock()
    _mock_query(
        db,
        [
            TokenMapping(token="A" * TOKEN_LENGTH, account_number="existing"),
            None,
        ],
    )
    mapping = TokenMapping(token="B" * TOKEN_LENGTH, account_number="4111-1111")
    db.refresh.side_effect = lambda instance: None
    monkeypatch.setattr(
        "app.service.generate_token",
        MagicMock(side_effect=["A" * TOKEN_LENGTH, "B" * TOKEN_LENGTH]),
    )
    db.add.side_effect = lambda instance: setattr(instance, "id", 1)

    result = TokenizationService(db)._create_new_mapping("4111-1111")

    assert result.token == mapping.token
    assert result.account_number == mapping.account_number
    assert db.add.call_count == 1
    assert db.commit.call_count == 1
    assert db.refresh.call_count == 1


def test_create_new_mapping_returns_existing_account_after_integrity_error(monkeypatch):
    db = MagicMock()
    _mock_query(
        db,
        [
            None,
            TokenMapping(token="C" * TOKEN_LENGTH, account_number="4111-1111"),
        ],
    )
    monkeypatch.setattr("app.service.generate_token", MagicMock(return_value="C" * TOKEN_LENGTH))
    db.add.side_effect = lambda instance: None
    db.commit.side_effect = IntegrityError("insert", {}, Exception("duplicate"))

    result = TokenizationService(db)._create_new_mapping("4111-1111")

    assert result.token == "C" * TOKEN_LENGTH
    assert result.account_number == "4111-1111"
    assert db.rollback.call_count == 1


def test_create_new_mapping_raises_after_exhausting_attempts(monkeypatch):
    db = MagicMock()
    _mock_query(
        db,
        [TokenMapping(token="D" * TOKEN_LENGTH, account_number="occupied")] * MAX_GENERATION_ATTEMPTS,
    )
    monkeypatch.setattr("app.service.generate_token", MagicMock(return_value="D" * TOKEN_LENGTH))

    with pytest.raises(HTTPException) as exc_info:
        TokenizationService(db)._create_new_mapping("4111-1111")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to generate unique token"
    assert db.add.call_count == 0
