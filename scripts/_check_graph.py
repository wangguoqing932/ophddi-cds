import json, re, csv
from collections import Counter

# Load GraphML
with open('data/processed/lightrag_index/graph_chunk_entity_relation.graphml', encoding='utf-8') as f:
    g = f.read()

nodes = re.findall(r'<node id="([^"]+)"', g)
edges = re.findall(r'<edge .*?source="([^"]+)".*?target="([^"]+)"', g)

print(f'Nodes: {len(nodes)}, Edges: {len(edges)}')

deg = Counter()
for s, t in edges:
    deg[s] += 1
    deg[t] += 1

all_degrees = [deg.get(n, 0) for n in nodes]
isolated = sum(1 for d in all_degrees if d == 0)
singleton = sum(1 for d in all_degrees if d == 1)
print(f'Isolated (deg=0): {isolated}/{len(nodes)} ({isolated/len(nodes)*100:.0f}%)')
print(f'Singleton (deg=1): {singleton}/{len(nodes)} ({singleton/len(nodes)*100:.0f}%)')
print(f'Mean degree: {sum(all_degrees)/len(all_degrees):.1f}')
print(f'Max degree: {max(all_degrees)}')

for lo, hi, label in [(0,0,'0'), (1,2,'1-2'), (3,5,'3-5'), (6,10,'6-10'), (11,20,'11-20'), (21,100,'21+')]:
    cnt = sum(1 for d in all_degrees if lo <= d <= hi)
    print(f'  deg {label}: {cnt} ({cnt/len(nodes)*100:.0f}%)')

# Drug coverage
drugs_a = set()
with open('data/seed/entities_a.csv', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        drugs_a.add(row['primary_name'].lower())

drugs_b = set()
with open('data/seed/entities_b.csv', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        drugs_b.add(row['generic_name'].lower())

node_lower = {n.strip('"').lower() for n in nodes}
a_in = sum(1 for d in drugs_a if d in node_lower)
b_in = sum(1 for d in drugs_b if d in node_lower)
print(f'\nDrug coverage:')
print(f'  Ophthalmic: {a_in}/{len(drugs_a)} ({a_in/len(drugs_a)*100:.0f}%)')
print(f'  Systemic:   {b_in}/{len(drugs_b)} ({b_in/len(drugs_b)*100:.0f}%)')

# Isolated node sample
if isolated > 0:
    iso = [n for n in nodes if deg.get(n, 0) == 0]
    print(f'\nIsolated nodes (first 15):')
    for n in iso[:15]:
        print(f'  {n[:80]}')
