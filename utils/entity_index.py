import re

def entity_index(word, start_index, sentence):
    matched = re.finditer(re.escape(word), sentence)
    new_standard = float("inf")
    for word in matched:
        start_standard = abs(start_index - word.span()[0])
        if new_standard >= start_standard:
            s = word.span()[0]
            new_standard = start_standard
    return s