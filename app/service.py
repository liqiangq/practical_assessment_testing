import re
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import TokenMapping
from app.utils import generate_token

TOKEN_LENGTH = 32
MAX_GENERATION_ATTEMPTS = 10
TOKEN_PATTERN = re.compile(r"^[0-9A-Za-z]{32}$")


class TokenizationService:
    def __init__(self, db: Session):
        self.db = db

    def tokenize(self, account_numbers: list[str]) -> list[str]:
        values = self._require_body(
            account_numbers,
            "Request body must be a JSON array of account numbers",
        )
        return [self._tokenize_one(value) for value in values]

    def detokenize(self, tokens: list[str]) -> list[str]:
        values = self._require_body(
            tokens,
            "Request body must be a JSON array of tokens",
        )
        return [self._detokenize_one(value) for value in values]

    def _tokenize_one(self, account_number: str) -> str:
        normalized = self._normalize(account_number, "Account number must not be blank")

        existing = (
            self.db.query(TokenMapping)
            .filter(TokenMapping.account_number == normalized)
            .first()
        )
        if existing:
            return existing.token

        return self._create_new_mapping(normalized).token

    def _detokenize_one(self, token: str) -> str:
        normalized = self._normalize(token, "Token must not be blank")

        if not TOKEN_PATTERN.fullmatch(normalized):
            raise HTTPException(
                status_code=400,
                detail="Invalid token format. Expected 32 characters in [0-9A-Za-z].",
            )

        mapping = (
            self.db.query(TokenMapping)
            .filter(TokenMapping.token == normalized)
            .first()
        )
        if not mapping:
            raise HTTPException(status_code=404, detail="Token not found")

        return mapping.account_number

    def _create_new_mapping(self, account_number: str) -> TokenMapping:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            token = generate_token(TOKEN_LENGTH)

            existing_token = (
                self.db.query(TokenMapping)
                .filter(TokenMapping.token == token)
                .first()
            )
            if existing_token:
                continue

            try:
                mapping = TokenMapping(token=token, account_number=account_number)
                self.db.add(mapping)
                self.db.commit()
                self.db.refresh(mapping)
                return mapping
            except IntegrityError:
                self.db.rollback()
                existing_account = (
                    self.db.query(TokenMapping)
                    .filter(TokenMapping.account_number == account_number)
                    .first()
                )
                if existing_account:
                    return existing_account

        raise HTTPException(status_code=500, detail="Failed to generate unique token")

    def _require_body(self, values: list[str] | None, message: str) -> list[str]:
        if values is None or len(values) == 0:
            raise HTTPException(status_code=400, detail=message)
        return values

    def _normalize(self, value: str | None, message: str) -> str:
        if value is None:
            raise HTTPException(status_code=400, detail=message)

        normalized = value.strip()
        if not normalized:
            raise HTTPException(status_code=400, detail=message)

        return normalized
