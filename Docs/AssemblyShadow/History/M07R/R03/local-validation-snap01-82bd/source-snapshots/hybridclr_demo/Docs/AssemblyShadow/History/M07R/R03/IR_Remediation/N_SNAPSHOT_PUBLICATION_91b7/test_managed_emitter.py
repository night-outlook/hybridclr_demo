#!/usr/bin/env python3
"""Compile unchanged C# emitter/PInvoke declarations and actual native writer.

.NET host marshalling is real; Unity, IL2CPP conversion, terminal guards, the
native guard producer, metadata and GC lifetime are NOT exercised by this test.
All Report values are explicitly synthetic, never Player acceptance evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

PINS = {
    'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp':
        '2f13925190a1576738457d8d43f3646a4c7c095f',
    'Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs':
        '598feeec3231707091699d99fbf4428d50b52024',
}
PRODUCER_SHA = '3d68d22ef23e09b677c06e44f44acac5042b819987719c6cc2937f830f05785a'


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def section(source, marker):
    """Balanced source extraction; never transform C# into C++."""
    require(source.count(marker) == 1, 'Nonunique source marker: ' + marker)
    start = source.index(marker)
    i = source.index('{', start)
    depth, mode, escaped = 0, None, False
    while i < len(source):
        ch, pair = source[i], source[i:i+2]
        if mode == 'line':
            if ch == '\n': mode = None
        elif mode == 'block':
            if pair == '*/': mode = None; i += 1
        elif mode in ('"', "'"):
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == mode: mode = None
        elif pair == '//': mode = 'line'; i += 1
        elif pair == '/*': mode = 'block'; i += 1
        elif ch in ('"', "'"): mode = ch
        elif ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: return source[start:i+1]
        i += 1
    raise ValueError('Unbalanced source: ' + marker)


