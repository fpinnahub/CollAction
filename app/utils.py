
from consts import PUNCT_SINGS, ETC_FOLDER, END_SENTENCE, XML_NAMESPACE, XML_TAGS_FOR_LEMMAS, \
LB_FORM, LB_LEMM, LB_CHAR, CAT_BKGRND_COL


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
        # let's fix a Spacy bug here (lemma for prop. names often are not
        # capitalized):
        if token.pos_ is 'PROPN' and token.text[0].isupper() and \
                not token.lemma_[0].isupper():
            lemma_fixed = token.lemma_.capitalize()
        elif token.pos_ is 'PROPN' and token.text[0].islower() and \
                token.lemma_[0].isupper():
            lemma_fixed = token.lemma_.lower()
        else:
            lemma_fixed = token.lemma_
        lemmas.append(
            {
                'word': token.text,
                'lemma': lemma_fixed,
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
                "form": lem['word'].replace('\n', LB_FORM),
                "xml:id": f'w_{n}',
                "t": lem['lemma'].replace('\n', LB_LEMM),
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


def table_to_xml(table):
    """
    Redefining a core collatex function to have other attributes
    :param table: a collatex table
    :return: an XML collated document, with all the attributes existing in the input
    """
    from lxml import etree

    readings = []
    for column in table.columns:
        app = etree.Element('app')
        for key, value in sorted(column.tokens_per_witness.items()):
            child = etree.Element('rdg')
            child.attrib['wit'] = "#" + key
            child.text = "".join(str(item.token_data["form"]) for item in value)
            # TODO: redéfinir pour accepter un nombre arbitraire d'éléments et faire ça proprement
            # TODO: apparemment, aussi, il ne veut pas d'xml:id
            child.attrib['id'] = "".join(str(item.token_data["xml:id"]) for item in value)
            child.attrib['lemma'] = "".join(str(item.token_data["t"]) for item in value)
            child.attrib['pos'] = "".join(str(item.token_data["pos"]) for item in value)
            child.attrib['msd'] = "".join(str(item.token_data["morph"]) for item in value)
            app.append(child)
        # Without the encoding specification, outputs bytes instead of a string
        result = etree.tostring(app, encoding="unicode", pretty_print=True)
        readings.append(result)
    return "<root>" + "".join(readings) + "</root>"


def all_equal(iterable):
    """Check if all elements in an iterable are equals"""
    from itertools import groupby

    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def get_rows_from_printed_table(table):
    """Returning the list of the table rows"""
    rows = []
    row_prev = ''
    for row in table.splitlines():
        if '+' in row:
            rows.append(row_prev)
            row_prev = ''
        elif row_prev:
            row_prev = '|'.join(
                [
                    f'{r_p.strip()} {r.strip()}'
                    for r_p, r in zip(
                        row_prev.split('|'),
                        row.strip("|").strip().split('|')
                    )
                ]
            )
        else:
            row_prev = str(row.strip("|").strip())
    rows = rows[2:]

    # rows form printed table
    return [[cell.strip() for cell in row.split("|")] for row in rows]


def remove_prefix(text, prefix):

    return text[len(prefix):] if text.startswith(prefix) else text


def remove_suffix(text, suffix):

    return text[:-len(suffix)] if suffix and text.endswith(suffix) else text


def table_to_html(collation, table, data):
    """Generate html collation table from plain text table"""

    """
    'table' is a print of the collation table made with lemmas; we want to 
    produce the same table in HTML, with forms in place of lemmas.
    We work cell by cell, getting each cell table form 'collation.columns', 
    taking each lemma in the cell from ??? and replacing it with corresponding 
    forms, that are stored in 'data'.
    Issues come from extra characters from lemma to form, like
    mon(do) <-> mon ( do ),
    and cases like these.
    
    The HTML table is build step-by-step as pieces of text appended into 'html'.
     
    """

    # bare HTML table
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
<table id='the-collation-table' border='1' cellspacing='0' cellpadding='5'>\n"""

    # get rows and cells
    rows_from_table = get_rows_from_printed_table(table)

    # witness names
    witness_id = [wit['id'] for wit in data['witnesses']]
    html += "  <tr>\n"

    # working row by row, we collect words info
    wit_num = len(witness_id)
    n = [0] * wit_num           # to count the words in each cell
    lemmas = [''] * wit_num
    poss = [''] * wit_num
    morphs = [''] * wit_num
    forms = [''] * wit_num

    # setting the HTML table header
    for w_id in witness_id:
        html += f"""    <td style="text-align: center;">
        <span style="font-weight:bold;font-size:xx-large;">{w_id.strip()}</span>
        </td>\n"""
    html += f"""    <td style="text-align: center;">
            <span style="font-style:italic;font-size:x-large;">category</span>
            </td>\n"""
    html += f"""    <td style="text-align: center;">
                <span style="font-style:italic;font-size:x-large;">notes</span>
                </td>\n"""
    html += "  </tr>\n"

    debug_n = 0

    # extracting witnesses' info from data
    witness_datas = tuple(
        next(
            w['tokens'] for w in data["witnesses"] if w["id"] == wit_name
        ) for wit_name in witness_id
    )

    # rows from collation object
    # (we get rows also from collation table to double-check; mind that
    # collation table seems transposed, so we point at collation.columns)
    tech_obj = type('TechClass', (object,), {'token_string': ''})()
    rows_from_collation = [
        [' '.join(
            [
                tok.token_string
                for tok in row.tokens_per_witness.get(w_name, [tech_obj])
            ]
        ) for w_name in witness_id]
        for row in collation.columns
    ]

    # check length
    if len(rows_from_collation) != len(rows_from_table):

        raise AssertionError(
            'Collation and printed table have different length'
        )

    # check alignment
    for r in range(len(rows_from_table)):
        for w in range(wit_num):
            if not rows_from_collation[r][w]:

                continue
            if rows_from_table[r][w] != rows_from_collation[r][w]:

                # debug
                print(f'table: {rows_from_table[r][w]}\ncollation: {rows_from_collation[r][w]}')

                # correction:
                # we expect that from collation we got more spaces, nothing more
                if (rows_from_collation[r][w].replace(' ', '') ==
                        rows_from_table[r][w].replace(' ', '')):
                    rows_from_collation[r][w] = rows_from_table[r][w]
                else:

                    raise ValueError('Bad parsing value in collation table')

    # row-by-row and cell-by-cell, build the HTML table
    ri = 0
    for row in collation.columns:
        cells = rows_from_collation[ri]
        ri += 1

        variant = row.variant

        # check if just punctuation variation, and set cell background color
        # depending on the case
        just_punct = False
        if variant and all(c in PUNCT_SINGS + ['-'] for c in cells):
            bkgrnd_col = """style=\"background-color:peru;\""""
            just_punct = not just_punct
        else:
            bkgrnd_col = """style=\"background-color:red;\"""" \
                if variant else """style=\"background-color:rgba(0, 0, 0, 0);\""""
        notes_bkgrnd_col = """style=\"background-color:beige;\"""" \
            if variant else """style=\"background-color:bisque;\""""

        # check starting linebreaks (we will remove for better rendering)
        start_with_linebreak = True if all(c.startswith(LB_LEMM)
                                           for c in cells) else False

        html += "  <tr>\n"
        for ci, cell in enumerate(cells):   # 'ci' stands for cell index

            debug_n += 1

            # collect all token info for the cell
            witness_data = witness_datas[ci]

            # empty cell case
            if cell == '':
                html += f"    <td {bkgrnd_col}>-</td>\n"

                continue
            cell_html = ""

            # consume the cell words
            cell_remainder = str(cell)      # remainder should be empty when
            #                               # all words are consumed
            stay = True
            while n[ci] < len(witness_data) and cell_remainder.strip() and stay:

                debug_n += 1

                token = witness_data[n[ci]]
                form, pos, morph, lemma = \
                    token['form'], token['pos'], token['morph'], token['t']

                # lemma-by-lemma, recover its form, caring for variants

                # Workaround for Collation misbehaviour:
                # sometimes rows like these happens
                # |prestame(|prestame(|
                # |n)te     |nte )    |
                # where the lemma begins in a cell and ends in the cell below.
                # We are going to check if the lemma stand across the cells,
                # remove its tail form the lower cell and replace the form in
                # the upper.
                if lemma not in cell_remainder:
                    if f'{cell_remainder}{rows_from_collation[ri][ci]}'.startswith(lemma):
                        remainder = lemma[len(cell_remainder):]
                        rows_from_collation[ri][ci] = rows_from_collation[ri][ci].replace(remainder, '')
                        cell_remainder = ''
                    else:
                        # this is the case of some orphan string,
                        # without a corresponding lemma
                        stay = False

                        continue

                cell_remainder = cell_remainder.replace(lemma, '', 1)

                if variant:     # store value in list for further actions
                    lemmas[ci] += f'{lemma}¬'
                    poss[ci] += f'{pos}¬'
                    morphs[ci] += f'{morph}¬'
                forms[ci] += f'{form}¬'
                tooltip = f"LEM: {lemma}\nPOS: {pos}\nMorph: {morph}" if \
                    pos not in {'PUNCT', 'SPACE'} else ""
                cell_html += f'<span title="{tooltip}">{form}</span> '
                n[ci] += 1
            else:   # all words in the cell are now consumed
                if start_with_linebreak:
                    cell_html = cell_html.replace(LB_FORM, ' ', 1)

                if len(cell_remainder.strip()):     # this should not happen

                    try:

                        if cell.index(inner_trim(cell_remainder)) < \
                                cell.index(cell.replace(inner_trim(cell_remainder), '')):
                            cell_html = f'<span title="UNKNOWN">{cell_remainder}</span> {cell_html}'
                        else:
                            cell_html += f'<span title="UNKNOWN">{cell_remainder}</span> '

                    except:
                        print('ma come?')

                ### STRANGE --> see
                if n[ci] < len(witness_data) and cell in witness_data[n[ci]]['t']:
                    n[ci] += 1
                    if witness_data[n[ci]]['pos'] == 'SPACE':
                        witness_data[n[ci]]['t'] = ' '

                # remove go-to-line HTML char
                if variant:
                    if lemmas[ci]:
                        lemmas[ci] = lemmas[ci][:-1]
                    if poss[ci]:
                        poss[ci] = poss[ci][:-1]
                    if morphs[ci]:
                        morphs[ci] = morphs[ci][:-1]
                if forms[ci]:
                    forms[ci] = forms[ci][:-1]

            html += f"    <td  class=\"witness-cell\" {bkgrnd_col}>{cell_html.strip()}</td>\n"



        # guess the category
        if variant:
            # if forms have same @lemma, @pos and @msd => diffGraph
            if all_equal(lemmas) and all_equal(poss) and all_equal(morphs):
                variation_cat = "graphematic"
            # if forms have same @lemma, @pos, but different @msd > diffMorph
            elif all_equal(lemmas) and all_equal(poss):
                variation_cat = "flexional"
            # if forms have same @lemma, but different @pos and @msd > diffPos
            elif all_equal(lemmas):
                variation_cat = "morphosyntactic"
            elif just_punct:
                variation_cat = "punctuation"
            # if lemmas differ but forms don't
            elif all_equal(forms):
                variation_cat = "homographic interpretative"
            else:
                variation_cat = "lexical"

            # write the category
            html += f"    <td {CAT_BKGRND_COL[variation_cat]}>{variation_cat}</td>\n"

            # reset category vars
            lemmas = [''] * wit_num
            poss = [''] * wit_num
            morphs = [''] * wit_num
        elif all_equal(lemmas) and all_equal(poss) and all_equal(morphs) and not all_equal(forms):
            html += f"    <td {CAT_BKGRND_COL['graphematic']}>graphematic</td>\n"
        else:
            # empty cell for category
            html += f"    <td {bkgrnd_col}></td>\n"

        forms = [''] * wit_num
        # editable notes' cell
        html += f'    <td contenteditable="true" class="notes-cell" {notes_bkgrnd_col}></td>\n'

        html += "  </tr>\n"





    html += "</table>"

    # LB to linebreaks
    html = html.replace(LB_FORM, LB_CHAR)

    return html


def inner_trim(string):
    """Recursively replace double spaces with one"""
    while '  ' in string:
        string = string.replace('  ', ' ')

    return string


def collation_html_from_dict(dict_input, seg=True, coll_by_lemmas=True):
    """
    HTML collation table given lemmatized witnesses dict
    :param dict_input: str
    :param seg: bool (opt.), collate with segmentation
    :param coll_by_lemmas: bool (opt,), collate by lemmas or by forms
    """
    from collatex import collate, Collation

    # segmentation
    if seg:
        collation = Collation()
        for w in dict_input['witnesses']:
            if coll_by_lemmas:
                all_lemmas = ' '.join([d['t'] for d in w['tokens']])
                collation.add_plain_witness(w['id'], all_lemmas)
            else:
                all_forms = ' '.join([d['form'] for d in w['tokens']])
                collation.add_plain_witness(w['id'], all_forms)
        collation_material = collation
    else:
        collation_material = dict_input

    # generate output
    table = collate(
        collation_material, output="table", layout="vertical", segmentation=seg, near_match=not seg
    )

    return table_to_html(table, table.__str__(), dict_input)


def collate_from_json(json_input, output_dir, seg=False, coll_by_lemmas=True):
    """

    :param json_input: str
    :param output_dir: str
    :param seg: bool (opt.), collate with segmentation
    :param coll_by_lemmas: bool (opt,), collate by lemmas or by forms
    """
    import json
    from os.path import normpath
    from collatex import collate, Collation

    # load witnesses
    with open(json_input, 'r', encoding='utf8') as ji:
        collation_material_json = json.load(ji)

    # segmentation
    if seg:
        collation = Collation()
        for w in collation_material_json['witnesses']:
            if coll_by_lemmas:
                all_lemmas = ' '.join([d['t'] for d in w['tokens']])
                collation.add_plain_witness(w['id'], all_lemmas)
            else:
                all_forms = ' '.join([d['form'] for d in w['tokens']])
                collation.add_plain_witness(w['id'], all_forms)
        collation_material = collation
    else:
        collation_material = collation_material_json

    # generate output
    table = collate(
        collation_material, output="table", layout="vertical", segmentation=seg, near_match=not seg
    )
    tei_output = collate(
        collation_material, output="tei", layout="vertical", segmentation=seg, near_match=not seg,
        indent=True
    )
    xml_output = table_to_xml(table) if not seg else collate(collation_material, output='xml', indent=True)
    html_table = table_to_html(table, table.__str__(), collation_material_json)

    # writing output files
    with open(normpath(output_dir) + "/coll" + "/out.html", 'w', encoding='utf8') as f:
        print(html_table, file=f)

    with open(normpath(output_dir) + "/coll" + "/out.xml", 'w', encoding='utf8') as f:
        print(xml_output, file=f)

    with open(normpath(output_dir) + "/coll" + "/out_tei.xml", 'w', encoding='utf8') as f:
        print(tei_output, file=f)

    with open(normpath(output_dir) + "/coll" + "/out.table", 'w', encoding='utf8') as f:
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

    # lemmatize, if lemmas not given
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
