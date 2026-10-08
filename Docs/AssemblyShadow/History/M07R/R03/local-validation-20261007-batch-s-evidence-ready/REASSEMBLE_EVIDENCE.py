"""Reassemble exact transported evidence into an absolute unused directory."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_EVIDENCE.py /absolute/unused/directory')
out=Path(sys.argv[1]);assert out.is_absolute() and not out.exists();out.mkdir(parents=True)
for row in json.loads((root/'FILE_TRANSPORT.json').read_text())['files']:
 rel=Path(row['originalPath']);assert not rel.is_absolute() and '..' not in rel.parts;target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);whole=hashlib.sha256();total=0
 with target.open('xb') as dst:
  for part in row['parts']:
   rel=Path(part['path']);assert not rel.is_absolute() and '..' not in rel.parts;file=root/rel;h=hashlib.sha256();size=0
   with file.open('rb') as src:
    for block in iter(lambda:src.read(1048576),b''):h.update(block);whole.update(block);size+=len(block);total+=len(block);dst.write(block)
   assert h.hexdigest()==part['sha256'] and size==part['size']
 assert whole.hexdigest()==row['originalSha256'] and total==row['originalSize'];print(row['originalPath'],whole.hexdigest(),total)
