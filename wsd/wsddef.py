#!/usr/bin/python3
import spacy
import json
import requests
from pywsd.lesk import simple_lesk, cosine_lesk
from nltk.corpus import wordnet as wn
from oxforddictionaries.words import OxfordDictionaries
# load english dict
nlp = spacy.load('en')
#from espdict import espdict

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
        for item in indef['tuc']:
            try:
                #print("from glosbe:" +item['phrase']['text'] + " from text :" + token.text)
                if item['phrase']['text'] == token.text:
                    return token
            except:
                continue
    

def find_def(indef, lang, word):
    #have to change from iso standard
    if lang == 'eng':
        lang = 'en'
    if lang == 'spa':
        lang = 'es'
    if lang == 'arb':
        lang = 'ar'
    meaning = ""
    for tuc in indef['tuc']:
        try:
            if tuc['phrase']['text'] == word.text:
                esptemp = ""
                for m in tuc['meanings']:
                    if m['language'] == lang and len(m['text']) > len(meaning):
                        meaning = m['text']
        except KeyError:
            pass
    return meaning


def get_def(word, context, lang):
    #job = json.loads(injob.text)
    #lang = injob['language']
    #context = injob['context']
    #word = injob['word']
    #print("injob['language'] = " + lang)
    #print("injob['context'] = " + context)
    #print("injob['word'] = " + word)
    
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
    context = remove_notalpha(context)
    doc = nlp(context)
    if lang != 'eng':
        #call for translation to proper lang
        getstr = "https://glosbe.com/gapi/translate?from="+lang+"&dest=eng&format=json&phrase="+word+"&pretty=true"
        response = requests.get(getstr)
        indef = json.loads(response.text)
        word = find_token(indef, doc) 
    else:
        for token in doc: 
            if word == token.text:
                word = token
                break

    if word and word.is_stop: 
        if lang != 'eng':
            return find_def(indef, lang, word)
        else:
            o = OxfordDictionaries("0008ceae","e3319ad80adb64e830100bf675efba59")
            a = o.get_info_about_word(word.lemma_).json()
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
        if lang != 'eng': 
            #this should use the spa or arb word given 
            if len(indef['tuc']) > 0:
                meaning = find_def(indef, lang, word)
        else:
            # needs to look for beginning of sentence
            if (word.pos_ == 'PROPN'):
                meaning = word.text + " is a proper noun."
            elif answer:
                meaning = answer.definition()
        if meaning:
            return meaning
        else:
            return "Sorry, I don't know that definintion:("
    else:
        return "Sorry, I don't know that definition:(" 
