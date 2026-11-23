import sys, re
for path in sys.argv[1:]:
    s = open(path, encoding='utf-8', errors='replace').read()
    obj = None
    for m in re.finditer(r'<object name="([^"]*)"|<parameter name="([^"]*)"[^>]*>.*?<value ([^>]*)>', s, re.S):
        if m.group(1) is not None:
            obj = m.group(1); print(f"\n[{path}] {obj}"); continue
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(3)))
        print(f"  {m.group(2)} = {attrs.get('current','')!r}  (default={attrs.get('default','')!r})")
