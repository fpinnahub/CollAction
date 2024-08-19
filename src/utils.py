
from src.constants import PUNCT_SINGS, ETC_FOLDER, END_SENTENCE, XML_NAMESPACE, XML_TAGS_FOR_LEMMAS


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

        raise TypeError('Text must be a string or a list of')

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




def dictfy_witness_text(txt, witness_name, lang_model=None, txt_lang='it'):
    """Get dictionary of lemmas from a plain text"""
    lemmas = get_spacy_lemmas_from_text(txt, lang_model) \
        if lang_model else get_spacy_lemmas_from_text(txt)

    witness = {
        "id": witness_name,
        "tokens": [
            {
                "form": lem['word'].replace('\n', 'LB'),
                "xml:id": f'w_{n}',
                "t": lem['lemma'].replace('\n', 'LB'),
                "pos": lem['pos'],
                "morph": lem['morph']
            } for n, lem in enumerate(lemmas)
        ]
    }

    return witness


def jsonfy_witnesses(json_out, witness_path_names, witness_names=None):
    """
    Get json from all witness texts
    :param json_out: str, json output file name
    :param witness_path_names: list, list of witness text file whole path
    :param witness_names; list (opt.), the list of witnesses names
    """
    import json
    from os.path import normpath

    witnesses = []
    for wit in witness_path_names:
        f_name = wit.split(normpath('/'))[-1].split('.')[0]
        with open(wit, 'r', encoding='utf-8') as w:
            witnesses.append(dictfy_witness_text(w.read(), f_name))

    with open(normpath(json_out), 'w', encoding='utf8') as jo:
        json.dump({'witnesses': witnesses}, jo, indent=2, ensure_ascii=False)

    return




# def table_to_xml(table):
#     """
#     Redefining a core collatex function to have other attributes
#     :param table: a collatex table
#     :return: an XML collated document, with all the attributes existing in the input
#     """
#     readings = []
#     for column in table.columns:
#         app = etree.Element('app')
#         for key, value in sorted(column.tokens_per_witness.items()):
#             child = etree.Element('rdg')
#             child.attrib['wit'] = "#" + key
#             child.text = "".join(str(item.token_data["form"]) for item in value)
#             # TODO: redéfinir pour accepter un nombre arbitraire d'éléments et faire ça proprement
#             # TODO: apparemment, aussi, il ne veut pas d'xml:id
#             child.attrib['id'] = "".join(str(item.token_data["xml:id"]) for item in value)
#             child.attrib['lemma'] = "".join(str(item.token_data["t"]) for item in value)
#             child.attrib['pos'] = "".join(str(item.token_data["pos"]) for item in value)
#             child.attrib['msd'] = "".join(str(item.token_data["morph"]) for item in value)
#             app.append(child)
#         # Without the encoding specification, outputs bytes instead of a string
#         result = etree.tostring(app, encoding="unicode")
#         readings.append(result)
#     return "<root>" + "".join(readings) + "</root>"



def collate_from_json(json_input, output_dir, seg=False):
    import json
    from os.path import normpath
    from collatex import collate, Collation
    from falcon.collation import table_to_xml

    with open(json_input, 'r', encoding='utf8') as ji:
        collation_material = json.load(ji)

    # alignment_table_html = collate(json_in, layout='vertical', output='html')

    if seg:
        collation =Collation()
        for w in collation_material['witnesses']:
            all_forms = ' '.join([d['form'] for d in w['tokens']])
            collation.add_plain_witness(w['id'], all_forms)
        collation_material = collation

    table = collate(collation_material, output="table", layout="vertical", segmentation=seg, near_match=not seg)
    xml_output = table_to_xml(table)

    # with open(normpath(output_dir) + "/coll" + "/out.html", 'w') as f:
    #     print(alignment_table_html, file=f)

    with open(normpath(output_dir) + "/coll" + "/out.xml", 'w') as f:
        print(xml_output, file=f)

    with open(normpath(output_dir) + "/coll" + "/out.table", 'w') as f:
        print(table, file=f)

    return

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


def parse_xml_file(file_path):
    from lxml import etree

    tree = etree.parse(file_path)
    root = tree.getroot()

    # load namespace from xml file
    _ns, _ns_key = root.tag[1:].split('}')
    # check namespace
    if _ns.lower() not in XML_NAMESPACE.values() or _ns_key.lower() not in XML_NAMESPACE:
        print('WARNING: unknown xml namespace')  # TODO: replace with real warning

    # dynamic XPath string creation
    xpath_query = \
        ".//tei:*[" + " or ".join(f"self::{key_tag}:{tag}" \
                                  for tag in XML_TAGS_FOR_LEMMAS \
                                  for key_tag in XML_NAMESPACE) + "]"

    tokens = []
    for w in root.xpath(xpath_query, namespaces=XML_NAMESPACE):
        token = {
            'form': w.text or '',
            'xml:id': f"{w.tag.split('}')[1]}_{w.get('n', '')}",
            't': w.get('lemma', ''),
            'pos': w.get('pos', ''),
            'morph': w.get('msd', '')
        }
        tokens.append(token)

    return tokens


def generate_json(xml_files):
    witnesses = []
    for i, file_path in enumerate(xml_files, 1):
        tokens = parse_xml_file(file_path)
        witness = {
          'id': f'inf_{i}',
          'tokens': tokens
        }
        witnesses.append(witness)

    json_data = {
        'witnesses': witnesses
    }

    return json_data


def convert_xml_to_json(xml_files, output_file):
    import json

    json_data = generate_json(xml_files)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
