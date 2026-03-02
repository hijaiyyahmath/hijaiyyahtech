path = r'c:\hijaiyyah-codex\generate_st28_full.py'
with open(path, 'r', encoding='utf-8') as f:
    s = f.read()
s = s.replace('target_size=200', 'target_size=600')
with open(path, 'w', encoding='utf-8') as f:
    f.write(s)
print("Patched generate_st28_full.py to target_size=600")
