# Импорты библиотек обязательно.
#!pip install yargy
#!pip install natasha
from yargy import Parser, rule, and_, not_
from yargy.interpretation import fact
from yargy.predicates import gram
from yargy.relations import gnc_relation
from yargy.pipelines import morph_pipeline

from natasha import (
    Segmenter,
    MorphVocab,

    NewsEmbedding,
    NewsMorphTagger,
    NewsNERTagger,

    PER,
    NamesExtractor,


    Doc

)


import re
import pandas as pd
data = pd.read_csv(
    'https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1boACz8ab9UytCpi0QhTUFRyS2oyH1MXS')

dikt = []
for i in data['dlg_id'].unique():
    text = data.query("dlg_id==@i and role=='manager'")['text'].tolist()
    dikt.append(text)

# Достаем имя мененджера.


def extract_name(str):
    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    text = str
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)
    doc.tag_morph(morph_tagger)

    matches = names_extractor(text)
    facts = [_.fact.as_json for _ in matches]
    for i in facts:
        if i.get("first"):
            return i.get("first")


def extract_name_for(dikt):
    for i in dikt:
        if extract_name(i):
            return [extract_name(i), i]

# Приветствие


def is_part_in_list(str_):
    words = ['привет', 'здравствуйте', 'доброе утро',
             'добрый день', 'добрый вечер', 'доброй ночи']
    for word in words:
        if word.lower() in str_.lower():
            return str_


def extract_hi(dikt):
    for i in dikt:
        if is_part_in_list(i):
            return i
# Прощание


def is_part_in_list_bue(str_):
    words = ['досвидания', 'пака', 'до свидания', 'удачи',
             'всего хорошего', 'до связи', 'доброй ночи', 'давайте', 'все хорошо']
    for word in words:
        if word.lower() in str_.lower():
            return str_


def extract_bue(dikt):
    for i in reversed(dikt):
        if is_part_in_list_bue(i):
            return i
# Название компании


def is_comp_in_list(str_):
    s = str_
    match = re.findall(r'компания.*бизнес', s)
    return " ".join(match)


def extract_comapany(dikt):
    for i in dikt:
        if is_comp_in_list(i):
            return is_comp_in_list(i)

# Обходим базу


def daalog_parse(dialog):
    name = extract_name_for(dialog)[0]
    name_company = extract_comapany(dialog)
    hi = extract_name_for(dialog)[1]
    baye = extract_bue(dialog)
    manager_loyalty = True
    if hi == None or baye == None:
        manager_loyalty = False
    return {'manager': name, 'name_company': name_company, 'hi': hi, 'baye': baye, 'manager_loyalty': manager_loyalty}


# dialog_parse_mass  Вернет массив объектов согласно заданию.
# Каждый объект.
# manager: Менеджер
# name_company: Имя компании, если нет в диалоге None.
# hi : менеджер здоровается или нет.
# baye: Менеджер прощается или нет.
# manager_loyalty : менеджер поздаровался и попрощался или нет.
def dialog_parse_mass(dikt):
    dialog_parse_mass = []
    for dialog in dikt:
        dialog_parse_mass.append(daalog_parse(dialog))
    return dialog_parse_mass


# Проверим как работает :)
print(*dialog_parse_mass(dikt), sep='\n')
