import copy
import hashlib
import io
import struct
import unittest
from diagnostic_stream import (ContractError, CHUNK, TEXT_LIMIT, TOTAL, MAX_STREAM,
                               HEADER, SECTION, FRAME, encode, decode, hydrate,
                               canonical, binding, strict_json)

IDENTITY = dict(runId='snap02-test', caseId='baseline', requestSha256='a'*64,
                buildSha256='b'*64, processId=12345, demoCommit='1'*40,
                hybridclrCommit='2'*40, packageCommit='3'*40, nativeCommit='4'*40)
INLINE = {'reportTransport': 'NativeBoundedSnapshotV2', 'schemaVersion': 2,
          'result': 'Failed', 'acceptance': False, 'finalShadowField': 2}
FIELDS = {'finalDiagnostics': '{"name":"same bytes","classes":[]}',
          'finalExecutionDiagnostics': '{"counter":23}'}

class CodecTests(unittest.TestCase):
    def setUp(self):
        self.identity, self.inline, self.fields = copy.deepcopy(IDENTITY), dict(INLINE), dict(FIELDS)
        self.data, self.descriptor = encode(self.identity,self.inline,self.fields)
    def read(self, data=None, descriptor=None):
        return decode(io.BytesIO(self.data if data is None else data),
                      self.descriptor if descriptor is None else descriptor,self.identity,self.inline)
    def mutated(self, data):
        # Deliberately rebind OUTER hash: inner structure/integrity must still reject.
        d=dict(self.descriptor,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        return self.read(bytes(data),d)
    def test_exact_bytes_roundtrip(self):
        self.assertEqual(self.read(),self.fields)
    def test_actual_limit_not_increased(self):
        self.assertEqual(TEXT_LIMIT,262144);self.assertEqual(TOTAL,4194304)
        self.assertLessEqual(CHUNK,TEXT_LIMIT)
    def test_large_final_and_execution_are_lossless(self):
        fields={k:canonical({'classes':[{'id':i,'name':'X'*80} for i in range(8000)]}).decode() for k in FIELDS}
        data,d=encode(self.identity,self.inline,fields)
        self.assertTrue(all(len(v.encode())>TEXT_LIMIT for v in fields.values()))
        self.assertLess(len(data)+262144,TOTAL)
        self.assertEqual(decode(io.BytesIO(data),d,self.identity,self.inline),fields)
    def test_utf8_split_across_chunk(self):
        fields={k:'x'*(CHUNK-1)+'🐟'+'中'*30000 for k in FIELDS}
        data,d=encode(self.identity,self.inline,fields)
        self.assertEqual(decode(io.BytesIO(data),d,self.identity,self.inline),fields)
    def test_null_and_empty_distinct(self):
        fields=dict(finalDiagnostics=None,finalExecutionDiagnostics='')
        data,d=encode(self.identity,self.inline,fields)
        self.assertEqual(decode(io.BytesIO(data),d,self.identity,self.inline),fields)
    def test_embedded_nul_is_not_truncated(self):
        fields=dict(finalDiagnostics='a\0b',finalExecutionDiagnostics='\\u0000')
        data,d=encode(self.identity,self.inline,fields)
        self.assertEqual(decode(io.BytesIO(data),d,self.identity,self.inline),fields)
    def test_exact_chunk_size(self):
        fields={k:'a'*CHUNK for k in FIELDS};data,d=encode(self.identity,self.inline,fields)
        self.assertEqual(decode(io.BytesIO(data),d,self.identity,self.inline),fields)
    def test_aggregate_limit_fails_not_truncates(self):
        fields={k:'x'*(TOTAL//2) for k in FIELDS}
        with self.assertRaisesRegex(ContractError,'aggregate'): encode(self.identity,self.inline,fields)
    def test_inline_resource_not_free(self):
        with self.assertRaisesRegex(ContractError,'inline resource'):
            encode(self.identity,{'text':'x'*262144},self.fields)
    def test_missing_slot(self):
        with self.assertRaises(ContractError): encode(self.identity,self.inline,{'finalDiagnostics':'{}'})
    def test_extra_slot(self):
        with self.assertRaises(ContractError): encode(self.identity,self.inline,{**self.fields,'extra':'{}'})
    def test_boolean_pid_rejected(self):
        with self.assertRaises(ContractError): binding({**self.identity,'processId':True})
    def test_unknown_identity_field(self):
        with self.assertRaises(ContractError): binding({**self.identity,'ignored':'x'})
    def test_malformed_commit(self):
        with self.assertRaises(ContractError): binding({**self.identity,'demoCommit':'1'*39})
    def test_wrong_run_replay(self):
        self.identity['runId']='other'
        with self.assertRaisesRegex(ContractError,'binding'):self.read()
    def test_wrong_inline_replay(self):
        self.inline['finalShadowField']=3
        with self.assertRaisesRegex(ContractError,'binding'):self.read()
    def test_descriptor_unknown_version(self):
        with self.assertRaises(ContractError):self.read(descriptor={**self.descriptor,'kind':'V3'})
    def test_descriptor_bool_length(self):
        with self.assertRaises(ContractError):self.read(descriptor={**self.descriptor,'bytes':True})
    def test_tampered_payload_even_outer_hash_changed(self):
        b=bytearray(self.data);b[HEADER.size+SECTION.size+FRAME.size]^=1
        with self.assertRaisesRegex(ContractError,'chunk hash'):self.mutated(b)
    def test_wrong_sequence(self):
        b=bytearray(self.data);b[HEADER.size+SECTION.size:HEADER.size+SECTION.size+4]=struct.pack('>I',1)
        with self.assertRaisesRegex(ContractError,'order'):self.mutated(b)
    def test_swapped_slot_ownership(self):
        b=bytearray(self.data);b[HEADER.size]=15
        with self.assertRaisesRegex(ContractError,'slot ownership'):self.mutated(b)
    def test_enormous_declared_length(self):
        b=bytearray(self.data);b[HEADER.size+2:HEADER.size+6]=b'\xff'*4
        with self.assertRaisesRegex(ContractError,'resource'):self.mutated(b)
    def test_missing_or_partial_footer(self):
        for n in [1,8,32,40]:
            with self.subTest(n=n),self.assertRaises(ContractError):self.mutated(self.data[:-n])
    def test_trailing_bytes(self):
        with self.assertRaisesRegex(ContractError,'trailing'):self.mutated(self.data+b'x')
    def test_wrong_commit_footer(self):
        b=bytearray(self.data);b[-1]^=1
        with self.assertRaisesRegex(ContractError,'footer'):self.mutated(b)
    def test_wrong_full_field_digest(self):
        b=bytearray(self.data);b[HEADER.size+8]^=1
        with self.assertRaisesRegex(ContractError,'field hash'):self.mutated(b)
    def test_chunk_hash_binds_context(self):
        b=bytearray(self.data);b[10]^=1
        with self.assertRaisesRegex(ContractError,'header'):self.mutated(b)
    def test_noncanonical_chunk_length(self):
        b=bytearray(self.data);b[HEADER.size+SECTION.size+4:HEADER.size+SECTION.size+6]=b'\x00\x00'
        with self.assertRaisesRegex(ContractError,'length'):self.mutated(b)
    def test_null_cannot_have_data(self):
        b=bytearray(self.data);b[HEADER.size+1]=0
        with self.assertRaisesRegex(ContractError,'null'):self.mutated(b)
    def test_hydration_never_converts_failed_to_pass(self):
        raw={**self.inline,'diagnosticArtifact':self.descriptor}
        result=hydrate(raw,self.data,self.descriptor,self.identity)
        self.assertEqual(result['result'],'Failed');self.assertIs(result['acceptance'],False)
        self.assertEqual(result['reportTransport'],'NativeBoundedSnapshotV2')
        self.assertNotIn('finalDiagnostics',raw)
    def test_hydration_rejects_forged_descriptor(self):
        with self.assertRaises(ContractError):hydrate({**self.inline,'diagnosticArtifact':{}},self.data,self.descriptor,self.identity)
    def test_hydration_diagnostic_collision(self):
        raw={**self.inline,'finalDiagnostics':'{}','diagnosticArtifact':self.descriptor}
        with self.assertRaises(ContractError):hydrate(raw,self.data,self.descriptor,self.identity)
    def test_duplicate_json_is_not_normalized(self):
        with self.assertRaises(ContractError): strict_json('{"x":1,"x":2}')
    def test_nonfinite_json_is_not_normalized(self):
        with self.assertRaises(ContractError): strict_json('{"x":NaN}')
    def test_json_structure_preserved(self):
        self.assertEqual(strict_json('{"c":[{"x":1},null,true]}'),{'c':[{'x':1},None,True]})
    def test_short_read_is_failure(self):
        class Short(io.BytesIO):
            def read(self,n=-1):return super().read(max(0,n-1))
        with self.assertRaises(ContractError):decode(Short(self.data),self.descriptor,self.identity,self.inline)

if __name__=='__main__':unittest.main()
