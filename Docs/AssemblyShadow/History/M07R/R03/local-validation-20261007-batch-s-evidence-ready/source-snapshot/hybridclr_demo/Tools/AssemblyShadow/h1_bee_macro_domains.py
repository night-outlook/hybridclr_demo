"""Source-owned macro domains for the reviewed Unity 2022.3 Apple Bee graph.

All object actions must be linked, all PCHs must have real consumers, and every
compiler action still needs the exact requested feature/diagnostic definitions.
The exception is to *IL2CPP configuration ownership*, not to provenance: Unity's
external bdwgc/zlib C objects do not include the IL2CPP runtime configuration.
No node index, directory hash, action count, language alone, or observed macro
value selects a less strict domain. Unknown external source membership fails.
"""
from __future__ import annotations
from collections import defaultdict, deque
from pathlib import Path
import json

import h1_compiler_actions as a

POLICY = 'unity-2022.3-apple-bee-source-domains-v1'
RUNTIME = 'il2cpp-runtime'
FEATURE = 'HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW'
DIAGNOSTIC = 'HYBRIDCLR_H1_COUNT_DIAGNOSTICS'
INSTALLED = 'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp'
EXTERNAL = {
    'bdwgc': frozenset(('extra/gc.c', 'extra/krait_signal_handler.c')),
    'zlib': frozenset(name + '.c' for name in (
        'adler32', 'crc32', 'deflate', 'gzclose', 'gzlib', 'gzread', 'gzwrite',
        'infback', 'inffast', 'inflate', 'inftrees', 'trees', 'uncompr', 'zutil')),
}
MAX_NODES = 16384
MAX_PATHS = 131072


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def source_domain(unit, root):
    source = Path(unit['source'])
    a.need(source.is_relative_to(root), 'Native source is outside the selected project')
    external = root / INSTALLED / 'external'
    if source.is_relative_to(external):
        relative = source.relative_to(external).as_posix()
        library, _, name = relative.partition('/')
        a.need(library in EXTERNAL and name in EXTERNAL[library],
               'Unreviewed external compiler source: ' + relative)
        a.need(not unit['producer'] and unit['pch'] is None and unit['language'] == 'c',
               'External library must be a direct C object without a forced PCH')
        return 'external-' + library
    # C sources (including brotli and generated CodeGen.c), runtime lumps and
    # generated C++ remain in the runtime contract. Never exempt "all C".
    return RUNTIME


def _paths(node, key, root):
    values = node.get(key, [])
    a.need(type(values) is list and all(type(p) is str and p for p in values),
           'Malformed Bee ' + key)
    return [a.resolve(root, p) for p in values]


