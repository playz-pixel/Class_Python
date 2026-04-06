import json
bo_ma = {
    'a': '!', 'b': '@', 'c': '#', 'd': '$', 'e': '%', 
    'h': '^', 'i': '&', 'l': '*', 'o': ')', 'u': '-', ' ': '_'
}

with open('bo_ma.json', 'w', encoding='utf-8') as f:
    json.dump(bo_ma, f)