HARNESS = r'''
private static void Check(bool condition, string message)
{ if (!condition) throw new Exception("Host assertion: " + message); }
private const string Guard = "{\"available\":true,\"activeGuard\":1,\"baselineGuard\":0,\"caughtOldGuard\":1,\"stateCode\":9,\"extra\":\"synthetic guard seed, NOT actual game evidence\"}";
public static int Main(string[] args)
{
    Check(args.Length == 4, "library/mode/output/producer argv");
    IntPtr lib = NativeLibrary.Load(args[0]);
    NativeLibrary.SetDllImportResolver(typeof(Bridge).Assembly,
        (name, assembly, searchPath) => name == "__Internal" ? lib : IntPtr.Zero);
    string mode = args[1], path = args[2];
    var r = new Report {
        processId = Environment.ProcessId, result = "Passed", runId = "synthetic-host-run",
        caseId = "synthetic-" + mode, requestSha256 = new string('a',64),
        stimulus = mode.Contains("baseline") ? "baseline-owner" : "type-resolution",
        unityVersion = "2022.3.62f2", platform = "OSXPlayer",
        initialState = 6, poisonedState = 9, finalState = 9,
        nativeStimulusReturn = 1, preActiveReflection = 42, preActiveDelegate = 42,
        preCanaryCount = 1, finalCanaryCount = 1, preShadowField = 2, finalShadowField = 2,
        nativePhase = 910, terminalReportingProbeMask = 15, reserveGcProbeMask = 31,
        shadowFieldReadable = true, prePositive = true,
        activeReflectionAttempted = true, activeDelegateAttempted = true,
        aotReflectionAttempted = true, activeReflectionException = "ManagedExceptionCaught",
        activeDelegateException = "ManagedExceptionCaught", aotReflectionException = "ManagedExceptionCaught",
        firstRecovery = "{\"stateCode\":9,\"terminalFailureCode\":13}",
        finalRecovery = "{\"stateCode\":9,\"terminalFailureCode\":13}",
        finalDiagnostics = "{\"stateCode\":9}", finalExecutionDiagnostics = "{\"classes\":[]}",
        recoveryStable = true, fixedDiagnosticsReadable = true
    };
    if (mode == "occupied") {
        File.WriteAllText(path, "preserved");
        Check(R03_IR_ReportOpen(path) == -1, "occupied output rejected");
        Check(File.ReadAllText(path) == "preserved", "occupied bytes unchanged");
        Console.WriteLine("ExpectedRejectionVerified"); return 0;
    }
    Check(!File.Exists(path) && R03_IR_ReportOpen(path) == 1, "fresh output opened");
    bool expected = true;
    if (mode == "baseline" || mode == "duplicate-baseline") {
        Check(R03_IR_ReportText(8, Guard) == 1, "seed native-owned slot8 once");
        r.nativeGuardJson = Guard; // expected-value comparison only; emitter skips slot8
    }
    if (mode == "duplicate-baseline") {
        Check(R03_IR_ReportText(8, Guard) == -1, "duplicate remains forbidden"); expected = false;
    }
    if (mode == "missing-baseline") expected = false;
    if (mode == "duplicate-int") {
        Check(R03_IR_ReportInt(0, 6) == 1, "preseed integer"); expected = false;
    }
    if (mode == "off") {
        r.stimulus = "off"; r.initialState = r.poisonedState = r.finalState = 0;
        r.finalCanaryCount = 2; r.terminalReportingProbeMask = r.reserveGcProbeMask = 0;
    }
    if (mode == "failed-semantic") { r.result = "Failed"; r.failurePhase = 170; }
    if (mode == "unicode") r.error = "quotes\" backslash\\ newline\n 中文 é 🧪";
    if (mode == "exact-utf8" || mode == "oversize-utf8") {
        r.finalExecutionDiagnostics = new string('\u00e9', 131072 + (mode == "oversize-utf8" ? 1 : 0));
        Check(Encoding.UTF8.GetByteCount(r.finalExecutionDiagnostics) ==
              (mode == "exact-utf8" ? 262144 : 262146), "UTF8 byte boundary");
        expected = mode == "exact-utf8";
    }
    if (mode == "actual-producer") {
        r.finalExecutionDiagnostics = File.ReadAllText(args[3], Encoding.UTF8);
        Check(Encoding.UTF8.GetByteCount(r.finalExecutionDiagnostics) == 331078, "actual synthetic producer bytes");
        expected = false;
    }
    bool emitted = EmitNativeReport(r);
    Check(emitted == expected, "exact managed emitter result");
    if (expected) {
        using var observed = JsonDocument.Parse(File.ReadAllBytes(path));
        var root = observed.RootElement;
        Check(root.GetProperty("reportTransport").GetString() == "NativePreopenedSnapshotV1", "transport version");
        // Reflection here runs in the healthy host only, outside tested emitter.
        // Every field declared by actual Report must round-trip exactly.
        var expectedJson = JsonSerializer.SerializeToElement(r, new JsonSerializerOptions { IncludeFields = true });
        int count = 0;
        foreach (var property in expectedJson.EnumerateObject()) {
            Check(root.TryGetProperty(property.Name, out var value), "missing: " + property.Name);
            Check(value.ValueKind == property.Value.ValueKind &&
                  value.ToString() == property.Value.ToString(), "mismatch: " + property.Name);
            ++count;
        }
        Check(root.EnumerateObject().Count() == count + 1, "no additional or missing native fields");
        if (mode == "repeat-seal") Check(R03_IR_ReportSeal() == -1, "repeat seal rejected");
    } else {
        Check(new FileInfo(path).Length == 0, "incomplete evidence never serialized as complete");
        Check(R03_IR_ReportSeal() == -1, "failed transport cannot recover");
    }
    Console.WriteLine("HostRoundTripVerified");
    // No unload before process exit: the failure-path stream may still exist.
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--producer-json', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = args.repository.resolve(strict=True)
    out = args.output
    require(out.is_absolute() and out == out.resolve(strict=False), 'Canonical absolute output')
    require(out.parent.is_dir() and not out.exists() and not out.is_symlink(), 'Fresh output required')
    require(repo != out and repo not in out.parents and out not in repo.parents, 'Output outside repository')
    producer = args.producer_json.read_bytes()
    require(len(producer) == 331078 and sha(producer) == PRODUCER_SHA, 'Source-bound synthetic producer bytes')
    sources = []
    contents = []
    for rel, expected in PINS.items():
        data = (repo / rel).read_bytes()
        require(blob(data) == expected, 'Source mismatch: ' + rel)
        sources.append({'path': rel, 'gitBlob': expected, 'sha256': sha(data)})
        contents.append(data.decode('utf-8'))
    cpp, cs = contents
    start = cpp.index('namespace r03_ir_snapshot {')
    end = cpp.index('extern "C" IL2CPP_EXPORT void R03_IR_Exit')
    native = '#include <atomic>\n#include <cstdint>\n#include <cstdio>\n#include <cstdlib>\n#include <cstring>\n#include <cerrno>\n#include <fcntl.h>\n#include <unistd.h>\n#define IL2CPP_EXPORT\n' + cpp[start:end]
    imports = []
    for name in ('Open', 'Int', 'Text', 'Seal'):
        marker = 'private static extern int R03_IR_Report' + name + '('
        require(cs.count(marker) == 1, 'Exact PInvoke declaration: ' + name)
        pos = cs.index(marker)
        begin = cs.rfind('[DllImport(', 0, pos)
        imports.append(cs[begin:cs.index(';', pos)+1])
    report = section(cs, 'public sealed class Report')
    emitter = section(cs, 'private static bool EmitNativeReport')
    require(emitter.count('R03_IR_ReportInt(') == 25 and emitter.count('R03_IR_ReportText(') == 16, 'Complete emitter slots')
    managed = ('using System;\nusing System.IO;\nusing System.Linq;\nusing System.Text;\n'
               'using System.Text.Json;\nusing System.Runtime.InteropServices;\n'
               'public static class Bridge {\n' + report + '\n' + '\n'.join(imports) + '\n' + emitter + '\n' + HARNESS + '\n}\n')
    out.mkdir()
    project = out / 'project'; project.mkdir()
    (project / 'Program.cs').write_text(managed)
    (out / 'writer.cpp').write_text(native)
    (project / 'Bridge.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup></Project>\n')
    (project / 'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>\n')
    records, cases = [], []
    success = False
    def command(argv, tag, timeout=120):
        run = subprocess.run(argv, cwd=project, capture_output=True, timeout=timeout)
        (out / (tag + '.stdout')).write_bytes(run.stdout)
        (out / (tag + '.stderr')).write_bytes(run.stderr)
        records.append({'tag': tag, 'argv': argv, 'cwd': str(project), 'exit': run.returncode,
                        'stdoutSha256': sha(run.stdout), 'stderrSha256': sha(run.stderr)})
        require(run.returncode == 0, tag + ': ' + run.stderr.decode(errors='replace')[-2000:] + run.stdout.decode(errors='replace')[-2000:])
        return run
    try:
        cc = shutil.which('clang++') or shutil.which('g++'); dotnet = shutil.which('dotnet')
        require(cc and dotnet, 'C++17 compiler and .NET8 SDK required')
        command([dotnet, '--info'], 'dotnet-info')
        command([cc, '--version'], 'compiler-info')
        lib = out / ('libwriter.dylib' if sys.platform == 'darwin' else 'libwriter.so')
        flag = '-dynamiclib' if sys.platform == 'darwin' else '-shared'
        command([cc, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic', '-fPIC', flag,
                 str(out / 'writer.cpp'), '-o', str(lib)], 'native-compile')
        command([dotnet, 'build', str(project / 'Bridge.csproj'), '-c', 'Release', '--nologo',
                 '-p:UseSharedCompilation=false', '--disable-build-servers'], 'managed-compile')
        dll = project / 'bin/Release/net8.0/Bridge.dll'
        expected = {'type': None, 'baseline': None, 'off': None, 'unicode': None,
                    'failed-semantic': None, 'exact-utf8': None, 'oversize-utf8': ('text',15,9),
                    'actual-producer': ('text',15,9), 'duplicate-baseline': ('text',8,7),
                    'missing-baseline': ('missing-text',8,12), 'duplicate-int': ('int',0,7),
                    'repeat-seal': ('seal',-1,2), 'occupied': ('open',-1,4)}
        for mode, failure in expected.items():
            path = out / (mode + '.json')
            run = command([dotnet, str(dll), str(lib), mode, str(path), str(args.producer_json.resolve(strict=True))], mode, 30)
            text = run.stderr.decode('utf-8')
            lines = [line for line in text.splitlines() if line.startswith('[R03SnapshotFailure]')]
            if failure is None:
                require(not lines, 'Unexpected diagnostic: ' + mode)
            else:
                require(len(lines) == 1, 'Immutable first error only: ' + mode)
                require('operation=' + failure[0] + ' ' in lines[0] and
                        'field=' + str(failure[1]) + ' ' in lines[0] and
                        'reason=' + str(failure[2]) + ' ' in lines[0], 'Exact diagnostic: ' + mode)
                if failure[2] == 9:
                    require('length=262145 limit=262144' in lines[0], 'Unchanged byte limit')
            cases.append({'mode': mode, 'result': 'ExpectedHostOutcomeVerified',
                          'writerAccepted': failure is None or mode == 'repeat-seal',
                          'expectedFailure': failure, 'rawBytes': path.stat().st_size,
                          'rawSha256': sha(path.read_bytes())})
        success = True
    finally:
        unchanged = all(blob((repo / row['path']).read_bytes()) == row['gitBlob'] for row in sources)
        result = {'kind': 'ActualCSharpNativeSnapshotHostRoundTrip', 'result': 'PassedWithinHostScope' if success and unchanged else 'FailedOrIncomplete',
                  'sources': sources, 'cases': cases, 'records': records, 'sourceUnchanged': unchanged,
                  'actualCSharpEmitterAndPInvokeExecuted': True, 'nativeWriterReimplemented': False,
                  'reportValuesSynthetic': True, 'baselineSlot8ProducerSynthetic': True,
                  'IL2CPPMarshallingTested': False, 'UnityLaunched': False,
                  'runtimeAcceptance': False, 'NRootCauseProven': False,
                  'textLimit': 262144, 'producerInputSha256': sha(producer)}
        (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
        entries = [{'path': str(p.relative_to(out)), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
                   for p in sorted(out.rglob('*')) if p.is_file()]
        (out / 'MANIFEST.json').write_text(json.dumps({'files': entries}, indent=2) + '\n')
    require(success and unchanged, 'Complete test and preservation required')
    print(json.dumps({'result': result['result'], 'cases': len(cases), 'commands': len(records), 'runtimeAcceptance': False}))


if __name__ == '__main__':
    main()
