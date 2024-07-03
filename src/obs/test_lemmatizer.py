import spacy

from constants import TEXT_lIST
from utils import plain_text_from_split


load_model = spacy.load('it_core_news_sm', disable=['parser', 'ner'])
# my_text = 'i cretini sanno sempre tutto'
# doc = load_model(my_text)
# res = " ".join([token.lemma_ for token in doc])

my_text = plain_text_from_split(TEXT_lIST['inf_1'])
doc = load_model(my_text)
my_lemmas = [token.lemma_ for token in doc]
res = " ".join(my_lemmas)

print(my_lemmas)
print(res)
