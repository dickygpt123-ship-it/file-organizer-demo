import tempfile
import unittest
from pathlib import Path
from organize_files import plan, copy_files


class OrganizerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'input'
        self.source.mkdir()
        self.output = self.root / 'output'

    def test_preview_copy_unicode_and_duplicate_basenames(self):
        originals = {'客户甲/订单.TXT': b'one', '客户乙/订单.TXT': b'two', 'README': b'three'}
        for name, data in originals.items():
            file = self.source / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        manifest = plan(self.source, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(copy_files(manifest), 3)
        for name, data in originals.items():
            self.assertEqual((self.source / name).read_bytes(), data)
            extension = Path(name).suffix.lstrip('.').lower() or 'no-extension'
            self.assertEqual((self.output / extension / name).read_bytes(), data)

    def test_refuses_overwrite_and_nested_destinations(self):
        self.output.mkdir()
        sentinel = self.output / 'keep.txt'
        sentinel.write_text('keep')
        for target in [self.output, self.source, self.source / 'nested', self.root]:
            with self.assertRaises(ValueError):
                plan(self.source, target)
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_changed_source_requires_fresh_plan(self):
        source_file = self.source / 'a.txt'
        source_file.write_text('before')
        manifest = plan(self.source, self.output)
        source_file.write_text('after')
        with self.assertRaises(ValueError):
            copy_files(manifest)
        self.assertFalse(self.output.exists())

    def test_rejects_modified_target(self):
        (self.source / 'a.txt').write_text('a')
        manifest = plan(self.source, self.output)
        manifest['files'][0]['target'] = str(self.root / 'outside.txt')
        with self.assertRaises(ValueError):
            copy_files(manifest)
        self.assertFalse((self.root / 'outside.txt').exists())


if __name__ == '__main__':
    unittest.main()
