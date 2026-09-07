"""Source-derived algorithm calculations, NOT repository or IL2CPP Player tests.

Pinned sources: night-outlook/hybridclr @ a19db144751f4f016769b90e61a80b8c27578678
  hybridclr/metadata/MetadataUtil.h
  hybridclr/metadata/InterpreterImage.cpp
Graph counterexample: night-outlook/hybridclr_unity @
  2180b99daf39095cd76301da2bdf34ac945ee8b4
  Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs
No network, no source-tree modification, no third-party dependencies.
"""
from __future__ import annotations
import json
from pathlib import Path

INDEX_BITS = 22
KIND_BITS = 2
EXTRA_SHIFTS = (6, 4, 2, 0)
MASKS = tuple((1 << (INDEX_BITS + shift)) - 1 for shift in EXTRA_SHIFTS)
IMAGE_BITS = 32 - INDEX_BITS
MAX_IMAGE_INDEX_WITHOUT_KIND = 1 << (IMAGE_BITS - KIND_BITS)

class AllocatorModel:
    def __init__(self) -> None:
        self.next_by_kind = [1 << EXTRA_SHIFTS[0], 0, 0, 0]

    def allocate(self, dll_length: int) -> int | None:
        if not 0 < dll_length <= ((1 << 32) - 1) // 4:
            raise ValueError('Outside the staged DLL length guard')
        maximum_index = dll_length * 4
        kind = next((i for i in range(3, -1, -1) if maximum_index <= MASKS[i]), -1)
        if kind < 0:
            return None
        for final_kind in range(kind, -1, -1):
            new_index = self.next_by_kind[final_kind]
            if new_index >= MAX_IMAGE_INDEX_WITHOUT_KIND - (1 if final_kind == 3 else 0):
                continue
            self.next_by_kind[final_kind] += 1 << EXTRA_SHIFTS[final_kind]
            return new_index | (final_kind << (IMAGE_BITS - KIND_BITS))
        return None


def capacity(length: int) -> dict:
    model = AllocatorModel()
    indices = []
    while (index := model.allocate(length)) is not None:
        indices.append(index)
    assert len(indices) == len(set(indices))
    assert all(index not in (0, (1 << IMAGE_BITS) - 1) for index in indices)
    return {'dllBytes': length, 'freshProcessHomogeneousCapacity': len(indices),
            'finalCursors': model.next_by_kind}


def topological_providers_first(edges: set[tuple[str, str]]) -> list[str]:
    nodes = {name for edge in edges for name in edge}
    state: dict[str, int] = {}
    result: list[str] = []
    def visit(node: str) -> None:
        mark = state.get(node, 0)
        if mark == 1:
            raise ValueError('DependencyCycle')
        if mark == 2:
            return
        state[node] = 1
        for provider in sorted(p for consumer, p in edges if consumer == node):
            visit(provider)
        state[node] = 2
        result.append(node)
    for node in sorted(nodes):
        visit(node)
    return result


def main() -> None:
    rows = [capacity(length) for length in (1024, (1 << 20) - 1, 1 << 20,
                                           (1 << 22) - 1, 1 << 22,
                                           (1 << 24) - 1, 1 << 24,
                                           (1 << 26) - 1, 1 << 26)]
    assert [row['freshProcessHomogeneousCapacity'] for row in rows] == [338, 338, 83, 83, 19, 19, 3, 3, 0]
    mixed = AllocatorModel()
    for _ in range(10):
        assert mixed.allocate(1024) is not None
    remaining = 0
    while mixed.allocate(1024) is not None:
        remaining += 1
    assert remaining == 328

    baseline = {('Module.A', 'Module.B')}
    target = {('Module.B', 'Module.A')}
    graph_result = {'baselineOrder': topological_providers_first(baseline),
                    'targetOrder': topological_providers_first(target)}
    try:
        topological_providers_first(baseline | target)
        raise AssertionError('Union must contain the demonstrated artificial cycle')
    except ValueError as error:
        graph_result['currentUnionOrderError'] = str(error)
    output = {
        'kind': 'SourceDerivedAlgorithmCalculation',
        'repositoryTestsExecuted': False,
        'nativeRuntimeExecuted': False,
        'unityPlayerExecuted': False,
        'allocatorAssumptions': 'Fresh allocator; all DLLs in each row have the same byte length; no ordinary Interpreter images or prior failed allocation consumption.',
        'allocator': rows,
        'remainingSmallImageCapacityAfter10OrdinaryAllocations': remaining,
        'graphCounterexample': graph_result,
        'result': 'CalculatedAndAsserted'
    }
    path = Path(__file__).with_name('source-algorithm-results.json')
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
