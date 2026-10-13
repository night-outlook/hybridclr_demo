"""Executable design reference, not connected to the Unity Player.

R03BoundedDiagnosticsV2 stores exact UTF-8 bytes, never a summary/hash substitute.
The caller must authenticate the expected descriptor from the sealed run record.
Hashes provide integrity/binding, NOT authenticity against a malicious producer.
"""
from __future__ import annotations
import hashlib
import io
import json
import struct
from typing import BinaryIO

MAGIC = b'R03DIA2\0'
END = b'R03END2\0'
CHUNK = 65536
TEXT_LIMIT = 262144              # Unchanged physical text-slot bound.
TOTAL = 16 * TEXT_LIMIT           # No larger aggregate than original 16 slots.
RESERVE = TEXT_LIMIT              # Reserved for envelope/inline/descriptor bytes.
MAX_STREAM = TOTAL - RESERVE
HEADER = struct.Struct('>8s32s32s')
SECTION = struct.Struct('>BBIH32s') # slot, null/text, exact bytes, chunk count, hash
FRAME = struct.Struct('>IH32s')    # index, length-minus-one, context-bound hash
FIELDS = ('finalDiagnostics', 'finalExecutionDiagnostics')
IDENTITY_KEYS = {'runId', 'caseId', 'requestSha256', 'buildSha256', 'processId',
                 'demoCommit', 'hybridclrCommit', 'packageCommit', 'nativeCommit'}

class ContractError(ValueError):
    pass

def need(ok: bool, message: str) -> None:
    if not ok:
        raise ContractError(message)

def sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def hex_value(value: object, length: int) -> bool:
    return (isinstance(value, str) and len(value) == length and
            all(c in '0123456789abcdef' for c in value))

def binding(identity: dict) -> bytes:
    need(type(identity) is dict and set(identity) == IDENTITY_KEYS, 'identity schema')
    for k in ('runId', 'caseId'):
        v = identity[k]
        need(isinstance(v, str) and 0 < len(v) <= 128 and v.isascii()
             and all(c.isalnum() or c in '-_.' for c in v), 'identity name')
    need(type(identity['processId']) is int and 0 < identity['processId'] < 2**31,
         'identity PID')
    for k in ('requestSha256', 'buildSha256'):
        need(hex_value(identity[k], 64), 'identity digest')
    for k in ('demoCommit', 'hybridclrCommit', 'packageCommit', 'nativeCommit'):
        need(hex_value(identity[k], 40), 'identity commit')
    return sha(b'R03-IDENTITY-V2\0' + canonical(identity))

def inline_bytes(inline: dict) -> bytes:
    need(type(inline) is dict and not any(k in inline for k in FIELDS), 'inline schema')
    data = canonical(inline)
    # Account for descriptor/envelope space inside the unchanged aggregate.
    need(len(data) <= RESERVE - 4096, 'inline resource bound')
    return data

def frame_hash(context: bytes, slot: int, index: int, data: bytes) -> bytes:
    return sha(b'R03-FRAME-V2\0' + context + struct.pack('>BII', slot, index, len(data)) + data)

def encode(identity: dict, inline: dict, fields: dict[str, str | None]) -> tuple[bytes, dict]:
    """Host reference: native integration must stream, not materialize this buffer."""
    need(type(fields) is dict and set(fields) == set(FIELDS), 'exact diagnostic slots')
    context, inline_hash = binding(identity), sha(inline_bytes(inline))
    out = bytearray(HEADER.pack(MAGIC, context, inline_hash))
    for slot, name in enumerate(FIELDS, 14):
        value = fields[name]
        need(value is None or isinstance(value, str), 'text or null only')
        data = b'' if value is None else value.encode('utf-8', errors='strict')
        count = (len(data) + CHUNK - 1) // CHUNK
        projected = len(out) + SECTION.size + len(data) + count * FRAME.size + 40
        need(projected <= MAX_STREAM and count <= 64, 'aggregate resource bound')
        out.extend(SECTION.pack(slot, int(value is not None), len(data), count, sha(data)))
        for index in range(count):
            part = data[index * CHUNK:(index + 1) * CHUNK]
            out.extend(FRAME.pack(index, len(part) - 1, frame_hash(context, slot, index, part)))
            out.extend(part)
    out.extend(END + sha(bytes(out)))
    need(len(out) <= MAX_STREAM, 'aggregate resource bound')
    encoded = bytes(out)
    descriptor = {'kind': 'R03BoundedDiagnosticsV2', 'bytes': len(encoded),
                  'sha256': sha(encoded).hex(), 'binding': context.hex(),
                  'inlineSha256': inline_hash.hex()}
    return encoded, descriptor

