import hashlib
import io
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch
import export_m00_fixture as export
import ordinary_input as ordinary
from test_ordinary_input import setup_project


class ArchiveOrigin(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=setup_project(Path(self.tmp.name).resolve()/'repo')
        self.data=ordinary.fixture(self.root)[0]
        self.output=self.root/'export'

    def archive(self, names):
        archive=self.root/export.ARCHIVE;archive.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive,'w:gz') as stream:
            for name in names:
                member=tarfile.TarInfo(name);member.size=len(self.data)
                stream.addfile(member,io.BytesIO(self.data))
        return hashlib.sha256(archive.read_bytes()).hexdigest()

    def test_exact_member_and_compact_fixture_are_cross_authenticated(self):
        sha=self.archive([ordinary.MEMBER])
        with patch.object(export,'ARCHIVE_SHA',sha):
            result=export.export(self.root,self.output,True)
        self.assertEqual(result['result'],'FrozenFixtureOriginVerified')
        self.assertEqual((self.output/'frozen-m00.dll').read_bytes(),self.data)
        self.assertFalse(result['historicalPlayerExecutionReused'])

    def test_archive_digest_mismatch_rejected(self):
        self.archive([ordinary.MEMBER])
        with self.assertRaisesRegex(ValueError,'archive hash mismatch'):
            export.export(self.root,self.output,True)

    def test_same_bytes_wrong_origin_member_rejected(self):
        sha=self.archive(['different-origin.dll'])
        with patch.object(export,'ARCHIVE_SHA',sha):
            with self.assertRaisesRegex(ValueError,'Pinned historical member'):
                export.export(self.root,self.output,True)

    def test_duplicate_or_escaping_archive_members_rejected(self):
        for names in ([ordinary.MEMBER,ordinary.MEMBER],['../bad']):
            with self.subTest(names=names):
                # Each separate archive/output is a labelled synthetic input.
                archive=self.root/export.ARCHIVE
                if archive.exists():archive.unlink()
                sha=self.archive(names)
                output=self.root/('export-'+str(len(names)))
                with patch.object(export,'ARCHIVE_SHA',sha):
                    with self.assertRaisesRegex(ValueError,'Unsafe or duplicate'):
                        export.export(self.root,output,True)

    def test_symbolic_link_archive_member_refused(self):
        archive=self.root/export.ARCHIVE;archive.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive,'w:gz') as stream:
            member=tarfile.TarInfo('link');member.type=tarfile.SYMTYPE;member.linkname='outside'
            stream.addfile(member)
        sha=hashlib.sha256(archive.read_bytes()).hexdigest()
        with patch.object(export,'ARCHIVE_SHA',sha):
            with self.assertRaisesRegex(ValueError,'Non-regular'):
                export.export(self.root,self.output,True)


if __name__=='__main__':unittest.main()
