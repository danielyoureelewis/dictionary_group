#!/usr/bin/python3
import spacy
import json
import requests
from pywsd.lesk import simple_lesk, cosine_lesk
from nltk.corpus import wordnet as wn
from oxforddictionaries.words import OxfordDictionaries
from nltk.stem.snowball import SnowballStemmer
# load english dict
nlp = spacy.load('en')
o = OxfordDictionaries("0008ceae","e3319ad80adb64e830100bf675efba59")
slp = spacy.load('es')

def remove_notalpha(line):
    line = line.replace('\n', ' ')
    result = ''.join([i for i in line if i.isalpha() or i == ' ' or i == '\n'])
    return result


def pos_convert(pos):
    pos_dict = {'NOUN': 'n', 'VERB': 'v', 'ADJ': 'a'}
    try:
        return pos_dict[pos]
    except Exception:
        return 'n'


def check_def(context, definition):
    definition = nlp(definition)
    pnt = 100/len(definition)
    score = 0
    context.split()
    for word in definition:
        if not word.is_stop and word.text in context:
            score = score + pnt
    return score


def find_token(indef, doc):
    for token in doc:
        print("find token token.text = " + token.lemma_)
        for item in indef['tuc']:
            try:
                #print("from glosbe:" +item['phrase']['text'] + " from text :" + token.text)
                if item['phrase']['text'] == token.text:
                    return token
            except:
                continue
    

def find_def(indef, lang, word):
    #have to change from iso standard
    text = word.text
    print("text is " + text)
    if lang == 'eng':
        lang = 'en'
    if lang == 'spa':
        lang = 'es'
    if lang == 'arb':
        lang = 'ar'
    if lang == 'fra':
        lang = 'fr'
    meaning = ""
    for tuc in indef['tuc']:
        try:
            if tuc['phrase']['text'] == word.lemma_:
                esptemp = ""
                for m in tuc['meanings']:
                    if m['language'] == lang and len(m['text']) > len(meaning):
                        meaning = m['text']
        except KeyError:
            pass
    return meaning


def get_def(injob):
    lang = injob['language']
    context = injob['context'].lower()
    word = injob['word'].lower()
    
    #print(u"injob['language'] = " + lang)
    #print(u"injob['context'] = " + context)
    print(u"injob['word'] = " + word)
    
    # make proper names into iso standard
    if lang == 'English':
        lang = 'eng'
    if lang == 'Spanish':
        lang = 'spa'
    if lang == 'Arabic':
        lang = 'arb'
    if lang == 'French':
        lang = 'fra'

    # remove non alphanumeric chars
    #context = remove_notalpha(context)

    doc = nlp(context)

    if lang != 'eng':
        stoken = slp(word)
        for token in stoken:
            print(token.lemma_)
            word = token.lemma_.lower()
        print(word)
        #call for translation to proper lang
        getstr = "https://glosbe.com/gapi/translate?from="+lang+"&dest=eng&format=json&phrase="+word+"&pretty=true"
        response = requests.get(getstr)
        print(response)
        indef = json.loads(response.text)
        print(indef)
        word = find_token(indef, doc)
        print(type(word))
    else:
        for token in doc: 
            #print(word + " " + token.text)
            if word == token.text:
                word = token
                break
    
    if word and word.is_stop or word.text == 'I': 
        if lang != 'eng':
            return find_def(indef, lang, word)
        else:
            if word.text == 'I':
                response = "Singular first person pronoun."
            else:
                try:
                    a = o.get_info_about_word(word.lemma_).json()
                except:
                    a = o.get_info_about_word(word.text).json()
                response = a['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
            return response

    if word:
        # do two seperate lesks 
        answer = simple_lesk(context, word.text, 
                            pos_convert(word.pos_))
        cosans = cosine_lesk(context, word.text, 
                            pos_convert(word.pos_))

        # find what we hope is the better answer
        if(check_def(context, cosans.definition()) >
           check_def(context, answer.definition())):
            answer = cosans

        sense = str(answer)
        sense = sense.split("'")[1].split(".")

        if ((sense[0] != word.lemma_ or
             int(sense[2]) > 4) and word.pos_ != 'PROPN'):
            try:
                answer = wn.synset(word.lemma_ + '.' +
                                   pos_convert(word.pos_) +
                                   '.01')
            except Exception:
                pass

        if (word.pos_ == 'PROPN'):
            meaning = word.text + " is a proper noun."
        elif lang != 'eng' and len(indef['tuc']) > 0: 
            #this should use the spa or arb word given 
            meaning = find_def(indef, lang, word)
        elif answer:
            meaning = answer.definition()

        if meaning:
            print("meaning: " + meaning)
            return meaning
        elif lang == 'eng':
            return "Sorry, I don't know that definintion:("
        elif lang == 'spa':
            return "Lo siento, no sé esa definición:("
    elif lang == 'eng':
        return "Sorry, I don't know that definintion:("
    elif lang == 'spa':
        return "Lo siento, no sé esa definición:("
