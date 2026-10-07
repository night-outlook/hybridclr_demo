"""Read-only native-action census, not a macro-domain admission policy.

Preserves complete raw actions plus declared paths to the selected native output.
Counts, language, directory hashes and macro values never authorize exemptions.
"""
from __future__ import annotations

from collections import defaultdict, deque
import copy
import hashlib
import json
from pathlib import Path

import h1_compiler_actions as a

MAX_NODES = 16384
MAX_EDGES = 262144
MAX_PATHS = 65536


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def inventory(graph: dict, root: Path, native: Path, responses=None) -> dict:
    nodes = graph.get('Nodes')
    a.need(type(nodes) is list and 0 < len(nodes) <= MAX_NODES, 'Census requires a bounded node inventory')
    responses = responses or {}
    paths_in, paths_out = [], []
    owners, consumers = defaultdict(list), defaultdict(list)
    errors = []
    path_count = 0
    for index, node in enumerate(nodes):
        values = {}
        for key in ('Inputs', 'Outputs'):
            raw = node.get(key, []) if type(node) is dict else []
            if type(raw) is not list or any(type(p) is not str or not p for p in raw):
                errors.append({'nodeIndex': index, 'error': 'Malformed ' + key})
                raw = []
            path_count += len(raw)
            a.need(path_count <= MAX_PATHS, 'Census path inventory bound exceeded')
            a.need(all(len(p) <= 4096 for p in raw), 'Census path length bound exceeded')
            try:
                values[key] = [a.resolve(root, p) for p in raw]
            except ValueError as error:
                errors.append({'nodeIndex': index, 'error': str(error)})
                values[key] = []
        paths_in.append(values['Inputs']); paths_out.append(values['Outputs'])
        for path in set(values['Outputs']): owners[path].append(index)
        for path in set(values['Inputs']): consumers[path].append(index)
    reverse = defaultdict(set)
    edge_count = 0
    ambiguities = []
    for path, producer_ids in owners.items():
        if len(producer_ids) != 1:
            ambiguities.append({'path': path, 'producers': producer_ids})
            continue
        for consumer in consumers.get(path, []):
            if consumer != producer_ids[0]:
                reverse[consumer].add(producer_ids[0]); edge_count += 1
                a.need(edge_count <= MAX_EDGES, 'Census edge bound exceeded')
    for index, node in enumerate(nodes):
        if type(node) is not dict: continue
        keys = [k for k in ('Deps', 'Dependencies', 'ToBuildDependencies') if k in node]
        if len(keys) > 1:
            errors.append({'nodeIndex': index, 'error': 'Ambiguous dependency representation'})
            continue
        deps = node[keys[0]] if keys else []
        if type(deps) is not list or any(type(d) is not int or not 0 <= d < len(nodes) for d in deps):
            errors.append({'nodeIndex': index, 'error': 'Malformed dependency indices'})
            continue
        for dep in deps:
            reverse[index].add(dep); edge_count += 1
            a.need(edge_count <= MAX_EDGES, 'Census edge bound exceeded')
    selected = owners.get(a.resolve(root, str(native)), [])
    next_node = {}
    queue = deque()
    if len(selected) == 1:
        next_node[selected[0]] = None
        queue.append(selected[0])
    while queue:
        consumer = queue.popleft()
        for producer in sorted(reverse.get(consumer, ())):
            if producer not in next_node:
                next_node[producer] = consumer
                queue.append(producer)
    rows = []
    for index, node in enumerate(nodes):
        if type(node) is not dict or not str(node.get('Annotation', '')).startswith('C_Mac_arm64'):
            continue
        row = {'nodeIndex': index, 'rawNode': copy.deepcopy(node),
            'nodeSha256': hashlib.sha256(canonical(node)).hexdigest(),
            'absoluteInputs': paths_in[index], 'absoluteOutputs': paths_out[index],
            'domainDecision': 'NotClassifiedRequiresPrimaryReview'}
        try:
            args, used = a.expand(a.split(node.get('Action')), root, responses)
            row['expandedArgv'] = args
            row['responseSources'] = sorted(used)
        except ValueError as error:
            row['argumentError'] = str(error)
        if index in next_node:
            path = [index]
            while next_node[path[-1]] is not None:
                path.append(next_node[path[-1]])
            row['declaredPathToSelectedOutput'] = path
            row['relationStatus'] = 'DeclaredDependencyPathObservedNotExecuted'
        else:
            row['declaredPathToSelectedOutput'] = []
            row['relationStatus'] = 'NoUnambiguousDeclaredPathFound'
        rows.append(row)
    return {'schemaVersion': 1, 'kind': 'H1NativeMacroDomainCensus',
        'status': 'InventoryOnlyNotAcceptance', 'nativeOutput': a.resolve(root, str(native)),
        'nativeOutputOwners': selected, 'rows': rows, 'compileActionCount': len(rows),
        'graphErrors': errors, 'ambiguousOutputOwners': ambiguities,
        'domainPolicyChanged': False, 'candidateAcceptance': False,
        'humanGatePassed': False, 'mayEnterR02': False}
