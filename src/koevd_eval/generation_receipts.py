"""Bounded operator-reviewed generation receipts, separate from result uploads.

Receipt bytes and audit hashes are consistency checks. A trusted local operator
must independently review the execution evidence before accepting a receipt;
neither this validator nor a Hugging Face identity proves model inference.
"""
from copy import deepcopy

from .eligibility import OperatorEvidence, declaration_identity
from .results import canonical_hash
from .storage import StorageError, encode

FORMAT = 'koevd-operator-generation-receipt-v1'
FIELDS = {'format', 'artifact_sha256', 'input_index_sha256', 'declaration_sha256',
          'execution_scope', 'generation_level', 'evidence_files', 'review_statement'}
REQUIRED_KINDS = {'source_manifest', 'execution_log', 'generation_output', 'runtime_record'}


def validate_receipt(receipt, document, index):
    if not isinstance(receipt, dict) or set(receipt) != FIELDS or receipt.get('format') != FORMAT:
        raise StorageError('invalid_generation_receipt', 'Unsupported operator generation receipt')
    if len(encode(receipt)) > 32768:
        raise StorageError('receipt_too_large', 'Generation receipt exceeds 32 KiB', 413)
    statement = receipt['review_statement']
    if not isinstance(statement, str) or not statement.strip() or len(statement.encode('utf-8')) > 4096:
        raise StorageError('invalid_generation_receipt', 'A bounded independent review statement is required')
    files = receipt['evidence_files']
    if not isinstance(files, list) or not 4 <= len(files) <= 64:
        raise StorageError('invalid_generation_receipt', 'Bounded execution evidence references are required')
    kinds = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {'kind', 'sha256', 'bytes'}:
            raise StorageError('invalid_generation_receipt', 'Unsupported evidence reference')
        if not isinstance(entry['kind'], str) or entry['kind'] not in REQUIRED_KINDS:
            raise StorageError('invalid_generation_receipt', 'Unsupported evidence kind')
        digest = entry['sha256']
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise StorageError('invalid_generation_receipt', 'Invalid execution evidence digest')
        if type(entry['bytes']) is not int or entry['bytes'] <= 0:
            raise StorageError('invalid_generation_receipt', 'Execution evidence byte count must be positive')
        kinds.add(entry['kind'])
    if kinds != REQUIRED_KINDS or receipt['generation_level'] != 'operator_reproduced':
        raise StorageError('invalid_generation_receipt', 'Independent generation review needs all evidence kinds')
    try:
        evidence = OperatorEvidence(
            receipt['artifact_sha256'], receipt['input_index_sha256'], receipt['declaration_sha256'],
            canonical_hash(receipt), receipt['generation_level'], receipt['execution_scope'])
    except ValueError as exc:
        raise StorageError('invalid_generation_receipt', str(exc)) from exc
    if (evidence.artifact_sha256 != document['content_sha256'] or
            evidence.input_index_sha256 != index['content_sha256'] or
            evidence.declaration_sha256 != declaration_identity(document)):
        raise StorageError('receipt_binding_mismatch', 'Receipt does not bind this exact result, inputs and declaration', 409)
    return deepcopy(receipt), evidence


def active_evidence(events, revision, document, index):
    """Read immutable accepted/revoked history; never use uploaded evidence flags."""
    active = None
    for event in events:
        details = event['details']
        if details.get('revision') != revision:
            continue
        if event['action'] == 'accept_generation_receipt':
            _, active = validate_receipt(details['receipt'], document, index)
        elif event['action'] == 'revoke_generation_receipt' and active is not None:
            if details['receipt_sha256'] == active.receipt_sha256:
                active = None
    return active
