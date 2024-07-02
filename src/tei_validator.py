from lxml import etree


def validate(xml_path: str, xsd_path: str = '../dat/teiP5osis.2.5.0.xsd') -> bool:
    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)
    result = xmlschema.validate(xml_doc)

    return result


# from validator import validate
#

# if validate("path/to/file.xml", "path/to/scheme.xsd"):
if validate("../etc/my_xml_out.xml"):
    print('Valid! :)')
else:
    print('Not valid! :(')
