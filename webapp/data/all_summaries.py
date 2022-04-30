import json

f = open('./all_summaries.txt').read().split('\n')
lines = {}
for l in f:
    if len(l)==0: continue
    print(l)
    lc = l.split()
    lines[lc[0][:-4]] = ' '.join(lc[1:])

q = open('./all_summaries.json', 'w+').write(json.dumps(lines))