class Reader:
    def __init__(self, stream: BinaryIO):
        self.stream, self.total = stream, 0
        self.hash = hashlib.sha256()
        self.prefix = hashlib.sha256()

    def take(self, count: int, prefix: bool = True) -> bytes:
        need(0 <= count <= CHUNK and self.total + count <= MAX_STREAM, 'read bound')
        data = self.stream.read(count)
        need(type(data) is bytes and len(data) == count, 'truncated or short read')
        self.total += len(data)
        self.hash.update(data)
        if prefix:
            self.prefix.update(data)
        return data

def decode(stream: BinaryIO, expected: dict, identity: dict, inline: dict) -> dict[str, str | None]:
    """Fail closed; no fields are returned before complete stream authentication.

    BinaryIO is an already safely opened bounded file. Path lookup, raw manifest
    authenticity and source/PID joins are external responsibilities, not bypassed.
    """
    need(type(expected) is dict and set(expected) ==
         {'kind', 'bytes', 'sha256', 'binding', 'inlineSha256'}, 'descriptor schema')
    need(expected['kind'] == 'R03BoundedDiagnosticsV2', 'version')
    need(type(expected['bytes']) is int and 192 <= expected['bytes'] <= MAX_STREAM,
         'descriptor length')
    for k in ('sha256', 'binding', 'inlineSha256'):
        need(hex_value(expected[k], 64), 'descriptor hash')
    context, inline_hash = binding(identity), sha(inline_bytes(inline))
    need(expected['binding'] == context.hex() and
         expected['inlineSha256'] == inline_hash.hex(), 'descriptor binding')
    r = Reader(stream)
    magic, got_context, got_inline = HEADER.unpack(r.take(HEADER.size))
    need((magic, got_context, got_inline) == (MAGIC, context, inline_hash), 'header binding')
    result = {}
    for slot, name in enumerate(FIELDS, 14):
        actual_slot, kind, total, count, whole_hash = SECTION.unpack(r.take(SECTION.size))
        need(actual_slot == slot and kind in (0, 1), 'slot ownership/order')
        need(total <= MAX_STREAM and count == (total + CHUNK - 1) // CHUNK and count <= 64,
             'declared resource bound')
        need(kind == 1 or (total == 0 and count == 0), 'null field content')
        need(r.total + total + count * FRAME.size + 40 <= MAX_STREAM, 'aggregate resource bound')
        data = bytearray()
        for index in range(count):
            actual_index, minus_one, checksum = FRAME.unpack(r.take(FRAME.size))
            length = minus_one + 1
            need(actual_index == index and length == min(CHUNK, total - len(data)),
                 'chunk order/length')
            part = r.take(length)
            need(frame_hash(context, slot, index, part) == checksum, 'chunk hash')
            data.extend(part)
        need(len(data) == total and sha(data) == whole_hash, 'complete field hash')
        try:
            text = bytes(data).decode('utf-8', errors='strict')
        except UnicodeDecodeError as e:
            raise ContractError('UTF-8') from e
        result[name] = text if kind else None
    expected_prefix = r.prefix.digest()
    need(r.take(8, False) == END and r.take(32, False) == expected_prefix, 'commit footer')
    need(stream.read(1) == b'', 'trailing data')
    need(r.total == expected['bytes'] and r.hash.hexdigest() == expected['sha256'],
         'whole-stream receipt')
    return result

def strict_json(text: str) -> object:
    """No duplicate-key or NaN normalization in diagnostics before semantic checks."""
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    def constant(value):
        raise ContractError('nonfinite JSON number: ' + value)
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError) as e:
        raise ContractError('strict diagnostics JSON: ' + str(e)) from e

def hydrate(raw_v2: dict, encoded: bytes, expected: dict, identity: dict) -> dict:
    """Return a tagged semantic view; NEVER rewrite a V2 record into fake V1 raw.

    This does not call or relax the original semantic verifier. Integration is
    gated until its transport dispatch accepts this explicit V2 tagged view.
    """
    need(type(raw_v2) is dict and raw_v2.get('diagnosticArtifact') == expected,
         'raw descriptor binding')
    need(raw_v2.get('reportTransport') == 'NativeBoundedSnapshotV2', 'raw transport')
    inline = {k: v for k, v in raw_v2.items() if k != 'diagnosticArtifact'}
    need(not any(k in inline for k in FIELDS), 'inline diagnostic collision')
    decoded = decode(io.BytesIO(encoded), expected, identity, inline)
    for value in decoded.values():
        if value is not None:
            strict_json(value)
    return {**inline, **decoded}
