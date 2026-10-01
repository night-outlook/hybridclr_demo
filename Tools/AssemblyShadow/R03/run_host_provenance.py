#!/usr/bin/env python3
"""Audit preserved D observations and the new scope contract, without rerunning D.

Synthetic filtered projections are contract tests only. No native app or Editor
is launched; no historical receipt/source/evidence is edited or reclassified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from batch_contract import loads, require, sha, ContractError
from batch_evidence import write
from build_provenance import inventory_entries, NATIVE_RELATIVE, INSTALL_FILE, RECEIPT_VERSION, OVERLAY
from editor_scope import load_scope, verify_editor, REFERENCE, EXCLUDED, PACKAGE

CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261001-batch-d-return-required'
SETTINGS_BLOB = '014b8f3f62be45f58f15f150032a9e2d0a65cc30'


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--admission-results', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    demo, package = args.workspace / 'hybridclr_demo', args.workspace / 'hybridclr_unity'
    root = args.output.resolve(); require(not root.exists(), 'Unused host result root required'); root.mkdir(parents=True)
    result = {'kind': 'R03ProvenanceAndScopeHostContracts', 'schemaVersion': 1, 'result': 'Failed',
              'freshEditorExecution': False, 'nativeExecution': False, 'R03Accepted': False, 'H2Passed': False,
              'historicalBatchResult': 'ReturnRequired', 'historicalCellReclassification': False, 'builds': []}
    try:
        require(blob((package / 'Editor/SettingsUtil.cs').read_bytes()) == SETTINGS_BLOB,
                'Review installed-root profile when SettingsUtil changes')
        source = (demo / 'Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs').read_text()
        require('public int schemaVersion = 2;' in source and 'receipt.installedNativeRoot = native;' in source,
                'Producer must emit actual installed root in v2')
        checkpoint = demo / CHECKPOINT
        diagnostic_path = checkpoint / 'preflight/DIAGNOSTIC_FINDINGS.json'
        diagnostic = loads(diagnostic_path.read_text())
        roles = {'candidate-release', 'reference-release', 'candidate-debug', 'candidate-off'}
        require({b['role'] for b in diagnostic['builds']} == roles, 'Four original role diagnostics required')
        for item in diagnostic['builds']:
            role = item['role']
            build_path = checkpoint / 'batch/builds' / role / 'build-receipt.json'
            build = loads(build_path.read_text())
            require(sha(build_path) == item['receiptSha256'], 'Preserved build receipt hash')
            require(build['schemaVersion'] == 1 and 'installedNativeRoot' not in build,
                    'Original receipt is v1, not new execution authority')
            require(build['result'] == 'Passed' and build['errors'] == 0 and item['runnerBuildCellResult'] == 'Failed',
                    'Preserve artifact/cell distinction')
            before, after = inventory_entries(build['installedBefore']), inventory_entries(build['installedAfter'])
            require(len(after) == len(before) + 1 and set(after) - set(before) == {OVERLAY},
                    'Each role adds precisely its diagnostic probe; reference cores may have fewer files')
            require(after[INSTALL_FILE]['sha256'] == build['installReceiptSha256'], 'Original install hash binding')
            installed = checkpoint / 'preflight/native-receipts' / role / 'installed-sdk.json'
            copied = installed.with_name('stripped-aot-copy.json')
            require(installed.read_bytes() == copied.read_bytes() and sha(installed) == build['installReceiptSha256'],
                    'Byte-identical installation receipt copies are legitimate content duplicates')
            locators = item['hashMatchingInstallReceipts']
            require(len(locators) == 2 and all(x['sha256'] == build['installReceiptSha256'] for x in locators),
                    'Original recursive lookup would reject two matches')
            native = Path(build['projectPath']) / NATIVE_RELATIVE
            canonical = [x for x in locators if x['nativeRoot'] == str(native)]
            require(len(canonical) == 1 and canonical[0]['exactInstalledAfterMatch'] is True and
                    canonical[0]['files'] == len(after),
                    'Recorded actual installed root/profile mismatch')
            other = next(x for x in locators if x is not canonical[0])
            require(other['changed'] == ['hybridclr/generated/MethodBridge.cpp'] and other['exactInstalledAfterMatch'] is False,
                    'Preserve recorded generated-copy distinction')
            result['builds'].append({'role': role, 'receiptSha256': sha(build_path),
                                    'originalSchema': 1, 'newRequiredSchema': RECEIPT_VERSION,
                                    'installedBeforeFiles': len(before), 'installedAfterFiles': len(after),
                                    'recordedReceiptCopies': 2, 'recordedInstalledRoot': str(native),
                                    'originalRunnerCell': 'Failed', 'newNativeVerification': 'NotRun'})
        host = loads(args.admission_results.read_text())
        require(host['result'] == 'Passed' and host['failures'] == 0, 'Fresh host admission contracts required')
        required_ids = [c['id'] for c in host['cases']]
        scope = load_scope(demo, PACKAGE, required_ids)
        write(root / 'editor-scope.json', scope)
        original = ET.parse(demo / REFERENCE).getroot()
        try:
            verify_editor(original, scope)
        except ContractError:
            result['originalDEditorStillRejected'] = True
        else:
            raise ValueError('Do not promote the unfiltered ignored D aggregate')
        # Deliberately synthetic result tree. Original XML is never overwritten.
        projection = ET.Element('test-run', result='Passed', total='754', passed='754',
                                failed='0', skipped='0', inconclusive='0')
        for name in scope['expectedNames']:
            ET.SubElement(projection, 'test-case', fullname=name, result='Passed')
        checked = verify_editor(projection, scope)
        result['syntheticScopeContract'] = {'result': checked['result'], 'selectedNames': 754,
                                          'notFreshEditorEvidence': True, 'excluded': EXCLUDED}
        result['excludedCoverage'] = scope['excluded']
        result.update(referenceXmlSha256=scope['referenceSha256'], scopeSha256=sha(root / 'editor-scope.json'),
                      diagnosisSha256=sha(diagnostic_path), result='Passed')
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(root / 'results.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
