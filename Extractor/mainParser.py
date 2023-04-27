import sys
import spacy
#spacy.cli.download("en_core_web_sm")
from spacy.matcher import Matcher
import os
import re as r
import nltk
import pandas as pd
import constant as cs
import regexExtract as regEx
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import customModel as cm
from datetime import datetime
from dateutil import relativedelta
import csv

def extract_skills(nlp_text, noun_chunks, skills_file=None):
    """
    Helper function to extract skills from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param noun_chunks: noun chunks extracted from nlp text
    :return: list of skills extracted
    """
    tokens = [token.text for token in nlp_text if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(sys.argv[0]), 'skills.csv')
        )
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

def extract_education(nlp_text):
    '''
    Helper function to extract education from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :return: tuple of education degree and year if year if found
             else only returns education degree
    '''
    edu = []
    # Extract education degree
    try:
        for tex in nlp_text.split(' '):
            tex = r.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in cs.EDUCATION and tex not in cs.STOPWORDS:
                edu.append(tex)
    except IndexError:
        pass
    return edu

def get_total_experience(experience_list):
    '''
    Wrapper function to extract total months of experience from a resume
    :param experience_list: list of experience text extracted
    :return: total months of experience
    '''
    exp_ = []
    for line in experience_list:
        experience = r.search(
            r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present)',
            line,
            r.I
        )
        if experience:
            exp_.append(experience.groups())
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months


def get_number_of_months_from_dates(date1, date2):
    '''
    Helper function to extract total months of experience from a resume
    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    '''
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience


def extract_experience(resume_text):
    '''
    Helper function to extract experience from resume text

    :param resume_text: Plain resume text
    :return: list of experience
    '''
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # word tokenization
    word_tokens = nltk.word_tokenize(resume_text)

    # remove stop words and lemmatize
    filtered_sentence = [
            w for w in word_tokens if w not
            in stop_words and wordnet_lemmatizer.lemmatize(w)
            not in stop_words
        ]
    sent = nltk.pos_tag(filtered_sentence)

    # parse regex
    cp = nltk.RegexpParser('P: {<NNP>+}')
    cs = cp.parse(sent)

    # for i in cs.subtrees(filter=lambda x: x.label() == 'P'):
    #     print(i)

    test = []

    for vp in list(
        cs.subtrees(filter=lambda x: x.label() == 'P')
    ):
        test.append(" ".join([
            i[0] for i in vp.leaves()
            if len(vp.leaves()) >= 2])
        )

    # Search the word 'experience' in the chunk and
    # then print out the text after it
    x = [
        x[x.lower().index('experience') + 10:]
        for i, x in enumerate(test)
        if x and 'experience' in x.lower()
    ]
    return x

def extract_entity_sections(text):
    '''
    Helper function to extract all the raw text from sections of
    resume

    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    entities = {}
    key = False
    #wordnet_lemmatizer = WordNetLemmatizer()
    #stop_words = set(stopwords.words('english'))
    #the above two now is acutaully not in use. The improvement in performance related is unknown.
    #word_tokens = nltk.word_tokenize(text)
    word_tokens=text.split(' ')
    for phrase in word_tokens:
        if len(phrase) == 1:
            p_key = phrase.lower()
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities

def cleanResume(resumeText):
    resumeText = r.sub('httpS+s*', ' ', resumeText)  # remove URLs
    resumeText = r.sub('RT|cc', ' ', resumeText)  # remove RT and cc
    resumeText = r.sub('#S+', '', resumeText)  # remove hashtags
    resumeText = r.sub('@S+', '  ', resumeText)  # remove mentions
    resumeText = r.sub('[%s]' % r.escape("""!"#$%&'()*+,-./:;<=>?@[]^_`{|}~"""), ' ', resumeText)  # remove punctuations
    resumeText = r.sub(r'[^x00-x7f]',r' ', resumeText)
    resumeText = r.sub('s+', ' ', resumeText)  # remove extra whitespace
    resumeText = r.sub('[0-9]+', ' ', resumeText)
    return resumeText

class ResumeParser(object):
    def __init__(
            self,
            resume,
            skills_file=None,
            custom_regex=None
    ):
        nlp = spacy.load('en_core_web_sm')  # the name of the model pipeline
        # custom_nlp = spacy.load(os.path.dirname(os.path.abspath(__init__.py)))
        self.__skills_file = skills_file
        # self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name':None,
            'locations':None,
            'organisations':None,
            'education': None,
            'skills': None,
            'experience': None
        }
        self.__resume = resume
        '''
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        ## to get the extention of the file
        self.__text_raw = et.extract_text(self.__resume, '.' + ext)  #
        self.__text = ' '.join(self.__text_raw.split())  # long string
                '''
        #self.__text = cleanResume(self.__text)
        self.__text_raw=str(self.__resume)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        # self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)  # nltk model default noun chunks
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        cust_ent = cm.extract_entities_wih_custom_model(
            self.__nlp
        )
        skills = extract_skills(
            self.__nlp,
            self.__noun_chunks,
            self.__skills_file
        )
        self.__details['name'] = regEx.name_extractor(self.__nlp)
        self.__details['organisations'] = regEx.org_extractor(self.__nlp)
        self.__details['locations'] = regEx.loc_extractor(self.__nlp)
        entities = extract_entity_sections(self.__text)
        self.__details['skills'] = skills
        #edu = et.extract_education(
        #               [sent.string.strip() for sent in self.__nlp.sents]
        #       )
        edu = extract_education(
            self.__text
        )

        try:
            self.__details['experience'] = entities['experience']
            #try:
            #    exp = round(
            #       get_total_experience(entities['experience']) / 12,
            #       2
            #    )
            #    self.__details['total_experience'] = exp
            #except KeyError:
            #    self.__details['total_experience'] = 0

        except KeyError:
            self.__details['experience'] = 0
        try:
            self.__details['education'] = edu
                #entities['education']
        except KeyError:
            try:
                self.__details['education'] = cust_ent['Degree']
            except KeyError:
                self.__details['education'] = None
        return


def resume_result_wrapper(resume_csv_path, output_csv_path, skills_file= None):
    with open(resume_csv_path, 'r', encoding='latin1') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        results = []
        for row in enumerate(reader):
            resume_id = row[0]
            resume_text = row[1]
            parser = ResumeParser(resume_text, skills_file=skills_file)
            extracted_data = parser.get_extracted_data()
            name = extracted_data['name']
            locations = ", ".join(extracted_data['locations']) if extracted_data['locations'] else ''
            organisations = ", ".join(extracted_data['organisations']) if extracted_data['organisations'] else ''
            education = ", ".join(extracted_data['education']) if extracted_data['education'] else ''
            skills = ", ".join(extracted_data['skills']) if extracted_data['skills'] else ''
            experience = extracted_data['experience']
            results.append([resume_id, name, locations, organisations, education, skills, experience])

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['cvid', 'name', 'locations', 'organisations', 'education', 'skills', 'experience'])
        writer.writerows(results)
#====================================
# If only go through a csv to extract
#====================================
#resume_result_wrapper('D:\FTEC5910\cvjd_parser\cv_raw.csv','D:\FTEC5910\cvjd_parser\cv_with_section.csv')

