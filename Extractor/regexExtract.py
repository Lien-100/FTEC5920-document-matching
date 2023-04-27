##This script contain some fucntion used for extract specific detail sections
import logging
import re as r
def term_match(string_to_search, term):
    """
    A utility function which return the first match to the `regex_pattern` in the `string_to_search`
    :param string_to_search: A string which may or may not contain the term.
    :type string_to_search: str
    :param term: The term to search for the number of occurrences for
    :type term: str
    :return: The first match of the `regex_pattern` in the `string_to_search`
    :rtype: str
    """
    try:
        regular_expression = r.compile(term, r.I)
        result = r.findall(regular_expression, string_to_search)
        if len(result) > 0:
            return result[0] ##return the first matched result
        else:
            return None
    except Exception:
        logging.error('Error occurred during regex search')
        return None

def name_extractor(input_string):

    doc = input_string

    # Extract entities
    doc_entities = doc.ents

    # Subset to person type entities
    doc_persons = filter(lambda x: x.label_ == 'PERSON', doc_entities)
    doc_persons = filter(lambda x: len(x.text.strip().split()) >= 2, doc_persons)
    doc_persons = map(lambda x: x.text.strip(), doc_persons)
    doc_persons = list(doc_persons)

    # Assuming that the first Person entity with more than two tokens is the candidate's name
    if len(doc_persons) > 0:
        return [doc_persons[i] for i in range(len(doc_persons))]
    return None

def org_extractor(input_string):

    doc = input_string

    # Extract entities
    doc_entities = doc.ents

    # Subset to person type entities
    doc_persons = filter(lambda x: x.label_ == 'ORG', doc_entities)
    doc_persons = filter(lambda x: len(x.text.strip().split()) >= 2, doc_persons)
    doc_persons = map(lambda x: x.text.strip(), doc_persons)
    doc_persons = list(doc_persons)

    # Assuming that the first Person entity with more than two tokens is the candidate's name
    if len(doc_persons) > 0:
        return [doc_persons[i] for i in range(len(doc_persons))]
    return None

def loc_extractor(input_string):

    doc = input_string

    # Extract entities
    doc_entities = doc.ents

    # Subset to person type entities
    doc_persons = filter(lambda x: x.label_ == 'GPE', doc_entities)
    doc_persons = filter(lambda x: len(x.text.strip().split()) >= 2, doc_persons)
    doc_persons = map(lambda x: x.text.strip(), doc_persons)
    doc_persons = list(doc_persons)

    # Assuming that the first Person entity with more than two tokens is the candidate's name
    if len(doc_persons) > 0:
        return [doc_persons[i] for i in range(len(doc_persons))]
    return None