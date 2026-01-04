def encode(message):
    vowels = 'aeiouAEIOU'
    shifted_vowels = {v: chr((ord(v) - 65 + 2) % 26 + 65) if v.isupper() else chr((ord(v) - 97 + 2) % 26 + 97) for v in vowels}
    encoded_message = ''.join(shifted_vowels.get(c, c).swapcase() for c in message)
    return encoded_message
