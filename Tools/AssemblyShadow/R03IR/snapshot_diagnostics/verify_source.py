#!/usr/bin/env python3
"""Check the bounded diagnostic-only source delta against immutable N bytes."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

cpp = (ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp').read_text()
cs = (ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs').read_text()
before = cpp[:cpp.index('namespace r03_ir_snapshot {')].replace('#include <cerrno>\n', '')
after = cpp[cpp.index('extern "C" IL2CPP_EXPORT void R03_IR_Exit'):]
require(digest(before) == '950e53edf5d23f2c6f01c019a3f5d8a5fd0938654aeab86e0bf0ca5b48478afb', 'Original non-writer producer prefix changed')
require(digest(after) == '3fa2c5894f79600f6354951c527238a669c05c99e0d5b2c1d67dca82a0eae068', 'Original GC/field/guard/exit functions changed')
require(digest(cs) == 'e06face7827175c759de30b6c2de1424308a46e45ef1e1525f26b5084f47d94f', 'Original managed emitter or semantic predicates changed')
for text in ('constexpr size_t TextLimit = 262144;', 'constexpr int IntCount = 25;',
             'constexpr int FirstBool = 14;', 'constexpr int TextCount = 16;',
             'O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW', 'NativePreopenedSnapshotV1'):
    require(text in cpp, 'Original transport contract missing: '+text)
for name, call, expected in (('IntNames', 'Int', 25), ('TextNames', 'Text', 16)):
    match = re.search(r'constexpr const char\* '+name+r'\[\] = \{([^}]+)\}', cpp)
    require(match is not None, 'Field schema missing: '+name)
    names = re.findall(r'"(\w+)"', match[1])
    mapping = re.findall(r'R03_IR_Report'+call+r'\((\d+), r\.(\w+)', cs)
    require(len(names)==expected and mapping==[(str(i),n) for i,n in enumerate(names)], 'Exact original field mapping changed')
print(json.dumps({'result':'DiagnosticDeltaVerified','originalNPrefixAndSuffixUnchanged':True,
                  'entireManagedSourceUnchanged':True,'schemaAndBoundsUnchanged':True,
                  'NRootCauseProven':False,'runtimeAcceptance':False}))
