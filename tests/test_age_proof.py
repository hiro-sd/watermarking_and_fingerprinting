from dataclasses import replace
from datetime import date

import pytest

from zkp_demo.age_proof import (
    IneligibleError,
    create_age_proof,
    issue_credential,
    verify_age_proof,
)


ISSUER_KEY = b"test-issuer-key-with-enough-bytes"


def test_eligible_holder_can_create_verifiable_proof() -> None:
    credential = issue_credential(
        "alice",
        date(2000, 8, 11),
        ISSUER_KEY,
        credential_nonce="credential-nonce",
    )
    proof = create_age_proof(
        credential,
        20,
        date(2026, 8, 11),
        ISSUER_KEY,
        proof_nonce="proof-nonce",
    )

    assert verify_age_proof(
        proof,
        ISSUER_KEY,
        expected_minimum_age=20,
        expected_reference_date=date(2026, 8, 11),
    )
    public_proof = proof.to_public_dict()
    public_text = str(public_proof)
    assert "2000-08-11" not in public_text
    assert "birth_date" not in public_proof
    assert "exact_age" not in public_proof


def test_holder_below_minimum_age_cannot_create_proof() -> None:
    credential = issue_credential("bob", date(2010, 1, 1), ISSUER_KEY)

    with pytest.raises(IneligibleError):
        create_age_proof(credential, 20, date(2026, 8, 11), ISSUER_KEY)


def test_condition_is_checked_on_birthday_boundary() -> None:
    credential = issue_credential("carol", date(2006, 8, 12), ISSUER_KEY)

    with pytest.raises(IneligibleError):
        create_age_proof(credential, 20, date(2026, 8, 11), ISSUER_KEY)

    proof = create_age_proof(credential, 20, date(2026, 8, 12), ISSUER_KEY)
    assert verify_age_proof(proof, ISSUER_KEY)


def test_tampered_proof_is_rejected() -> None:
    credential = issue_credential("dave", date(1990, 1, 1), ISSUER_KEY)
    proof = create_age_proof(credential, 20, date(2026, 8, 11), ISSUER_KEY)

    assert not verify_age_proof(replace(proof, minimum_age=18), ISSUER_KEY)
    assert not verify_age_proof(proof, b"another-issuer-key-long-enough")
