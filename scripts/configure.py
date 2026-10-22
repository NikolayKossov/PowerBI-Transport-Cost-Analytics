"""Set the Power Query source root for this checkout. Close Desktop first."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
file=root/'model/Analytics.SemanticModel/model.bim'
data=json.loads(file.read_text(encoding='utf-8'))
path='C:/PowerBI/data' if '--reset' in sys.argv else (root/'data').as_posix()
expression='"'+path.replace('"','""')+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
next(x for x in data['model']['expressions'] if x['name']=='DataRoot')['expression']=expression
file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'power-query/DataRoot.m').write_text(expression+'\n',encoding='utf-8')
print('DataRoot =',path)
