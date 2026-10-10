#!/usr/bin/env python3
"""Pinned composite source recipe; outputs are independently compiled and hashed."""
from pathlib import Path
import subprocess
import sys

p=Path(__file__).with_name('apply_exact_patch.py')
source=p.read_text()
def one(old,new):
    global source
    if source.count(old)!=1:raise RuntimeError('Nonunique recipe correction: '+old[:90])
    source=source.replace(old,new,1)
old="original_player = HERE / 'PlayerProject/R03Player.cs' "
one(old,old.rstrip()+'\n')
one("NATIVE = 'bdfce18f0925041695408bcbcff10d91b28de396'", "NATIVE = '5df6a01bfee2fe63b28fa45d8720571858c0f589'")
one('#include "vm/Runtime.h"\n#include "vm/Object.h"',
    '#include "vm/Runtime.h"\n#include "vm/Assembly.h"\n#include "gc/GCHandle.h"\n#include "vm/Object.h"')
old='        const auto* engine = MetadataCache::GetAotAssemblyByNamePhysical("UnityEngine.CoreModule");'
one(old,'#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\n'+old+'\n#else\n        const auto* engine = Assembly::Load("UnityEngine.CoreModule");\n#endif')
compile(source,str(p),'exec')
p.write_text(source)
subprocess.run([sys.executable,'-B',str(p)],check=True)

root=p.resolve().parents[4]
player=root/'Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs'
s=player.read_text()
def edit(old,new):
    global s
    if s.count(old)!=1:raise RuntimeError('Nonunique Player context: '+old[:90])
    s=s.replace(old,new,1)
edit('                EncodeReport(report);','''                EncodeReport(report);
                LogCaughtException(new InvalidOperationException("R03IR native exception transport positive control"));''')
edit('                report.error = "ManagedExceptionCapturedSeeNativeJournal";','''                report.error = "ManagedExceptionCapturedSeeNativeJournal";
                LogCaughtException(error);''')
edit('        private static int s_phase;','''        [DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
        private static extern void R03_IR_LogException(IntPtr handle);
        private static void LogCaughtException(Exception error)
        {
            GCHandle root = default(GCHandle);
            try
            {
                // Normal, not pinned: retain the actual exception for a native
                // nonvirtual diagnostic. IL2CPP's GCHandle icalls use this token.
                root = GCHandle.Alloc(error, GCHandleType.Normal);
                R03_IR_LogException(GCHandle.ToIntPtr(root));
            }
            catch (Exception)
            {
                R03_IR_Journal(s_phase, "exception-object-diagnostic-unavailable");
            }
            finally { if (root.IsAllocated) root.Free(); }
        }
        private static int s_phase;''')
player.write_text(s)
probe=root/'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp'
s=probe.read_text()
s += r'''

extern "C" IL2CPP_EXPORT void R03_IR_LogException(intptr_t handle)
{
    // This token was created by GCHandle.Alloc in the current isolated Player
    // and remains rooted until this call returns. Never dereference arbitrary
    // pointers supplied by JSON. No managed Message/ToString/logger invocation.
    try
    {
        const auto token = static_cast<uint32_t>(handle);
        Il2CppObject* object = token ? il2cpp::gc::GCHandle::GetTarget(token) : nullptr;
        const Il2CppClass* klass = object ? object->klass : nullptr;
        std::fprintf(stderr, "[R03IRManagedException] type=%s.%s message=",
            klass && klass->namespaze ? klass->namespaze : "Unavailable",
            klass && klass->name ? klass->name : "Unavailable");
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
        il2cpp::vm::assembly_shadow_reporting::WriteMessage(reinterpret_cast<const Il2CppException*>(object));
#else
        std::fputs("UnavailableFeatureOff", stderr);
#endif
        std::fputc('\n',stderr);std::fflush(stderr);
    }
    catch (...) { std::fputs("[R03IRManagedException] NativeDiagnosticUnavailable\n",stderr);std::fflush(stderr); }
}
'''
probe.write_text(s)
subprocess.run(['git','-C',str(root),'diff','--check'],check=True)
