chars = ""

with open('ws.txt', 'r', encoding='utf-8') as w:
    global words
    words = w.read().split('\n')

for w in words:
    for l in w:
        if l in chars:
            pass
        else:
            chars = chars+l

print(chars)
print(len(chars))
