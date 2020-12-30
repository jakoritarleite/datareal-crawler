from __future__ import annotations

from re import findall
from lxml import etree
from io import StringIO

categories = {
    'Types': ['Apartamentos', 'Casas', 'Comércios', 'Sobrados', 'Galpões', 'Terrenos', 'Salas', 'Lofts'],
    'Apartamentos': ['apartamento', 'apto', 'giardino', 'garden', 'cobertura'],
    'Casas': ['casa', 'residência', 'residencia'],
    'Comércios': ['ponto', 'empreendimento'],
    'Sobrados': ['sobrado', 'geminado'],
    'Galpões': ['galpão', 'galpao'],
    'Terrenos': ['terreno', 'área', 'area', 'rural'],
    'Salas': ['sala'],
    'Lofts': ['loft']
}

formated = None

def regex_int(content: str, group: bool = True, index=0):
    content_sio = StringIO(content)
    try:
        parser = etree.parse(content_sio)

        if content_parsed := parser.xpath('//*/text()'):
            if len(content_parsed) > 1:
                for i in range(len(content_parsed)):
                    if content_integer := findall(r'\d+', content_parsed[i]):
                        if group:
                            content_parsed = ''.join(content_integer[j] for j in range(len(content_integer)) if content_integer[i] != '00')

                        else:
                            content_parsed = content_integer[index]
            
                return content_parsed
            
            else:
                if content_integer := findall(r'\d+', content_parsed[0]):
                    if group:
                        content_parsed = ''.join(content_integer[j] for j in range(len(content_integer)) if content_integer[0] != '00')

                    else:
                        content_parsed = content_integer[index]
            
                return content_parsed

        else:
            return content

    except Exception:
        if content_parsed := findall('\d+', content):
            if (content_integer := content_parsed) and (len(content_parsed) > 1):
                if group:
                    content_parsed = ''.join(content_integer[i] for i in range(len(content_integer)) if content_integer[i] != '00')

                else:
                    content_parsed = content_integer[index]

                return content_parsed

            else:
                return content_parsed[0]

        else:
            return content

def cleaner(content: str) -> Clean[Content]:
    formated = content.strip()
    formated = formated.replace('\t', '')
    formated = formated.replace('\r', '')
    formated = formated.replace('\n', '')

    return formated

def title(content: str) -> Clean[Title]:
    formated = cleaner(content)

    return formated

def price(content: str) -> Clean[Price]:
    if formated := regex_int(content):
        return formated

def rooms(content: str) -> Clean[Rooms]:
    formated = cleaner(content)

    if formated := regex_int(formated, False):
        formated = formated

    return formated

def suites(content: str) -> Clean[Suites]:
    formated = cleaner(content)

    if formated := regex_int(formated, False, 1):
        formated = formated

    return formated

def bathrooms(content: str) -> Clean[Bathrooms]:
    formated = cleaner(content)

    return formated

def body(content: str) -> Clean[Body]:
    formated = cleaner(content)

    return formated

def category(content: str) -> Clean[Category]:
    formated = cleaner(content.lower())

    for i in range(len(categories['Types'])):
        for j in range(len(categories[categories['Types'][i]])):
            if categories[categories['Types'][i]][j] in formated:
                formated = categories['Types'][i]

    return formated

def features(content: list) -> Clean[Features]:
    formated = list()
    for feature in content:
        if feature.strip():
            formated.append(cleaner(feature))

    return formated

def garages(content: str) -> Clean[Garages]:
    formated = cleaner(content)

    if formated_cleansed := findall(r'\d+', formated):
        formated_cleansed = ''.join(formated_cleansed[i] for i in range(len(formated_cleansed)))

        try:
            return int(formated_cleansed)

        except Exception:
            pass

    elif not findall(r'\d+', formated):
        if 'garage' in formated:
            formated_cleansed = '1'

            try:
                return int(formated_cleansed)

            except Exception:
                pass

    return formated

def total_area(content: str) -> Clean[TotalArea]:
    formated = cleaner(content)

    if formated := regex_int(formated):
        formated = formated

    return formated

def ground_area(content: str) -> Clean[GroundArea]:
    formated = cleaner(content)

    if formated := regex_int(formated):
        formated = formated

    return formated

def privative_area(content: str) -> Clean[PrivativeArea]:
    formated = cleaner(content)

    if formated := regex_int(formated):
        formated = formated

    return formated