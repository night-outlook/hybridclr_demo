"""Filesystem controls are unit evidence, not Mac batch/capacity acceptance."""
import errno
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

import storage_guard as g


def observation(available=128*g.GIB, *, device=1, read_only=False, roles=('batch', 'temp')):
    return {'observedUtc': 'fixture', 'monotonicNs': 1, 'volumes': [
        dict(role=name, device=device, fsid=11, availableBytes=available, freeBytes=256*g.GIB,
             totalBytes=512*g.GIB, availableFileNodes=0, readOnly=read_only) for name in roles]}


class StoragePolicyTests(unittest.TestCase):
    def test_minimum_and_empirical_budget(self):
        self.assertEqual(g.required_start({'planningBytes': 0}), 64*g.GIB)
        self.assertEqual(g.required_start({'planningBytes': 30*g.GIB}), 80*g.GIB)
        self.assertEqual(g.required_start({'planningBytes': 50*g.GIB}), 120*g.GIB)

    def test_invalid_size_never_admitted(self):
        for value in (-1, True, 3.5, '1'):
            with self.subTest(value=value), self.assertRaises(g.StorageBlocked):
                g.required_start({'planningBytes': value})

    def test_q_entry_and_post_failure_capacity_both_rejected(self):
        for free in (22*g.GIB, 14847991808):
            with self.subTest(free=free), self.assertRaises(g.StorageBlocked):
                g.capacity_ok(observation(free), g.START_MIN)

    def test_inclusive_threshold(self):
        g.capacity_ok(observation(g.START_MIN), g.START_MIN)
        with self.assertRaises(g.StorageBlocked):
            g.capacity_ok(observation(g.START_MIN-1), g.START_MIN)

    def test_shared_volumes_never_summed(self):
        with self.assertRaises(g.StorageBlocked):
            g.capacity_ok(observation(40*g.GIB), 64*g.GIB)

    def test_read_only_denied(self):
        with self.assertRaises(g.StorageBlocked):
            g.capacity_ok(observation(read_only=True), g.FLOOR)

    def test_filesystem_switch_denied(self):
        with self.assertRaises(g.StorageBlocked):
            g.capacity_ok(observation(device=2), g.FLOOR, {'batch': (1,11), 'temp': (1,11)})

    def test_file_node_stat_is_diagnostic_not_static_inode_guarantee(self):
        g.capacity_ok(observation(), g.FLOOR)

    def test_no_locations_denied(self):
        with self.assertRaises(g.StorageBlocked):
            g.capacity_ok(dict(volumes=[]), g.FLOOR)


class PathAndAllocationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_canonical_unused_leaf(self):
        self.assertEqual(g.existing_parent(self.root/'new'/'leaf'), self.root)

    def test_relative_and_parent_traversal_rejected(self):
        for p in (Path('relative'), self.root/'..'/'other'):
            with self.assertRaises(g.StorageBlocked): g.canonical(p)

    def test_symlink_parent_and_dangling_link_rejected(self):
        alias = self.root/'alias'; alias.symlink_to(self.root, target_is_directory=True)
        dangling = self.root/'dangling'; dangling.symlink_to(self.root/'absent')
        for p in (alias/'new', dangling/'new'):
            with self.assertRaises(g.StorageBlocked): g.canonical(p)

    def test_existing_file_not_probe_directory(self):
        p=self.root/'file'; p.write_text('keep')
        with self.assertRaises(g.StorageBlocked): g.existing_parent(p)

    def test_snapshot_uses_unprivileged_free_not_total_free(self):
        v=SimpleNamespace(f_frsize=4096,f_bsize=4096,f_blocks=100,f_bavail=3,f_bfree=90,
                          f_favail=12,f_flag=0,f_fsid=44)
        with mock.patch.object(g.os,'statvfs',return_value=v): row=g.sample({'test':self.root})['volumes'][0]
        self.assertEqual(row['availableBytes'],12288);self.assertEqual(row['freeBytes'],368640)

    def test_negative_available_saturates_to_zero(self):
        v=SimpleNamespace(f_frsize=4096,f_bsize=4096,f_blocks=100,f_bavail=-1,f_bfree=90,
                          f_favail=12,f_flag=0,f_fsid=44)
        with mock.patch.object(g.os,'statvfs',return_value=v): row=g.sample({'test':self.root})['volumes'][0]
        self.assertEqual(row['availableBytes'],0)

    def test_probe_writes_reads_and_only_removes_owned_files(self):
        sentinel=self.root/'user';sentinel.write_text('unchanged')
        report=g.allocation_probe(self.root)
        self.assertEqual(report['result'],'Passed');self.assertFalse(report['reservation'])
        self.assertEqual(list(self.root.iterdir()),[sentinel]);self.assertEqual(sentinel.read_text(),'unchanged')

    def test_probe_mkdir_enospc_retained(self):
        with mock.patch.object(g.tempfile,'mkdtemp',side_effect=OSError(errno.ENOSPC,'No space')):
            report=g.allocation_probe(self.root)
        self.assertEqual(report['result'],'Failed');self.assertEqual(report['error']['errno'],errno.ENOSPC)
        self.assertEqual(report['failedOperation'],'mkdir')

    def test_probe_fsync_failure_does_not_pass(self):
        with mock.patch.object(g.os,'fsync',side_effect=OSError(errno.EDQUOT,'quota')):
            report=g.allocation_probe(self.root)
        self.assertEqual(report['result'],'Failed');self.assertEqual(report['failedOperation'],'fsync')
        self.assertEqual(report['error']['errno'],errno.EDQUOT);self.assertEqual(list(self.root.iterdir()),[])

    def test_probe_cleanup_error_does_not_pass(self):
        real=Path.unlink
        def blocked(path,*a,**k):
            if path.name=='allocation.bin': raise OSError(errno.EACCES,'denied')
            return real(path,*a,**k)
        with mock.patch.object(Path,'unlink',blocked): report=g.allocation_probe(self.root)
        self.assertEqual(report['result'],'Failed');self.assertTrue(report['cleanupErrors'])

    def test_exclusive_receipt_write(self):
        p=self.root/'record.json';g.write_new(p,{'original':True})
        with self.assertRaises(FileExistsError):g.write_new(p,{'original':False})
        self.assertTrue(json.loads(p.read_text())['original'])

    def test_footprint_hardlink_and_symlink(self):
        p=self.root/'a';p.write_bytes(b'x'*8192);os.link(p,self.root/'b')
        (self.root/'link').symlink_to(p)
        d=g.footprint(self.root)
        self.assertEqual(d['logicalBytesPerPath'],16384)
        self.assertEqual(d['allocatedBytesUniqueInode'],p.stat().st_blocks*512)
        self.assertEqual(d['symlinksNotFollowed'],1);self.assertFalse(d['physicalApfsSharingKnown'])

    def test_sparse_file_uses_logical_upper_estimate(self):
        p=self.root/'sparse'
        with p.open('wb') as f:f.truncate(8*1024*1024)
        self.assertGreaterEqual(g.footprint(self.root)['planningBytes'],8*1024*1024)

    def test_scan_limits_do_not_authorize_partial_size(self):
        (self.root/'a').write_text('x')
        with self.assertRaises(g.StorageBlocked):g.footprint(self.root,max_entries=0)
        with self.assertRaises(g.StorageBlocked):g.footprint(self.root,seconds=-1)

    def test_special_file_not_ignored(self):
        os.mkfifo(self.root/'fifo')
        with self.assertRaises(g.StorageBlocked):g.footprint(self.root)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.q=self.root/'q';(self.q/'cells').mkdir(parents=True)
        self.cell=self.q/'cells/production-entry-integration.json';self.cell.write_text('preserved Q fixture')
        self.hash=g.digest(self.cell)
        self.patches=[mock.patch.object(g,'Q_CELL_SHA',self.hash),mock.patch.object(g,'diagnostics',return_value=[])]
        for p in self.patches:p.start();self.addCleanup(p.stop)
        self.session=g.StorageSession(self.root/'session',{'batch':self.root/'new','temp':self.root},interval=.01)
        self.addCleanup(self.close)

    def close(self):
        self.session.stop.set()
        if self.session.thread:self.session.thread.join(1)
        if not self.session.trace.closed:self.session.trace.close()

    def test_admit_and_finish_preserve_q_and_no_batch_creation(self):
        with mock.patch.object(g,'sample',return_value=observation()):
            self.assertEqual(self.session.admit(self.q)['state'],'Admitted')
            self.session.start();time.sleep(.03)
            report=self.session.finish(batch_started=False,batch_exit=None)
        self.assertEqual(report['state'],'Passed');self.assertGreaterEqual(report['samples'],3)
        self.assertFalse(self.session.thread.is_alive());self.assertFalse((self.root/'new').exists())
        self.assertEqual(g.digest(self.cell),self.hash)

    def test_low_space_denies_before_allocation_probe(self):
        with mock.patch.object(g,'sample',return_value=observation(22*g.GIB)),mock.patch.object(g,'allocation_probe') as probe:
            report=self.session.admit(self.q)
        self.assertEqual(report['state'],'Blocked');probe.assert_not_called()

    def test_wrong_q_evidence_denied(self):
        self.cell.write_text('changed')
        report=self.session.admit(self.q)
        self.assertEqual(report['state'],'Blocked')

    def test_probe_failure_denies(self):
        with mock.patch.object(g,'sample',return_value=observation()),mock.patch.object(g,'allocation_probe',return_value={'result':'Failed'}):
            report=self.session.admit(self.q)
        self.assertEqual(report['state'],'Blocked')

    def test_transient_floor_breach_remains_latched(self):
        self.session.devices={'batch':(1,11),'temp':(1,11)}
        with mock.patch.object(g,'sample',return_value=observation(g.FLOOR-1)):
            self.session.observe('periodic')
        with mock.patch.object(g,'sample',return_value=observation()):
            with self.assertRaises(g.StorageBlocked):self.session.before('integration')
            self.session.before('resource-p05-restore',cleanup=True)
        self.assertIsNotNone(self.session.problem)

    def test_missing_telemetry_fails_closed_but_preserves_cleanup(self):
        with mock.patch.object(g,'sample',side_effect=OSError(errno.EIO,'IO failure')):
            with self.assertRaises(g.StorageBlocked):self.session.before('compiler')
            self.session.before('restore',cleanup=True)
        self.assertEqual(self.session.problem['errno'],errno.EIO)

    def test_exception_preserves_errno_and_traceback(self):
        try:raise OSError(errno.ENOSPC,'actual fixture error','/fixture/directory')
        except OSError as error:
            with mock.patch.object(g,'sample',return_value=observation()):self.session.record_failure('integration',error)
        f=next(self.session.root.glob('failure-*.json'));v=json.loads(f.read_text())
        self.assertEqual(v['error']['errno'],errno.ENOSPC);self.assertIn('OSError',v['error']['traceback'])
        self.assertEqual(v['error']['filename'],'/fixture/directory')

    def test_second_session_root_rejected(self):
        with self.assertRaises(FileExistsError):g.StorageSession(self.session.root,self.session.paths)



