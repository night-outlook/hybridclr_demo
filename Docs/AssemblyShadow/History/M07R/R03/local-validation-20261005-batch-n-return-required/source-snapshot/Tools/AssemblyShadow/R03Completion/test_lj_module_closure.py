"""Static regression derived from the authenticated J resolved lock, not a Unity run.

Source: demo 71bddefd86a3b718d9d36b3edc2d88cd21db1e92,
Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-j-return-required/
preflight/issue-resource-snapshot/Packages/packages-lock.json
Git blob: 61f02845b988206b6ffc75e4d380e9b9a95fc42f.
"""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resource_capabilities as profile
from batch_contract import ContractError

# All built-in module names in the published J lock. Subsystems was depth 1;
# the other modules were explicit roots. This catalogue is independent of the
# generator under test, and does not claim J had a successful target snapshot.
J_MODULES = frozenset('''ai androidjni animation assetbundle audio cloth director
imageconversion imgui jsonserialize particlesystem physics physics2d screencapture
subsystems terrain terrainphysics tilemap ui uielements umbra unityanalytics
unitywebrequest unitywebrequestassetbundle unitywebrequestaudio
unitywebrequesttexture unitywebrequestwww vehicles video vr wind xr'''.split())
TRANSITIVE = 'com.unity.modules.subsystems'


class ObservedModuleClosureTests(unittest.TestCase):
    def setUp(self):
        self.original = {'com.unity.modules.' + n: '1.0.0'
                         for n in J_MODULES if n != 'subsystems'}
        self.original.update({'com.unity.render-pipelines.universal': '14.0.12',
                              'com.unity.test-framework': '1.1.33',
                              'com.unity.ugui': '1.0.0'})
        self.manifest = profile.dependency_profile(self.original, Path('/owning/package'))
        self.lock = {'dependencies': {k: {'version': v}
                     for k, v in self.manifest['dependencies'].items()}}

    def test_observed_transitive_module_is_explicitly_pinned(self):
        self.assertNotIn(TRANSITIVE, self.original)
        self.assertEqual(self.manifest['dependencies'][TRANSITIVE], '1.0.0')

    def test_complete_observed_j_module_membership_reconciles(self):
        modules = {n.removeprefix('com.unity.modules.')
                   for n in self.manifest['dependencies'] if n.startswith('com.unity.modules.')}
        self.assertEqual(modules, J_MODULES)
        self.assertTrue(profile.validate_packages(self.manifest, self.lock))

    def test_missing_from_both_documents_is_not_optional(self):
        del self.manifest['dependencies'][TRANSITIVE]
        del self.lock['dependencies'][TRANSITIVE]
        with self.assertRaises(ContractError):
            profile.validate_packages(self.manifest, self.lock)

    def test_transitive_version_change_is_rejected(self):
        self.manifest['dependencies'][TRANSITIVE] = '2.0.0'
        self.lock['dependencies'][TRANSITIVE]['version'] = '2.0.0'
        with self.assertRaises(ContractError):
            profile.validate_packages(self.manifest, self.lock)

    def test_original_conflicting_module_version_is_rejected(self):
        original = copy.deepcopy(self.original)
        original[TRANSITIVE] = '2.0.0'
        with self.assertRaises(ContractError):
            profile.dependency_profile(original, Path('/owning/package'))

    def test_unknown_resolved_module_does_not_gain_a_waiver(self):
        self.lock['dependencies']['com.unity.modules.unreviewed'] = {'version': '1.0.0'}
        with self.assertRaises(ContractError):
            profile.validate_packages(self.manifest, self.lock)
