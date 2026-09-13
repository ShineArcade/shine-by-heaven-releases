"""Reapply and rebuild the approved release; assert exact artifact reproducibility."""
import hashlib,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
paths=list((ROOT/'bible-content/apps/mobile/assets/bible_direction').rglob('*.json'))+list((ROOT/'bible-content/apps/mobile/assets/bible_direction').rglob('*.gz'))
paths.append(ROOT/'bible-content/apps/mobile/tool/bible_content_channel.v1.source.json')
def snapshot():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=snapshot()
for command in [('node','apply_editorial_change_set.mjs'),('node','build_reading_2026_package.mjs','--package-only'),('python','build_kjv_reading_2026_package.py')]:
 result=subprocess.run([command[0],str(ROOT/'bible-content/apps/mobile/tool'/command[1]),*command[2:]],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
 assert result.returncode==0,(command,result.stdout,result.stderr)
assert before==snapshot(),'Reapplying or rebuilding changed approved bytes'
print(json.dumps(dict(result='PASS',files=len(paths),reapplication='idempotent',packages='byte-identical')))
