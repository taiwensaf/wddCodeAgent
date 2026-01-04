def encrypt(s):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    encrypted = ''
    for char in s:
        if char.isalpha():
            shift = (2 * 3) % 26
            new_index = (alphabet.index(char.lower()) + shift) % 26
            new_char = alphabet[new_index]
            encrypted += new_char.upper() if char.isupper() else new_char
        else:
            encrypted += char
    return encrypted