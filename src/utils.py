
from constants import PUNCT_SINGS, ETC_FOLDER, END_SENTENCE


def plain_text_from_split(txt):
    """Build a text from the list of words and punctuation signs"""

    my_txt = ' '.join(txt)
    for char in PUNCT_SINGS:
        my_txt = my_txt.replace(f' {char}', f'{char}')

    return my_txt


def get_spacy_lemmas_from_text(txt, lang_model='it_core_news_lg', **lang_model_params):
    """Given a text as a long string or as a list of words, get its lemmas. Only for Italian"""
    import spacy

    # loading spacy language model
    if 'disable' not in lang_model_params:
        lang_model_params['disable'] = ['parser', 'ner']
    nlp = spacy.load(lang_model, **lang_model_params)

    # checking and loading input
    if isinstance(txt, str):
        doc = nlp(txt)
    elif isinstance(txt, list):
        _txt = plain_text_from_split(txt)
        doc = nlp(_txt)
    else:

        raise TypeError('Text must be a string or a list of words')

    # getting the lemmas and words
    lemmas = []
    for token in doc:
        lemmas.append(
            {
                'word': token.text,
                'lemma': token.lemma_,
                'pos': token.pos_,
                'morph': token.morph.__str__(),
                'n': token.i,
                'sentence_start': token.is_sent_start,
                'sentence_end': token.is_sent_end,
                'punctuation': token.is_punct,
                'out_of_voc': token.is_oov,
                'title': token.is_title
            }
        )
    return lemmas


def split_string_text(txt):
    """Split string of text into list of words"""
    import re

    if not isinstance(txt, str):

        raise TypeError('A string of text must be given')

    w_list_with_space = re.split(r'(\W+)', txt)
    w_list = []
    for w in w_list_with_space:
        if w != ' ':
            w_list.append(w)

    return w_list


def get_tei_from_plain_text(
        txt, tei_file='xml-tei_out.xml', lemmas=None, lang_model=None, txt_lang='it',
        body_lang='it', **tei_tags
):
    """Given a string of text, it generates an XML-TEI from it"""
    import xml.etree.ElementTree as ET

    from xml.dom import minidom
    from os.path import normpath

    # inner function to format XML string in a human beautiful way
    def prettify(elem):
        rough_string = ET.tostring(elem, 'utf-8')
        re_parsed = minidom.parseString(rough_string)

        return re_parsed.toprettyxml(indent='    ')

    if not isinstance(txt, str):

        raise TypeError('A string of text must be given')

    # # words list
    # txt_w = split_string_text(txt)  # avoid this way, get it from spacy!

    out_tei = tei_file if normpath('/') in tei_file else f'{ETC_FOLDER}{tei_file}'

    # lemmatize, if not given lemmas
    if lemmas is None:
        # lemmas = get_lemmas_from_text(txt_w, lang_model)
        lemmas = get_spacy_lemmas_from_text(txt, lang_model) \
            if lang_model else get_spacy_lemmas_from_text(txt)

    # basic TEI file structure creation
    TEI = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    tei_header = ET.SubElement(TEI, 'teiHeader')
    file_desc = ET.SubElement(tei_header, 'fileDesc')
    title_stmt = ET.SubElement(file_desc, 'titleStmt')
    title = ET.SubElement(title_stmt, 'title')
    publication_stmt = ET.SubElement(file_desc, 'publicationStmt')
    source_desc = ET.SubElement(file_desc, 'sourceDesc')
    ET.SubElement(publication_stmt, 'p')
    ET.SubElement(source_desc, 'p')

    # creating the <text> section
    text_elem = ET.SubElement(TEI, 'text', attrib={'xml:lang': txt_lang})
    body = ET.SubElement(text_elem, "body", attrib={'xml:lang': body_lang})
    div = ET.SubElement(body, "div")

    # sentences <s> creation, taking into account punctuation and line-breaks (maybe!)
    s = ET.SubElement(div, 's')

    for lem in lemmas:
        word = lem['word']
        # line breaks (XML killing characters) management
        word = word.replace('\n', '{LB}')
        n = str(lem.get('n', -1))
        # if word in [',', '.', '!', '?', ';', ':', "'"]:  # punctuation
        if lem['punctuation']:
            pass
        w = ET.SubElement(s, "w", attrib={
            "xml:id": f"w_{n}",
            "n": n,
            "lemma": lem['lemma'].replace('\n', '{LB}'),
            'pos': lem.get('pos', 'empy'),
            'msd': lem.get('morph', 'empty')
        })
        w.text = word

        # adding new sentence (new line)
        if word in END_SENTENCE or lem['sentence_end']:
            s = ET.SubElement(div, "s")

    # saving in the right XML format
    with open(out_tei, 'w') as xml_out:
        xml_out.write(prettify(TEI))

