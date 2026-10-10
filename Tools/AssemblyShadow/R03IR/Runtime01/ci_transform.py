#!/usr/bin/env python3
"""Pinned composite recipe correction; outputs are separately compiled and hashed."""
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
one(old,old.rstrip()+'\n')  # Preserve separation from enclosing triple quote.
one('#include "vm/Runtime.h"\n#include "vm/Object.h"',
    '#include "vm/Runtime.h"\n#include "vm/Assembly.h"\n#include "vm/Object.h"')
old='        const auto* engine = MetadataCache::GetAotAssemblyByNamePhysical("UnityEngine.CoreModule");'
one(old,'#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\n'+old+'\n#else\n        const auto* engine = Assembly::Load("UnityEngine.CoreModule");\n#endif')
compile(source,str(p),'exec')
p.write_text(source)
subprocess.run([sys.executable,'-B',str(p)],check=True)