def derive(graph, root, native, config, units, response_contents, feature):
    """Return exhaustive graph/argument attribution, not compiler execution proof."""
    a.need(type(feature) is bool, 'An explicit feature mode is required')
    nodes = graph.get('Nodes')
    a.need(type(nodes) is list and 0 < len(nodes) <= MAX_NODES, 'Bounded Bee graph required')
    owners, consumers = defaultdict(list), defaultdict(list)
    inputs, outputs, count = [], [], 0
    for i, node in enumerate(nodes):
        a.need(type(node) is dict, 'Malformed Bee node')
        ins, outs = _paths(node, 'Inputs', root), _paths(node, 'Outputs', root)
        count += len(ins) + len(outs)
        a.need(count <= MAX_PATHS, 'Bee path inventory exceeds bound')
        inputs.append(ins); outputs.append(outs)
        for path in set(outs): owners[path].append(i)
        for path in set(ins): consumers[path].append(i)
    links = [(i, n) for i, n in enumerate(nodes)
             if str(n.get('Annotation', '')).startswith('Link_Mac_arm64') and n.get('Action')]
    a.need(len(links) == 1 and units, 'Expected all native actions and exactly one link')
    link_index, link = links[0]
    link_argv, used = a.expand(a.split(link['Action']), root, response_contents)
    link_outs = [p for p in outputs[link_index] if Path(p).name == 'GameAssembly.dylib']
    a.need(len(link_outs) == 1 and owners[link_outs[0]] == [link_index], 'Ambiguous native link output')
    a.need(a.resolve(root, a.option(link_argv, '-o')) == link_outs[0], 'Link -o and declared output differ')
    a.need(link.get('Env', []) == [], 'Unevidenced link environment overrides')

    # The supported Apple graph links objects directly. Reject unrecorded inputs,
    # duplicate objects and a disconnected native action rather than ignore it.
    object_units = [u for u in units if not u['producer']]
    unit_outputs = [u['output'] for u in object_units]
    declared_objects = [p for p in inputs[link_index] if Path(p).suffix == '.o']
    command_objects = [a.resolve(root, t) for t in link_argv[1:]
                       if not t.startswith('-') and Path(t).suffix == '.o']
    a.need(len(unit_outputs) == len(set(unit_outputs)), 'Duplicate object producer')
    a.need(len(declared_objects) == len(set(declared_objects)) and
           len(command_objects) == len(set(command_objects)) and
           set(declared_objects) == set(command_objects) == set(unit_outputs),
           'Native object producer / link Inputs / link argv coverage differs')
    for unit in units:
        i = unit['nodeIndex']
        a.need(owners[unit['output']] == [i], 'Native output has another graph producer')
        a.need(nodes[i].get('Env', []) == [], 'Unevidenced compile environment overrides')

    # Record the exact file-edge path from the link to the selected native output.
    # ToBuildDependencies is a scheduling relation; it cannot alone prove that
    # a particular object or binary is actually a link/copy input.
    native_path = a.resolve(root, str(native))
    trail = {link_outs[0]: []}
    queue = deque([link_outs[0]])
    while queue:
        previous = queue.popleft()
        for i in consumers.get(previous, []):
            for path in outputs[i]:
                if Path(path).name != 'GameAssembly.dylib' or path in trail:
                    continue
                a.need(owners[path] == [i], 'Ambiguous selected-output copy producer')
                trail[path] = trail[previous] + [{'nodeIndex': i, 'input': previous, 'output': path}]
                queue.append(path)
    a.need(native_path in trail, 'Link output does not reach selected native library')

    a.need(Path(link_argv[0]).is_absolute(), 'Compiler executable must be an explicit absolute path')
    compiler = a.resolve(root, link_argv[0])
    sdk = a.resolve(root, a.option(link_argv, '-isysroot'))
    states, domains, seen_sources = {}, defaultdict(list), defaultdict(set)
    for unit in units:
        flags = unit['flags']
        a.need(Path(flags[0]).is_absolute(), 'Compiler executable must be an explicit absolute path')
        a.need(a.resolve(root, flags[0]) == compiler and
               a.resolve(root, a.option(flags, '-isysroot')) == sdk,
               'Native compiler/SDK action identities disagree')
        defs = a.definitions(flags)
        a.need(defs.get(FEATURE) == ('1' if feature else '0') and defs.get(DIAGNOSTIC) == '1',
               'An actual compiler action lacks the requested Shadow/count-diagnostic defines')
        domain = source_domain(unit, root)
        if domain == RUNTIME:
            state = a.effective_macros(flags, config)
            expected = {'IL2CPP_DEBUG': state['il2cppDebug'], 'NDEBUG': state['ndebug'],
                        'IL2CPP_DEVELOPMENT': state['il2cppDevelopment']}
        else:
            a.need('IL2CPP_DEBUG' not in defs and 'IL2CPP_DEVELOPMENT' not in defs,
                   'External source must not claim ownership of IL2CPP configuration macros')
            expected = {'IL2CPP_DEBUG': None, 'NDEBUG': '1' if 'NDEBUG' in defs else '0',
                        'IL2CPP_DEVELOPMENT': None}
            seen_sources[domain].add(Path(unit['source']).relative_to(root / INSTALLED / 'external').as_posix())
        expected.update({FEATURE: '1' if feature else '0', DIAGNOSTIC: '1'})
        a.need(domain not in states or states[domain] == expected,
               'Translation units disagree within macro domain: ' + domain)
        states[domain] = expected
        domains[domain].append(unit['nodeIndex'])
        unit['macroDomain'] = domain
    a.need(RUNTIME in domains, 'Missing IL2CPP runtime macro domain')
    runtime = states[RUNTIME]
    for name, files in EXTERNAL.items():
        domain = 'external-' + name
        if domain not in domains:
            continue
        a.need(seen_sources[domain] == {name + '/' + f for f in files} and
               len(domains[domain]) == len(files), 'External source membership differs: ' + name)
        # NDEBUG is library-owned here: consistency and real headerless probes
        # are mandatory, but the runtime assertion profile is not imposed on GC
        # or zlib. Their recorded state is never used to prove runtime assertions.
    ledger = [{'id': name, 'unitIndices': sorted(domains[name]), 'expectedMacros': states[name],
               'configurationIncludedInProbe': name == RUNTIME} for name in sorted(domains)]
    return {'compileActionCount': len(units), 'linkActionCount': 1,
            'compilerPath': compiler, 'sdkPath': sdk, 'beeLinkOutputPath': link_outs[0],
            'il2cppDebug': runtime['IL2CPP_DEBUG'], 'ndebug': runtime['NDEBUG'],
            'il2cppDevelopment': runtime['IL2CPP_DEVELOPMENT'], 'responseSources': sorted(used),
            'macroDomainPolicy': POLICY, 'macroDomains': ledger,
            'linkage': {'linkNodeIndex': link_index, 'objectUnitIndices': [u['nodeIndex'] for u in object_units],
                        'selectedNative': native_path, 'postLinkFileEdges': trail[native_path]}}
