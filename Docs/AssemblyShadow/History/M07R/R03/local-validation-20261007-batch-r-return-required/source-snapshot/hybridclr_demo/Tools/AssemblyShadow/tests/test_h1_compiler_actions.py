import unittest
from pathlib import Path
import h1_compiler_actions as h

CONFIG = '#ifndef IL2CPP_DEBUG\n#define IL2CPP_DEBUG 0\n#endif\n#ifndef IL2CPP_DEVELOPMENT\n#define IL2CPP_DEVELOPMENT 0\n#endif\n'
ROOT = Path('/project')


def graph(flags='-DIL2CPP_DEBUG=1', second=None, link_flags=''):
    actions = [flags] if second is None else [flags, second]
    nodes = [{'Annotation': 'C_Mac_arm64 ' + str(i),
        'Action': '/tool/clang++ -isysroot /sdk ' + item + ' -c input.cpp -o out' + str(i) + '.o',
        'Inputs': ['input.cpp'], 'Outputs': ['out' + str(i) + '.o']} for i, item in enumerate(actions)]
    nodes += [{'Annotation': 'Link_Mac_arm64', 'Action': '/tool/clang++ -isysroot /sdk ' + link_flags,
        'Inputs': ['out' + str(i) + '.o' for i in range(len(actions))], 'Outputs': ['Library/GameAssembly.dylib']},
        {'Annotation': 'Copy', 'Inputs': ['Library/GameAssembly.dylib'], 'Outputs': ['Build/GameAssembly.dylib']}]
    return {'Nodes': nodes}


def derive(value, responses=None):
    return h.derive_graph_evidence(value, ROOT, ROOT / 'Build/GameAssembly.dylib', CONFIG, responses)


class CompilerActionsTests(unittest.TestCase):
    def test_debug(self): self.assertEqual('1', derive(graph())['il2cppDebug'])
    def test_release(self):
        value = derive(graph('-DNDEBUG=1')); self.assertEqual(('0','1'), (value['il2cppDebug'], value['ndebug']))
    def test_ndebug_zero_is_defined(self):
        self.assertEqual('1', h.effective_macros(['-DNDEBUG=0'], CONFIG)['ndebug'])
    def test_ordered_undefine(self):
        self.assertEqual('0', h.effective_macros(['-DNDEBUG=1', '-UNDEBUG'], CONFIG)['ndebug'])
    def test_ordered_redefine(self):
        self.assertEqual('0', h.effective_macros(['-DIL2CPP_DEBUG=1', '-DIL2CPP_DEBUG=0'], CONFIG)['il2cppDebug'])
    def test_separate_operand(self):
        self.assertEqual('1', h.effective_macros(['-D', 'IL2CPP_DEBUG=1'], CONFIG)['il2cppDebug'])
    def test_macro_union_cannot_mask_missing_override(self):
        with self.assertRaisesRegex(ValueError, 'Translation units'): derive(graph(second=''))
    def test_link_macro_not_compile_evidence(self):
        self.assertEqual('0', derive(graph(flags='', link_flags='-DIL2CPP_DEBUG=1'))['il2cppDebug'])
    def test_expand_nested_retained_responses(self):
        r = {'/project/a.rsp': b'@b.rsp', '/project/b.rsp': b'-DIL2CPP_DEBUG=1'}
        data = derive(graph(flags='@a.rsp'), r)
        self.assertEqual([' /project/a.rsp'.strip(), '/project/b.rsp'], data['responseSources'])
        self.assertEqual('1', data['il2cppDebug'])
    def test_unretained_response_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unretained'): derive(graph(flags='@missing.rsp'))
    def test_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError, 'cycle'): h.expand(['@a'], ROOT, {'/project/a': b'@a'})
    def test_depth_rejected(self):
        r = {'/project/' + str(i): ('@' + str(i + 1)).encode() for i in range(18)}
        with self.assertRaisesRegex(ValueError, 'nesting'): h.expand(['@0'], ROOT, r)
    def test_spaces_in_response_path(self):
        args = h.split('/tool/clang++ @"has space.rsp"')
        self.assertEqual(['/tool/clang++', '-O2'], h.expand(args, ROOT, {'/project/has space.rsp': b'-O2'})[0])
    def test_response_macro_can_undefine_direct_macro(self):
        data = derive(graph('-DIL2CPP_DEBUG=1 @a.rsp'), {'/project/a.rsp': b'-UIL2CPP_DEBUG'})
        self.assertEqual('0', data['il2cppDebug'])
    def test_ambiguous_header_rejected(self):
        with self.assertRaises(ValueError): h.header_default(CONFIG + CONFIG, 'IL2CPP_DEBUG')
    def test_forced_include_requires_proof(self):
        with self.assertRaisesRegex(ValueError, 'preprocessing'): h.effective_macros(['-include', 'other.h'], CONFIG)
    def test_unresolved_expression_rejected(self):
        with self.assertRaises(ValueError): h.effective_macros(['-DIL2CPP_DEBUG=OTHER'], CONFIG)
    def test_mismatched_sdk_rejected(self):
        value=graph(second=''); value['Nodes'][1]['Action']=value['Nodes'][1]['Action'].replace('/sdk','/sdk2')
        with self.assertRaises(ValueError): derive(value)
    def test_unreachable_library_rejected(self):
        value=graph(); value['Nodes'].pop()
        with self.assertRaisesRegex(ValueError, 'reach'): derive(value)
    def test_duplicate_link_rejected(self):
        value=graph(); value['Nodes'].append(value['Nodes'][1])
        with self.assertRaises(ValueError): derive(value)
    def test_shell_action_rejected(self):
        with self.assertRaises(ValueError): h.split('/tool/clang++ input.cpp && touch output')
    def test_empty_response_allowed(self):
        self.assertEqual(([], {'/project/a'}), h.expand(['@a'], ROOT, {'/project/a': b''}))



class ExtraMacroTests(unittest.TestCase):
    def test_explicit_values_do_not_eagerly_require_header_defaults(self):
        import h1_compiler_actions as h
        self.assertEqual('1',h.effective_macros(['-DIL2CPP_DEBUG=1','-DIL2CPP_DEVELOPMENT=0'],'')['il2cppDebug'])
    def test_function_like_ndebug_still_counts_as_defined(self):
        import h1_compiler_actions as h
        self.assertEqual('1',h.effective_macros(['-DNDEBUG(x)=0','-DIL2CPP_DEBUG=1','-DIL2CPP_DEVELOPMENT=0'],'')['ndebug'])
    def test_function_like_tracked_boolean_requires_preprocessing(self):
        import h1_compiler_actions as h
        with self.assertRaisesRegex(ValueError,'preprocessing'):
            h.definitions(['-DIL2CPP_DEBUG(x)=1'])

if __name__ == '__main__': unittest.main()
