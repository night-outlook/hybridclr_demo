"""Reconstruct exact oversized Q evidence copies into a new absolute unused directory."""
import pathlib,hashlib,json,sys
root=pathlib.Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_LARGE_FILES.py /absolute/unused/output-directory')
target=pathlib.Path(sys.argv[1]);assert target.is_absolute() and not target.exists();manifest=json.loads((root/'LARGE_FILE_TRANSPORT.json').read_text());target.mkdir(parents=True)
for row in manifest['files']:
 rel=pathlib.Path(row['originalPath']);assert not rel.is_absolute() and '..' not in rel.parts;out=target/rel;out.parent.mkdir(parents=True,exist_ok=True);whole=hashlib.sha256();size=0
 with out.open('xb') as dst:
  for item in row['parts']:
   rel=pathlib.Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts;part=root/rel;partHash=hashlib.sha256();partSize=0
   with part.open('rb') as src:
    for data in iter(lambda:src.read(1048576),b''):dst.write(data);whole.update(data);partHash.update(data);size+=len(data);partSize+=len(data)
   assert partHash.hexdigest()==item['sha256'] and partSize==item['size']
 assert whole.hexdigest()==row['originalSha256'] and size==row['originalSize'];print(row['originalPath'],whole.hexdigest(),size)
