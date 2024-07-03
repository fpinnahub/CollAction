import xml.etree.ElementTree as ET

from xml.dom import minidom
from constants import TEXT_lIST
from utils import get_lemmas_from_text


def create_tei(text, lemmas):
    # Creazione della struttura base del documento TEI
    TEI = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    teiHeader = ET.SubElement(TEI, "teiHeader")
    fileDesc = ET.SubElement(teiHeader, "fileDesc")
    titleStmt = ET.SubElement(fileDesc, "titleStmt")
    title = ET.SubElement(titleStmt, "title")
    publicationStmt = ET.SubElement(fileDesc, "publicationStmt")
    sourceDesc = ET.SubElement(fileDesc, "sourceDesc")
    ET.SubElement(publicationStmt, "p")
    ET.SubElement(sourceDesc, "p")

    # Creazione della sezione <text>
    text_elem = ET.SubElement(TEI, "text", attrib={"xml:lang": "it"})
    body = ET.SubElement(text_elem, "body", attrib={"xml:lang": "it"})
    div = ET.SubElement(body, "div")

    # Creazione delle frasi <s> considerando punteggiatura e fine linea
    s = ET.SubElement(div, "s")

    for i, (word, lemma) in enumerate(zip(text, lemmas)):
        if word in [',', '.', '!', '?', ';', ':', "'"]:  # Punteggiatura
            w = ET.SubElement(s, "pc", attrib={
                "xml:id": f"w_{i}",
                "n": str(i)
            })
        else:
            w = ET.SubElement(s, "w", attrib={
                "xml:id": f"w_{i}",
                "n": str(i),
                "lemma": lemma
            })
        w.text = word

        # Aggiungere nuova frase (nuova linea)
        if word in ['.', '!', '?']:
            s = ET.SubElement(div, "s")

    # Funzione per generare una stringa XML formattata
    def prettify(elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="    ")

    # Stampa il documento XML formattato
    return prettify(TEI)


# Input
my_text = TEXT_lIST['inf_1']
my_lemmas = get_lemmas_from_text(my_text)

# Genera il file TEI
xml_ou = create_tei(my_text, my_lemmas)

with open('../../etc/my_xml_out.xml', 'w') as xml_out:
    xml_out.write(xml_ou)


# print(xml_ou)

# from pprint import pprint as pp
#
# pp(xml_ou)
