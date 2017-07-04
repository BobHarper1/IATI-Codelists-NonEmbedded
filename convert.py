from os.path import join

from lxml import etree as ET
import csv


"""

Converts codelist files from external sources into the format used by IATI.

Currently only supports the IANA Media Types code list (FileFormat).

"""

# Adapted from code at http://effbot.org/zone/element-lib.htm
def indent(elem, level=0, shift=2):
    i = "\n" + level*" "*shift
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " "*shift
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1, shift)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

template = ET.parse('templates/FileFormat.xml', ET.XMLParser(remove_blank_text=True))
codelist_items = template.find('codelist-items')

media_types = ET.parse('source/media-types.xml')
for registry in media_types.findall('{http://www.iana.org/assignments}registry'):
    registry_id = registry.attrib['id']
    for record in registry.findall('{http://www.iana.org/assignments}record'):
        codelist_item = ET.Element('codelist-item')

        code = ET.Element('code')
        code.text = registry_id + '/' + record.find('{http://www.iana.org/assignments}name').text
        codelist_item.append(code)

        category = ET.Element('category')
        category.text = registry_id
        codelist_item.append(category)

        codelist_items.append(codelist_item)

# template.write('xml/FileFormat.xml', encoding='UTF-8', pretty_print=True)

def source_to_xml(xml_name, source_name, csv_rows=None):
    tmpl_path = join('templates', '{}.xml'.format(xml_name))
    tmpl = ET.parse(tmpl_path, ET.XMLParser(remove_blank_text=True))
    codelist_items = tmpl.find('codelist-items')

    if not csv_rows:
        source_path = join('source', '{}.csv'.format(source_name))
        with open(source_path) as f:
            reader = csv.DictReader(f)
            csv_rows = [x for x in reader]

    for csv_row in csv_rows:
        codelist_item = ET.Element('codelist-item')

        code = ET.Element('code')
        code.text = csv_row['code']
        codelist_item.append(code)

        name = ET.Element('name')
        codelist_item.append(name)
        narrative = ET.Element('narrative')
        narrative.text = csv_row['name_en']
        name.append(narrative)
        narrative_fr = ET.Element('narrative', attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'fr'})
        narrative_fr.text = csv_row['name_fr']
        name.append(narrative_fr)
        codelist_item.append(name)

        if 'description_en' in csv_row:
            description = ET.Element('description')
            codelist_item.append(description)
            narrative = ET.Element('narrative')
            narrative.text = csv_row['description_en']
            description.append(narrative)
            narrative_fr = ET.Element('narrative', attrib={'{http://www.w3.org/XML/1998/namespace}lang': 'fr'})
            narrative_fr.text = csv_row['description_fr']
            description.append(narrative_fr)
            codelist_item.append(description)

        if 'category' in csv_row:
            category = ET.Element('category')
            category.text = csv_row['category']
            codelist_item.append(category)

        codelist_items.append(codelist_item)

    xml_path = join('xml', '{}.xml'.format(xml_name))
    tmpl.write(xml_path, encoding='UTF-8', pretty_print=True)

source_to_xml('AidType', 'dac_crs_aid_types')
source_to_xml('AidType-category', 'dac_crs_aid_type_categories')
source_to_xml('CollaborationType', 'dac_crs_collaboration_types')
source_to_xml('CRSChannelCode', 'dac_crs_channel_codes')
source_to_xml('FinanceType', 'dac_crs_finance_types')
source_to_xml('FinanceType-category', 'dac_crs_finance_type_categories')
source_to_xml('FlowType', 'dac_crs_flow_types')
source_to_xml('Region', 'dac_crs_regions')
source_to_xml('SectorCategory', 'dac_crs_sector_categories')

source_path = join('source', 'dac_crs_sectors.csv')
with open(source_path) as f:
    reader = csv.DictReader(f)
    sectors = []
    for sector in reader:
        if sector['voluntary_code'] != '':
            sector['code'] = sector['voluntary_code']
        sectors.append(sector)
sectors = sorted(sectors, key=lambda x: x['code'])
source_to_xml('Sector', 'dac_crs_sectors', csv_rows=sectors)
