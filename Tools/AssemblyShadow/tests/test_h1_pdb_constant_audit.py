import copy
import struct
import unittest

import h1_pdb_constant_audit as audit


def fixture(name='answer', signature=b'\x08\x2a\0\0\0', method_rows=1, constant_first=1, include_scope=True):
    external = b'\0' * 24 + struct.pack('<Q', 1 << 6) + struct.pack('<I', method_rows)
    valid = (1 << 52) | ((1 << 50) if include_scope else 0)
    tables = struct.pack('<IBBBBQQ', 0, 2, 0, 0, 1, valid, 0)
    tables += struct.pack('<I', 1) * (2 if include_scope else 1)
    if include_scope:
        tables += (struct.pack('<I', 1) if method_rows >= 65536 else struct.pack('<H', 1))
        tables += struct.pack('<HHHII', 0, 1, constant_first, 0, 3)
    tables += struct.pack('<HH', 1, 1)
    string_heap = b'\0' + name.encode() + b'\0'
    blob_heap = b'\0' + bytes([len(signature)]) + signature
    items = [('#Pdb', external), ('#~', tables), ('#Strings', string_heap), ('#Blob', blob_heap)]
    header = b'BSJB' + struct.pack('<HHII', 1, 1, 0, 4) + b'v\0\0\0' + struct.pack('<HH', 0, len(items))
    header_size = len(header) + sum(8 + ((len(n) + 1 + 3) & ~3) for n, _ in items)
    offset = header_size
    body = b''
    for name, value in items:
        header += struct.pack('<II', offset, len(value)) + name.encode() + b'\0' * (((len(name) + 1 + 3) & ~3) - len(name))
        body += value
        offset += len(value)
    return header + body


class PortablePdbConstantAuditTests(unittest.TestCase):
    def test_real_format_minimal_inventory(self):
        value=audit.parse(fixture());self.assertEqual(1,value['constantCount']);self.assertEqual('answer',value['constants'][0]['name'])
    def test_exact_bytes_equal(self):
        value=audit.parse(fixture());self.assertTrue(audit.compare(value,copy.deepcopy(value)))
    def test_changed_name_detected(self):
        self.assertFalse(audit.compare(audit.parse(fixture()),audit.parse(fixture(name='other'))))
    def test_changed_value_detected(self):
        self.assertFalse(audit.compare(audit.parse(fixture()),audit.parse(fixture(signature=b'\x08\x2b\0\0\0'))))
    def test_changed_scope_detected(self):
        a=audit.parse(fixture());b=copy.deepcopy(a);b['constants'][0]['length']=4;self.assertFalse(audit.compare(a,b))
    def test_duplicate_constant_not_set_equal(self):
        a=audit.parse(fixture());b=copy.deepcopy(a);b['constants']*=2;self.assertFalse(audit.compare(a,b))
    def test_large_external_method_count_uses_four_byte_index(self):
        self.assertEqual(1,audit.parse(fixture(method_rows=65536))['constants'][0]['methodRid'])
    def test_method_index_boundary(self):
        self.assertEqual(1,audit.parse(fixture(method_rows=65535))['constantCount'])
    def test_unscoped_constant_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(fixture(include_scope=False))
    def test_invalid_constant_list_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(fixture(constant_first=0))
    def test_missing_method_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(fixture(method_rows=0))
    def test_truncated_root_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(b'BSJB')
    def test_truncated_stream_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(fixture()[:-1])
    def test_wrong_magic_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(b'NOPE'+fixture()[4:])
    def test_empty_signature_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(fixture(signature=b''))
    def test_compressed_integer_forms(self):
        self.assertEqual((127,1),audit.compressed(b'\x7f',0));self.assertEqual((128,2),audit.compressed(b'\x80\x80',0));self.assertEqual((16384,4),audit.compressed(b'\xc0\0\x40\0',0))
    def test_compressed_truncation(self):
        for data in (b'',b'\x80',b'\xc0\0',b'\xff\0\0\0'):
            with self.subTest(data=data),self.assertRaises(audit.PdbAuditError):audit.compressed(data,0)
    def test_inventory_never_opens_human_gate(self):
        value=audit.parse(fixture());self.assertFalse(value['humanGatePassed']);self.assertFalse(value['runtimeAcceptance']);self.assertFalse(value['mayEnterR02'])
    def test_enum_signature_bytes_preserved(self):
        signature=b'\x08\x01\0\0\0\x05';self.assertEqual(signature.hex(),audit.parse(fixture(signature=signature))['constants'][0]['signatureHex'])
    def test_scope_list_gap_rejected(self):
        with self.assertRaises(audit.PdbAuditError):audit.parse(fixture(constant_first=2))


if __name__=='__main__':unittest.main()
