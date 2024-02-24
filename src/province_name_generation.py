import random

vowels  = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

def create_name(structure):
    for j in range(len(structure)):
        out = ""
        for i in range(len(structure)):
            if structure[i] == "Y":
                out += random.choice([random.choice(consonants),""])
            elif structure[i] == "A":
                out += random.choice([random.choice(consonants) + random.choice(vowels) + random.choice([random.choice(consonants),""]),""])
            elif structure[i] == "K":
                out += random.choice(consonants) + random.choice(vowels) + random.choice([random.choice(consonants),""])
            elif structure[i] == "L":
                out += random.choices(["", "land"], weights=[0.9, 0.1])[0]
            else:
                out += structure[i]
        return out.capitalize()