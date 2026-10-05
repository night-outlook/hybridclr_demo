"""Source wiring regression: API CI must validate the package it actually checks out."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]

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

if __name__ == '__main__': unittest.main()
