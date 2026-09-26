from pathlib import Path
import markdown
root=Path(__file__).resolve().parents[1]
folder=root/'REPORT'
if not folder.exists(): folder=root/'report'
src=folder/'ASSAYPILOT_TECHNICAL_REPORT.md'
body=markdown.markdown(src.read_text(encoding='utf-8'),extensions=['tables','fenced_code','toc'])
css="body{max-width:1080px;margin:40px auto;padding:0 24px;font:17px/1.65 Georgia,serif;color:#162b3b}h1,h2{font-family:system-ui;line-height:1.2}h2{margin-top:2em}img{width:100%;height:auto}table{border-collapse:collapse;width:100%;font:12px/1.4 system-ui;display:block;overflow-x:auto}td,th{padding:7px;border-bottom:1px solid #ccd3d8;text-align:left}th{background:#edf2f4}code{font-size:.8em;overflow-wrap:anywhere}a{color:#146785}@media print{body{margin:0;font-size:11pt}h2{break-after:avoid}img{break-inside:avoid}}"
(folder/'ASSAYPILOT_TECHNICAL_REPORT.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>AssayPilot Technical Report</title><style>'+css+'</style><body>'+body+'</body></html>',encoding='utf-8')
print('REPORT_HTML_RENDERED; no experiment executed')