class IntegrationProbeTests(unittest.TestCase):
    def test_exact_new_capture_parent_probed_before_integration(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();capture=root/'new-receipts';capture.mkdir()
            session=g.StorageSession(root/'evidence',{'restoredCapture':capture/'return-baseline'})
            try:
                with mock.patch.object(g,'sample',return_value=observation()),mock.patch.object(g,'allocation_probe',return_value={'result':'Passed'}) as probe:
                    session.before('production-entry-integration')
                probe.assert_called_once_with(capture)
                self.assertTrue((root/'evidence/integration-allocation-probe.json').is_file())
                self.assertFalse((capture/'return-baseline').exists())
            finally:session.trace.close()

    def test_integration_probe_failure_is_latched(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();session=g.StorageSession(root/'evidence',{'restoredCapture':root/'new'})
            try:
                with mock.patch.object(g,'sample',return_value=observation()),mock.patch.object(g,'allocation_probe',return_value={'result':'Failed'}):
                    with self.assertRaises(g.StorageBlocked):session.before('production-entry-integration')
                    with self.assertRaises(g.StorageBlocked):session.before('later-cell')
                    session.before('resource-p05-restore',cleanup=True)
            finally:session.trace.close()

    def test_unadmitted_monitor_cannot_start(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();session=g.StorageSession(root/'evidence',{'batch':root/'new'})
            try:
                with self.assertRaises(g.StorageBlocked):session.start()
            finally:session.trace.close()

if __name__=='__main__':unittest.main()
