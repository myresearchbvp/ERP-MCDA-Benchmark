from __future__ import annotations
from pathlib import Path
import hashlib,csv,gzip

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def verify_checksum_manifest(repo:Path)->list[dict]:
    rows=[]
    for line in (repo/'checksums.sha256').read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        expected,rel=line.split('  ',1); p=repo/rel
        got=sha256(p) if p.exists() else 'MISSING'
        ok=got==expected
        rows.append({'gate':'scientific_checksum','object':rel,'status':'PASS' if ok else 'FAIL','expected_sha256':expected,'observed_sha256':got,'note':'computational checksum scope'})
    return rows

def compare_files(got:Path,ref:Path,gate:str,obj:str)->dict:
    gh=sha256(got); rh=sha256(ref); ok=gh==rh
    return {'gate':gate,'object':obj,'status':'PASS' if ok else 'FAIL','expected_sha256':rh,'observed_sha256':gh,'note':'byte-identical reference parity'}

def csv_rows(path:Path):
    opener=gzip.open if path.suffix=='.gz' else open
    mode='rt' if path.suffix=='.gz' else 'r'
    with opener(path,mode,encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
