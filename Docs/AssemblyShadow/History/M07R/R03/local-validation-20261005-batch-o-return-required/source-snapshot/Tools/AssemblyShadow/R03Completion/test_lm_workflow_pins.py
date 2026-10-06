"""Source wiring regressions for actual package pins and metadata dependencies."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = '$(PackageRoot)/Editor/AssemblyShadow/Metadata/NativeLayoutAdmissionValidator.cs'
CONTEXT = '$(PackageRoot)/Editor/AssemblyShadow/Metadata/NativeLayoutIdentityContext.cs'


def complete_named_layout_inputs(text):
    includes = {item.attrib.get('Include', '') for item in ET.fromstring(text).iter('Compile')}
    return VALIDATOR not in includes or CONTEXT in includes


class WorkflowPins(unittest.TestCase):
    def test_package_checkout_consumes_declared_pin(self):
        text = (ROOT / '.github/workflows/r03-build-api.yml').read_text()
        self.assertIn("for repo in ('hybridclr','hybridclr_unity','il2cpp_plus'):", text)
        self.assertIn('ref: ${{ steps.pins.outputs.hybridclr_unity }}', text)
        self.assertLess(text.index('id: pins'), text.index('repository: night-outlook/hybridclr_unity'))
        self.assertNotIn('ref: 120bb01be680cec0375002a0823552d66d34b84c', text)

    def test_build_api_keeps_exact_package_authority(self):
        text = (ROOT / 'Tools/AssemblyShadow/R03/build_api.py').read_text()
        self.assertIn("require(actual == pins['hybridclr_unity'], 'Host package pin mismatch')", text)

    def test_all_explicit_layout_project_lists_include_context(self):
        found = []
        for path in (ROOT / 'Tools/AssemblyShadow').rglob('*.csproj'):
            text = path.read_text()
            if VALIDATOR in text:
                found.append(path)
                self.assertTrue(complete_named_layout_inputs(text), str(path))
        self.assertGreaterEqual(len(found), 2)
        self.assertIn(ROOT / 'Tools/AssemblyShadow/R03/PlayerFixtures/PlayerFixtures.csproj', found)

    def test_missing_dependency_reproduces_old_project_gap(self):
        path = ROOT / 'Tools/AssemblyShadow/R03/PlayerFixtures/PlayerFixtures.csproj'
        text = path.read_text()
        self.assertEqual(text.count('<Compile Include="' + CONTEXT + '"/>'), 1)
        self.assertFalse(complete_named_layout_inputs(text.replace('<Compile Include="' + CONTEXT + '"/>', '')))

    def test_unrelated_project_is_not_a_layout_consumer(self):
        self.assertTrue(complete_named_layout_inputs('<Project><ItemGroup><Compile Include="Other.cs"/></ItemGroup></Project>'))

if __name__ == '__main__': unittest.main()
