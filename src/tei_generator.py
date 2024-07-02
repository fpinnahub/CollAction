import xml.etree.ElementTree as ET

from xml.dom import minidom


def create_tei(text, lemmas, ):
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

    # Creazione della frase <s>
    s = ET.SubElement(div, "s")

    # Iterazione sulle parole e sui lemmi per creare gli elementi <w>
    for i, (word, lemma) in enumerate(zip(text, lemmas)):
        w = ET.SubElement(s, "w", attrib={
            "xml:id": f"w_{i}",
            "n": str(i),
            "lemma": lemma
        })
        w.text = word

    # Funzione per generare una stringa XML formattata
    def prettify(elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="    ")

    # format and return
    return prettify(TEI)


# Input
lemmas = [
    'Artu',
    'je',
    'tu',
    'conoistre',
    'm',
    'm',
    'que1',
    'tu',
    'ne1',
    'faire',
    'je'
]

text = [
    'Artus',
    'je',
    'te',
    'conois',
    'mult',
    'miaus',
    'que',
    'tu',
    'ne',
    'fas',
    'moi'
]

# Genera il file TEI
xml_ou = create_tei(text, lemmas)

with open('../etc/my_xml_out.xml', 'w') as xml_out:
    xml_out.write(xml_ou)


# print(xml_ou)

# from pprint import pprint as pp
#
# pp(xml_ou)
