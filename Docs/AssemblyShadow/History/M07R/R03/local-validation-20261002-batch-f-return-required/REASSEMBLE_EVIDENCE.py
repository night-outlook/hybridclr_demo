"""Reconstruct the exact sealed archive at a new, caller-specified path."""
import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
manifest=json.loads((root/'ARCHIVE_TRANSPORT.json').read_text())
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_EVIDENCE.py /absolute/unused/evidence.tar.gz')
target=pathlib.Path(sys.argv[1]);assert target.is_absolute() and not target.exists()
whole=hashlib.sha256();size=0
with target.open('xb') as output:
 for part in manifest['parts']:
  h=hashlib.sha256();n=0
  with (root/part['path']).open('rb') as source:
   for block in iter(lambda:source.read(1048576),b''):
    h.update(block);whole.update(block);output.write(block);n+=len(block)
  assert h.hexdigest()==part['sha256'] and n==part['size'];size+=n
assert whole.hexdigest()==manifest['originalSha256'] and size==manifest['originalSize']
print('Authenticated archive:',target,whole.hexdigest(),size)
