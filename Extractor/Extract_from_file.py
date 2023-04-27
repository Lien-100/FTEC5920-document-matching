#==============
# This script go through a given folder and store the parsed result in to a csv
#==============
import extractTxt as et
import os
import io
import csv
from mainParser import ResumeParser

parsed_result={}
parsed_result['id'],parsed_result['name'],parsed_result['location'],parsed_result['organisations']=[],[],[],[]
parsed_result['education'],parsed_result['skills'],parsed_result['experience']=[],[],[]
for root, directories, filenames in os.walk('D:\FTEC5910\cvjd_parser\Step1_extract_from_file\data'):
    i: int = 1
    for filename in filenames:
        file = os.path.join(root, filename)
        if not isinstance(file, io.BytesIO):
            ext = os.path.splitext(file)[1].split('.')[1]
        else:
            ext = file.name.split('.')[1]
        ## to get the extention of the file
        raw_txt=et.extract_text(file,'.' + ext)
        parser = ResumeParser(raw_txt, skills_file=None)
        extracted_data = parser.get_extracted_data()
        parsed_result['id'].append(i)
        parsed_result['name'].append(extracted_data['name'])
        parsed_result['location'].append(", ".join(extracted_data['locations']) if extracted_data['locations'] else '')
        parsed_result['organisations'].append(", ".join(extracted_data['organisations']) if extracted_data['organisations'] else '')
        parsed_result['education'].append(", ".join(extracted_data['education']) if extracted_data['education'] else '')
        parsed_result['skills'].append(", ".join(extracted_data['skills']) if extracted_data['skills'] else '')
        parsed_result['experience'].append(extracted_data['experience'])
        i += 1

with open('parsed_result_from_folder.csv', mode='w', newline='',encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['ID', 'Name', 'Location', 'Organisations', 'Education', 'Skills', 'Experience'])

    for i in range(len(parsed_result['id'])):
        writer.writerow([
            parsed_result['id'][i],
            parsed_result['name'][i],
            parsed_result['location'][i],
            parsed_result['organisations'][i],
            parsed_result['education'][i],
            parsed_result['skills'][i],
            parsed_result['experience'][i]
        ])