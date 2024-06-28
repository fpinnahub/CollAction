import spacy


load_model = spacy.load('it_core_news_sm', disable=['parser', 'ner'])
my_text = 'i cretini sanno sempre tutto'
doc = load_model(my_text)
res = " ".join([token.lemma_ for token in doc])

print(res)
