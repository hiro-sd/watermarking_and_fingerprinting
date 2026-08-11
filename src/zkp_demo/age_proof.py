"""Toy age-condition proof for learning purposes.

IMPORTANT: this is not a cryptographic zero-knowledge proof. A trusted issuer
reads the birth date and creates an HMAC attestation for the age condition. The
verifier sees no birth date or exact age, but the construction has neither a
real range-proof protocol nor the security guarantees of a ZKP system.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass, replace
from datetime import date


class IneligibleError(ValueError):
    """Raised when the credential holder does not satisfy the age condition."""


@dataclass(frozen=True)
class AgeCredential:
    """Private credential held by the prover; it must not be shared."""

    subject_id: str
    birth_date: date
    credential_nonce: str
    issuer_signature: str


@dataclass(frozen=True)
class AgeProof:
    """Condition-only attestation that can be sent to a verifier."""

    subject_id: str
    minimum_age: int
    reference_date: date
    credential_commitment: str
    proof_nonce: str
    issuer_attestation: str

    def to_public_dict(self) -> dict[str, str | int]:
        """Return only fields intended for the verifier."""

        values = asdict(self)
        values["reference_date"] = self.reference_date.isoformat()
        return values


def _require_key(issuer_key: bytes) -> None:
    if len(issuer_key) < 16:
        raise ValueError("issuer_key must contain at least 16 bytes")


def _credential_message(
    subject_id: str, birth_date: date, credential_nonce: str
) -> bytes:
    return f"{subject_id}|{birth_date.isoformat()}|{credential_nonce}".encode()


def _credential_commitment(credential: AgeCredential) -> str:
    message = _credential_message(
        credential.subject_id,
        credential.birth_date,
        credential.credential_nonce,
    )
    return hashlib.sha256(message).hexdigest()


def _proof_message(proof: AgeProof) -> bytes:
    return (
        f"{proof.subject_id}|{proof.minimum_age}|{proof.reference_date.isoformat()}|"
        f"{proof.credential_commitment}|{proof.proof_nonce}"
    ).encode()


def _age_on(birth_date: date, reference_date: date) -> int:
    if birth_date > reference_date:
        raise ValueError("birth_date cannot be later than reference_date")
    birthday_has_passed = (reference_date.month, reference_date.day) >= (
        birth_date.month,
        birth_date.day,
    )
    return reference_date.year - birth_date.year - (not birthday_has_passed)


def issue_credential(
    subject_id: str,
    birth_date: date,
    issuer_key: bytes,
    *,
    credential_nonce: str | None = None,
) -> AgeCredential:
    """Issue a private age credential after an assumed identity check."""

    _require_key(issuer_key)
    if not subject_id:
        raise ValueError("subject_id must not be empty")
    nonce = credential_nonce or secrets.token_hex(16)
    signature = hmac.new(
        issuer_key,
        _credential_message(subject_id, birth_date, nonce),
        hashlib.sha256,
    ).hexdigest()
    return AgeCredential(subject_id, birth_date, nonce, signature)


def create_age_proof(
    credential: AgeCredential,
    minimum_age: int,
    reference_date: date,
    issuer_key: bytes,
    *,
    proof_nonce: str | None = None,
) -> AgeProof:
    """Create an issuer attestation without putting the birth date in the proof."""

    _require_key(issuer_key)
    if minimum_age < 0:
        raise ValueError("minimum_age must be non-negative")

    expected_signature = hmac.new(
        issuer_key,
        _credential_message(
            credential.subject_id,
            credential.birth_date,
            credential.credential_nonce,
        ),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(credential.issuer_signature, expected_signature):
        raise ValueError("credential signature is invalid")
    if _age_on(credential.birth_date, reference_date) < minimum_age:
        raise IneligibleError(f"age condition (age >= {minimum_age}) is not satisfied")

    unsigned_proof = AgeProof(
        subject_id=credential.subject_id,
        minimum_age=minimum_age,
        reference_date=reference_date,
        credential_commitment=_credential_commitment(credential),
        proof_nonce=proof_nonce or secrets.token_hex(16),
        issuer_attestation="",
    )
    attestation = hmac.new(
        issuer_key, _proof_message(unsigned_proof), hashlib.sha256
    ).hexdigest()
    return replace(unsigned_proof, issuer_attestation=attestation)


def verify_age_proof(
    proof: AgeProof,
    issuer_key: bytes,
    *,
    expected_minimum_age: int | None = None,
    expected_reference_date: date | None = None,
) -> bool:
    """Verify integrity and optionally enforce the verifier's requested condition."""

    _require_key(issuer_key)
    if expected_minimum_age is not None and proof.minimum_age != expected_minimum_age:
        return False
    if expected_reference_date is not None and proof.reference_date != expected_reference_date:
        return False
    expected = hmac.new(issuer_key, _proof_message(proof), hashlib.sha256).hexdigest()
    return hmac.compare_digest(proof.issuer_attestation, expected)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a toy age-condition proof (not a real cryptographic ZKP)."
    )
    parser.add_argument("--birth-date", type=date.fromisoformat, required=True)
    parser.add_argument("--minimum-age", type=int, default=20)
    parser.add_argument("--reference-date", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    # Fixed only to keep this command reproducible. Production secrets must never
    # be hard-coded, and this whole protocol must not be used in production.
    issuer_key = b"educational-demo-key-do-not-use"
    credential = issue_credential("demo-user", args.birth_date, issuer_key)
    try:
        proof = create_age_proof(
            credential, args.minimum_age, args.reference_date, issuer_key
        )
    except IneligibleError as error:
        print(json.dumps({"verified": False, "reason": str(error)}, ensure_ascii=False))
        return

    output = {
        "warning": "This is not a real cryptographic ZKP.",
        "proof": proof.to_public_dict(),
        "verified": verify_age_proof(
            proof,
            issuer_key,
            expected_minimum_age=args.minimum_age,
            expected_reference_date=args.reference_date,
        ),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
