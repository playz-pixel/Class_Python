cipher_dict = {
    'a': '!', 'b': '@', 'c': '#', 'd': '$', 'e': '%',
    'h': '^', 'i': '&', 'l': '*', 'm': '(', 'o': ')',
    'u': '-', ' ': '_'  
}

def ma_hoa(van_ban, bang_ma):
    ket_qua = ""
    for char in van_ban.lower():
        ket_qua += bang_ma.get(char, char)
    return ket_qua
def giai_ma(van_ban_ma, bang_ma):
    reverse_dict = {v: k for k, v in bang_ma.items()}
    
    ket_qua = ""
    for char in van_ban_ma:
        ket_qua += reverse_dict.get(char, char)
    return ket_qua
text_goc = "hello ad"
encoded_text = ma_hoa(text_goc, cipher_dict)
print(f"Văn bản gốc: {text_goc}")
print(f"Văn bản đã mã hóa: {encoded_text}")
decoded_text = giai_ma(encoded_text, cipher_dict)
print(f"Văn bản sau khi giải mã: {decoded_text}")