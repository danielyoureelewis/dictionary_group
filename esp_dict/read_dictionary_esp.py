#!/usr/bin/python3
import re
from collections import defaultdict
import copy


def remove_endl(line):
    result = ""
    for ch in line:
        if ch != '\n' and ch != '\r':
            result += ch
    return result


def main():
    with open("RealAcademiaEspanola-DiccionarioLlengueaEspanola.txt",
              encoding='UTF-8') as f:
        espDict = defaultdict(list)
        p_of_speech = [
                "m.", "verb.", "adj.", "V.",
                "f.", "var.", "abbr.", "prefix.",
                "colloq.", "symb.", "adv.", "naut.",
                "prep.", "mus.", "int.", "comb.",
                "predic.", "aeron.", "contr.", "slg.",
                "chem.", "attrib.", "ist.", "conj.",
                "pron.", "past.", "usu.", "biol.",
                "derog.", "esp.", "vulg.", "pastpart.",
                "coarseslg.", "unst.", "can.", "noun."
                ]
        part_of_speech = frozenset(p_of_speech)
        dicstr = f.read()
        defs = []
        entries = []
        perword = defaultdict(list)
        entries = dicstr.split('>')
        for entry in entries:
            pala, sep, definition = entry.partition('.')
            front, sep, definition = definition.partition('1.')
            definition = sep + definition
            regex = re.compile(r'(\d+. )')
            defs = regex.split(definition)
            for d in defs:
                words = d.split()
                for word in words[0:3]:
                    if word in part_of_speech:
                        perword[word[:-1]].append(remove_endl(d))
            espDict[pala] = copy.deepcopy(perword)
            perword.clear()
    print(espDict)


main()
