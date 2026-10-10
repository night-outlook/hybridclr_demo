#!/usr/bin/env python3
"""Primary source transformation in isolated CI; never used by Local Validation.

Ref publication remains Connector-owned. Authenticate original E blobs before
transforming, then compile/tests must pass before creating any output blobs.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
P = 'Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs'
PROBE = 'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp'
NATIVE = 'bdfce18f0925041695408bcbcff10d91b28de396'
PINS = {
 P: 'adc798c6c299594d496393c6729c4c6087111b31',
 PROBE: '17744ce9418379d8471c4dd52c5d53ad1795a6b7',
 'Tools/AssemblyShadow/R03/PlayerApiCompile/UnityEnvironment.cs': '454b4d26904e17d8d790f13c1aedcf7cf1f991c9',
 'Tools/AssemblyShadow/R03IR/run_terminal_local.py': '50ef04171f8b88180b659cd7c5f4aa29f871eac3',
 'Tools/AssemblyShadow/R03IR/test_terminal_contract.py': '672dbda251405b405993bdf2b3b861963875c306',
 'Tools/AssemblyShadow/R03/native_validation.py': '68c66e26168ba32f6231d11c13841765d5d1d49a',
 'Tools/AssemblyShadow/R03/source-pins.json': '053fba3e55f1a3c219fe125affcb20f790649c86',
 'Tools/AssemblyShadow/R03/build_api.py': 'e44a06015dea76ab4b6f6c946a61e664c1022a2d',
}

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def one(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError('Nonunique transformation context: ' + old[:100])
    return s.replace(old,new,1)

HELPERS = r'''
        // These diagnostics never call Exception.ToString or Unity logging.
        // Journal records are supplementary evidence, never semantic PASS.
        private static int s_phase;
        private static int s_reportingCalls;
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_Journal(int phase, string note);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_SaveReport(string path, string json);
        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern int R03_IR_ExerciseReporting();

        [Preserve]
        private sealed class ReportingCanary : ILogHandler
        {
            public void LogException(Exception error, UnityEngine.Object context) { ++s_reportingCalls; }
            public void LogFormat(LogType type, UnityEngine.Object context, string format, params object[] args)
            { ++s_reportingCalls; }
        }
        private static void Phase(int value, string note)
        {
            s_phase = value;
            R03_IR_Journal(value, note);
        }
        // Parse only the fixed scalar fields emitted by the native probe. Its
        // entire JSON is independently parsed and checked by the host verifier.
        // No reflective JsonUtility entry or DTO constructor after poison.
        private static string GuardScalar(string json, string name)
        {
            string key = "\"" + name + "\":";
            int at = json.IndexOf(key, StringComparison.Ordinal);
            Require(at >= 0 && json.IndexOf(key, at + key.Length, StringComparison.Ordinal) < 0,
                "Unique native guard key " + name);
            int start = at + key.Length;
            int end = start;
            while (end < json.Length && json[end] != ',' && json[end] != '}') ++end;
            Require(end > start && end < json.Length, "Bounded guard scalar " + name);
            return json.Substring(start, end - start);
        }
        private static void JsonString(StringBuilder text, string value)
        {
            if (value == null) { text.Append("null"); return; }
            const string hex = "0123456789abcdef";
            text.Append('"');
            for (int i = 0; i < value.Length; ++i)
            {
                int ch = value[i];
                if (ch == '"' || ch == '\\') { text.Append('\\'); text.Append((char)ch); }
                else if (ch < 32 || ch > 126)
                {
                    text.Append("\\u");
                    text.Append(hex[(ch >> 12) & 15]); text.Append(hex[(ch >> 8) & 15]);
                    text.Append(hex[(ch >> 4) & 15]); text.Append(hex[ch & 15]);
                }
                else text.Append((char)ch);
            }
            text.Append('"');
        }
        private static void JsonValue(StringBuilder text, string value) { JsonString(text, value); }
        private static void JsonValue(StringBuilder text, bool value) { text.Append(value ? "true" : "false"); }
        private static void JsonValue(StringBuilder text, int value)
        {
            // Do not invoke culture/format-provider lazy initialization after failure.
            long n = value;
            if (n < 0) { text.Append('-'); n = -n; }
            char[] digits = new char[10]; int count = 0;
            do { digits[count++] = (char)('0' + n % 10); n /= 10; } while (n != 0);
            while (count != 0) text.Append(digits[--count]);
        }
'''

PROBE_EXTRA = r'''

// IR-LOCAL-RUNTIME-01 supplementary native witness/persistence. These functions
// exist only in the isolated test Player overlay, never an old S/E installation.
#include "vm/Runtime.h"
#include "vm/Object.h"
#include <cstdio>
#include <cerrno>
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#include "vm/AssemblyShadowTerminalReporting.h"
#endif
#if defined(__APPLE__) || defined(__linux__)
#include <fcntl.h>
#include <unistd.h>
#endif

extern "C" IL2CPP_EXPORT void R03_IR_Journal(int32_t phase, const char* note)
{
    try
    {
        using namespace il2cpp::vm;
        AssemblyShadowState state;
        AssemblyShadow::GetState(state);
        std::string recovery;
        const auto code = AssemblyShadow::GetRecoveryInfoJson(recovery);
        std::fprintf(stderr, "[R03IRPhase] phase=%d state=%d recoveryCode=%d note=%s recovery=%s\n",
            phase, static_cast<int32_t>(state), static_cast<int32_t>(code),
            note ? note : "", recovery.c_str());
        std::fflush(stderr);
    }
    catch (...) { std::fputs("[R03IRPhase] NativeDiagnosticUnavailable\n", stderr); std::fflush(stderr); }
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_SaveReport(const char* path, const char* json)
{
#if defined(__APPLE__) || defined(__linux__)
    if (!path || path[0] != '/' || !json) return -1;
    const size_t length = std::strlen(json);
    if (!length || length > 1024 * 1024) return -1;
    const int fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) return -2; // Never truncate or replace prior evidence.
    size_t written = 0; int failure = 0;
    while (written < length)
    {
        const ssize_t count = ::write(fd, json + written, length - written);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) { failure = -3; break; }
        written += static_cast<size_t>(count);
    }
    if (!failure && ::fsync(fd) != 0) failure = -4;
    if (::close(fd) != 0 && !failure) failure = -5;
    if (failure) std::fprintf(stderr, "[R03IRReportWriteFailed] code=%d\n", failure);
    return failure;
#else
    (void)path; (void)json; return -6;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_ExerciseReporting()
{
    using namespace il2cpp::vm;
    try
    {
        // Resolve the real physical method even in OFF builds. A custom managed
        // handler is installed as a positive-control canary by the test source.
        const auto* engine = MetadataCache::GetAotAssemblyByNamePhysical("UnityEngine.CoreModule");
        if (!engine || !engine->image) return -1;
        const MethodInfo* report = nullptr;
        {
            il2cpp::os::FastAutoLock lock(&g_MetadataLock);
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
            AssemblyShadowTypeMetadataScope scope;
#endif
            for (uint32_t i=0; i<engine->image->typeCount; ++i)
            {
                auto h = MetadataCache::GetAssemblyTypeHandle(engine->image,i);
                auto n = MetadataCache::GetTypeNamespaceAndName(h);
                if (std::strcmp(n.first,"UnityEngine") || std::strcmp(n.second,"Debug")) continue;
                auto* owner = MetadataCache::GetTypeInfoFromHandle(h);
                for (uint32_t k=0; k<owner->method_count; ++k)
                {
                    auto raw = MetadataCache::GetMethodInfo(owner,k);
                    const auto* method = MetadataCache::GetMethodInfoFromMethodHandle(raw.handle);
                    if (!method || std::strcmp(method->name,"CallOverridenDebugHandler")) continue;
                    if (report) return -2;
                    report = method;
                }
            }
        }
        if (!report) return -3;
        void* args[] = {nullptr,nullptr};
        Il2CppException* error = nullptr;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
        const uint64_t before = assembly_shadow_reporting::HandledCounter().load(std::memory_order_relaxed);
#endif
        Il2CppObject* result = Runtime::Invoke(report,nullptr,args,&error);
        if (error || !result || result->klass != il2cpp_defaults.boolean_class) return -4;
        const bool handled = *static_cast<bool*>(Object::Unbox(result));
        int32_t code = handled ? 1 : 0;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
        const auto after = assembly_shadow_reporting::HandledCounter().load(std::memory_order_relaxed);
        if (after == before + 1) code += 16;
        else if (after != before) return -5;
#endif
        return code;
    }
    catch (...) { return -6; }
}
'''

def main():
    originals={}
    for path,blob in PINS.items():
        data=(ROOT/path).read_bytes()
        if git_blob(data)!=blob: raise RuntimeError('Wrong E input blob: '+path)
        originals[path]=data.decode()
    changed=dict(originals)
    s=originals[P]
    s=one(s,'            public bool acceptance = false;','''            public int reportingProtocol = 1;
            public int preReportingCode, postReportingCode, preReportingCalls, finalReportingCalls;
            public int failurePhase;
            public bool reportingWitness;
            public bool acceptance = false;''')
    # Remove the now-unused reflection-deserialized post-poison DTO.
    start=s.index('        [Serializable, Preserve] private sealed class NativeGuard')
    end=s.index('        [Serializable, Preserve] public sealed class Report',start)
    s=s[:start]+s[end:]
    s=one(s,'                AssemblyShadowState state;','''                Phase(1, "request-validated");
                // Warm the non-reflective serializer before any terminal state.
                EncodeReport(report);
                UnityEngine.Debug.unityLogger.logHandler = new ReportingCanary();
                UnityEngine.Debug.LogException(new InvalidOperationException("R03IR reporting positive control"));
                Require(s_reportingCalls == 1, "Managed reporting canary must execute before poison");
                report.preReportingCode = R03_IR_ExerciseReporting();
                report.preReportingCalls = s_reportingCalls;
                Require(report.preReportingCode == 1 && report.preReportingCalls == 2,
                    "Actual healthy Runtime::Invoke reporting callback must execute the custom handler");
                Phase(2, "reporting-positive-control");
                AssemblyShadowState state;''')
    s=one(s,'                    report.result = "Passed";','''                    report.postReportingCode = R03_IR_ExerciseReporting();
                    report.finalReportingCalls = s_reportingCalls;
                    report.reportingWitness = report.postReportingCode == 1 && report.finalReportingCalls == 3;
                    Require(report.reportingWitness, "OFF reporting callback must remain ordinary managed execution");
                    report.result = "Passed";''')
    points=[
      ('                Require(AssemblyShadowRuntime.ConfigureCandidates(',10,'configure'),
      ('                Require(AssemblyShadowRuntime.BeginTransaction(',11,'begin'),
      ('                Require(AssemblyShadowRuntime.ReserveMetadataBudget(',12,'reserve'),
      ('                Require(AssemblyShadowRuntime.StageAssembly(',13,'stage'),
      ('                Require(AssemblyShadowRuntime.ValidateTransaction()',14,'validate'),
      ('                Require(AssemblyShadowRuntime.CommitTransaction()',15,'commit'),
      ('                Type activeType = Type.GetType(',20,'active-type'),
      ('                object instance = Activator.CreateInstance(',21,'active-instance'),
      ('                Func<int> activeDelegate = ',22,'active-delegate'),
      ('                report.preActiveReflection = ',23,'active-pre-reflection'),
      ('                report.preActiveDelegate = ',24,'active-pre-delegate'),
      ('                if (request.stimulus == "baseline-owner")',30,'terminal-stimulus'),
      ('                report.activeReflectionAttempted = true;',40,'post-active-reflection'),
      ('                report.activeDelegateAttempted = true;',41,'post-active-delegate'),
      ('                report.aotReflectionAttempted = true;',42,'post-aot-reflection'),
      ('                report.finalShadowField = ',43,'post-field-read'),
    ]
    for anchor,phase,label in points:
        s=one(s,anchor,'                Phase(%d, "%s");\n'%(phase,label)+anchor)
    a=s.index('                    NativeGuard guard = JsonUtility.FromJson<NativeGuard>')
    b=s.index('                    report.nativeStimulusReturn = guard.caughtOldGuard;',a)+len('                    report.nativeStimulusReturn = guard.caughtOldGuard;')
    s=s[:a]+'''                    Require(GuardScalar(report.nativeGuardJson, "schemaVersion") == "1" &&
                        GuardScalar(report.nativeGuardJson, "available") == "true" &&
                        GuardScalar(report.nativeGuardJson, "activeGuard") == "1" &&
                        GuardScalar(report.nativeGuardJson, "baselineGuard") == "0" &&
                        GuardScalar(report.nativeGuardJson, "caughtOldGuard") == "1" &&
                        GuardScalar(report.nativeGuardJson, "stateCode") == "9",
                        "First terminal failure and caught managed guard exception required");
                    report.nativeStimulusReturn = 1;'''+s[b:]
    s=one(s,'                string diagnostics, execution;','''                Phase(44, "post-reporting-transport");
                report.postReportingCode = R03_IR_ExerciseReporting();
                report.finalReportingCalls = s_reportingCalls;
                report.reportingWitness = report.postReportingCode == 17 &&
                    report.preReportingCalls == 2 && report.finalReportingCalls == 2;
                Require(report.reportingWitness,
                    "Native terminal report must be handled without executing the custom managed handler");
                Phase(45, "fixed-diagnostics");
                string diagnostics, execution;''')
    s=one(s,'                report.error = error.ToString();','''                report.failurePhase = s_phase;
                // Exception formatting can itself invoke terminal-blocked managed
                // code. The phase and native first-failure journal carry detail.
                report.error = "ManagedExceptionCapturedSeeNativeJournal";
                R03_IR_Journal(s_phase, "outer-managed-catch");''')
    a=s.index('                    using (var output = new FileStream(')
    b=s.index('\n            }\n        }',a)
    s=s[:a]+'''                    Phase(90, "persist-final-report");
                    int saved = R03_IR_SaveReport(outputPath, EncodeReport(report));
                    R03_IR_Journal(91, saved == 0 ? "report-persisted" : "report-write-failed");
                    Application.Quit(saved == 0 ? 0 : 2); // Host verifier owns acceptance.
                }
                catch (Exception)
                {
                    R03_IR_Journal(99, "report-persistence-exception");
                    Application.Quit(2); // Never re-enter UnityEngine.Debug.
                }'''+s[b:]
    # Build an explicit field serializer from the exact scalar Report contract.
    a=s.index('        [Serializable, Preserve] public sealed class Report')
    b=s.index('\n        [DllImport',a)
    fields=[]
    for kind,decl in re.findall(r'public (string|int|bool) ([^;]+);',s[a:b]):
        for part in decl.split(','):
            name=part.split('=')[0].strip()
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*',name): raise RuntimeError('Unexpected report declaration')
            fields.append(name)
    assert fields and len(fields)==len(set(fields))
    encoder=['        private static string EncodeReport(Report report)','        {','            StringBuilder json = new StringBuilder(4096);',"            json.Append('{');"]
    for i,name in enumerate(fields):
        if i: encoder.append("            json.Append(',');")
        encoder += ['            JsonString(json, "'+name+'");',"            json.Append(':');",'            JsonValue(json, report.'+name+');']
    encoder += ["            json.Append('}');",'            return json.ToString();','        }']
    s=one(s,'        private static void Require(bool ok, string message)',HELPERS+'\n'+'\n'.join(encoder)+'\n\n        private static void Require(bool ok, string message)')
    s=one(s,'            if (!ok) throw new InvalidOperationException("R03IR: " + message);','''            if (!ok)
            {
                R03_IR_Journal(s_phase, message);
                throw new InvalidOperationException("R03IR: " + message);
            }''')
    assert 'error.ToString()' not in s and 'JsonUtility.ToJson' not in s and 'FromJson<NativeGuard>' not in s
    changed[P]=s
    changed[PROBE]=originals[PROBE]+PROBE_EXTRA
    path='Tools/AssemblyShadow/R03/PlayerApiCompile/UnityEnvironment.cs'
    changed[path]=one(originals[path],'''    public static class Debug
    { public static void LogException(Exception error) { throw new NotSupportedException(); } }''','''    public class Object { }
    public enum LogType { Error, Assert, Warning, Log, Exception }
    public interface ILogHandler
    {
        void LogException(Exception error, Object context);
        void LogFormat(LogType type, Object context, string format, params object[] args);
    }
    public interface ILogger { ILogHandler logHandler { get; set; } }
    public static class Debug
    {
        public static ILogger unityLogger { get { throw new NotSupportedException(); } }
        public static void LogException(Exception error) { throw new NotSupportedException(); }
    }''')
    path='Tools/AssemblyShadow/R03IR/run_terminal_local.py'
    anchor="    if request['stimulus'] == 'off':"
    s=originals[path]
    at=s.index(anchor,s.index('def verify_ir('))
    guard='''    require(exact_int(raw.get('reportingProtocol'), 1) and raw.get('reportingWitness') is True and
            exact_int(raw.get('failurePhase'), 0) and exact_int(raw.get('preReportingCode'), 1) and
            exact_int(raw.get('preReportingCalls'), 2), 'Actual healthy reporting positive control required')
    require(exact_int(raw.get('postReportingCode'), 1 if request['stimulus'] == 'off' else 17) and
            exact_int(raw.get('finalReportingCalls'), 3 if request['stimulus'] == 'off' else 2),
            'Native terminal reporting must not execute custom managed handler; OFF must remain normal')
'''
    s=s[:at]+guard+s[at:];changed[path]=s
    path='Tools/AssemblyShadow/R03IR/test_terminal_contract.py'
    s=one(originals[path],"            'acceptance': False, 'result': 'Passed', 'error': None,",'''            'acceptance': False, 'result': 'Passed', 'error': None,
            'reportingProtocol':1, 'reportingWitness':True, 'failurePhase':0,
            'preReportingCode':1, 'postReportingCode':17,
            'preReportingCalls':2, 'finalReportingCalls':2,''')
    s=one(s,'        self.raw.update(initialState=0,finalState=0,prePositive=True,','''        self.raw.update(reportingProtocol=1,reportingWitness=True,failurePhase=0,
            postReportingCode=1,finalReportingCalls=3,initialState=0,finalState=0,prePositive=True,''')
    s=one(s,"\n\nif __name__=='__main__':",'''
    def test_reporting_witness_cannot_be_missing_fabricated_or_execute_user_code(self):
        for name,value in [('reportingProtocol',None),('reportingWitness',False),
                           ('preReportingCalls',0),('preReportingCode',17),
                           ('postReportingCode',1),('finalReportingCalls',3),('failurePhase',44)]:
            with self.subTest(field=name):
                self.setUp();self.raw[name]=value
                with self.assertRaises(ContractError):self.verify()

    def test_reporting_numeric_fields_reject_boolean(self):
        for name in ('reportingProtocol','preReportingCode','postReportingCode',
                     'preReportingCalls','finalReportingCalls','failurePhase'):
            with self.subTest(field=name):
                self.setUp();self.raw[name]=True
                with self.assertRaises(ContractError):self.verify()


if __name__=='__main__':''')
    changed[path]=s
    path='Tools/AssemblyShadow/R03/native_validation.py'
    s=one(originals[path],"'GarbageCollector.cpp'))]","'GarbageCollector.cpp','Runtime.cpp'))]")
    s=one(s,"units=[copy/'vm/AssemblyShadow.cpp',","units=[copy/'vm/Runtime.cpp',copy/'vm/AssemblyShadow.cpp',")
    changed[path]=s
    path='Tools/AssemblyShadow/R03/build_api.py'
    s=one(originals[path],"        current = HERE / 'PlayerProject/R03Build.cs'",'''        current = HERE / 'PlayerProject/R03Build.cs'
        terminal_player = HERE.parent / 'R03IR/PlayerProject/R03TerminalPlayer.cs'
        original_player = HERE / 'PlayerProject/R03Player.cs' ''')
    s=one(s,'[runtime, compiler, core, log, old, current, *references, *plugins, *sources]',
          '[runtime, compiler, core, log, old, current, terminal_player, original_player, *references, *plugins, *sources]')
    s=one(s,"        result['completeHelper'] = binding(target)",'''        result['completeHelper'] = binding(target)
        player_target = compile_one('R03IRPlayer', [original_player, terminal_player], [built['HybridCLR.Runtime']])
        result['currentPlayerOfficialApi'] = binding(player_target)''')
    changed[path]=s.rstrip()+'\n'
    path='Tools/AssemblyShadow/R03/source-pins.json'
    pins=json.loads(originals[path]);pins['il2cpp_plus']=NATIVE
    changed[path]=json.dumps(pins,indent=2)+'\n'
    for path,text in changed.items():
        (ROOT/path).write_bytes(text.encode())
        print(path,git_blob(text.encode()))
    subprocess.run(['git','-C',str(ROOT),'diff','--check'],check=True)

if __name__=='__main__':main()
