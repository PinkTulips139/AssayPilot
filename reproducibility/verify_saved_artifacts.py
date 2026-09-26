from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'reproducibility/artifact_index.json').read_text(encoding='utf-8'))
bad=[]
for item in items:
 p=root/item['public_path']
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['public_sha256']: bad.append(item['public_path'])
print(json.dumps({'checked':len(items),'mismatches':bad,'status':'PASS' if not bad else 'FAIL'}))
raise SystemExit(bool(bad))
