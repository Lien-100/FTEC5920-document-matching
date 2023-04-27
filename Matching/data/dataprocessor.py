#!/usr/bin/env python  
#-*- coding:utf-8 _*-  
""" 
@author:watercow 
@license: Apache Licence 
@file: dataprocessor.py
@site:  
@software: PyCharm
"""
import csv
import os
import re
import json
from tqdm import tqdm
import networkx

def JD_segmentor(jd_content):
    '''
    :return: <list>
    '''
    pattern = re.compile(r'\d+[.]')
    req_list = re.split(pattern, jd_content)
    return req_list

class AliDataProcessor:
    def __init__(self, dataDir):
        self.user_file = os.path.join(dataDir, 'cvjd_parser/cv_raw.csv')
        self.jd_file = os.path.join(dataDir, 'cvjd_parser/JdCleanNew.csv')
        self.action_file = os.path.join(dataDir, '5920/action.csv')
        #self.browse_pair = self._generate_pair(mode='browsed') # list
        self.deliver_pair = self._generate_pair(mode='delivered') # list
        self.satisfied_pair = self._generate_pair(mode='satisfied') # list
        self.user_dict = self._generate_dict(mode='user') # {'user_id': [...,...,...], ...}
        self.jd_dict = self._generate_dict(mode='jd') # {'jd_id': [...,...,...], ...}
        # user_luqu_dict:表示当前user_id已经有了几个jd的offer {'user_id':['jd_id1','jd_id2',...],...}
        self.user_luqu_dict = self._generate_basicgraph_list(mode='user')
        # jd_luqu_dict:表示当前jd_id对哪几个user比较满意 {'jd_id':['user_id1','user_id2',...]}
        self.jd_luqu_dict = self._generate_basicgraph_list(mode='jd')
        # user_nothired_dict:表示当前user_id投递但没有被录取的jd {'user_id':['jd_id1','jd_id2',...],...}
        self.user_nothired_dict = self._generate_basicgraph_list(mode='user', pair='deliver')
        # jd_luqu_dict:表示当前对jd进行投递但没被录取的user {'jd_id':['user_id1','user_id2',...]}
        self.jd_nothired_dict = self._generate_basicgraph_list(mode='jd', pair='deliver')

    # =======Step 1 part========
    def _generate_pair(self, mode='satisfied'):
        res_list = []
        with open(self.action_file, 'r') as f:
            reader = csv.reader(f)
            ##header: user_id, jd_id, satisfied, dilicered
            for line in reader:
                action_list = '\t'.join(line).strip().split('\t')
                user_id = action_list[0]
                jd_no = action_list[1]
                #browsed = action_list[2]
                delivered = action_list[3]
                satisfied = action_list[2]

                if mode == 'satisfied':
                    if satisfied == '1':
                        res_list.append((user_id, jd_no))
                elif mode == 'delivered':
                    if delivered == '1' and satisfied == '0':
                        res_list.append((user_id, jd_no))
                    '''
            elif mode == 'browsed':
                if browsed == '1' and delivered == '0':
                    res_list.append((user_id, jd_no))
                    '''
        return res_list

    def _generate_dict(self, mode='user'):
        res_dict = {}
        # mode in [user, jd]

        if mode == 'user':
            with open(self.user_file, 'r') as f:
                reader = csv.reader(f)
                print('[user mode ...]')
                #header: cvnewid, cv
                for line in tqdm(reader):
                    #user_list = line.replace('\n', '').split('\t')
                    user_id = line[0]
                    if user_id in res_dict:
                        break
                    else:
                        res_dict[user_id] = []
                    ## Here only one entry is included, can have more in future
                    experience = line[1]
                    experience_list = experience.split('\n')
                    for i in experience_list:
                        res_dict[user_id].append(i)

        else: # mode == 'jd'
            with open(self.jd_file, 'r',encoding='latin1') as f:
                reader = csv.reader(f)
                print('[jd mode ...]')
                for line in tqdm(reader):
                    jd_no = line[0]
                    if jd_no in res_dict:
                        break
                    else:
                        res_dict[jd_no] = []
                    job_description = line[1]
                    job_description_list = self._generate_jd_list(job_description)
                    for i in job_description_list:
                        res_dict[jd_no].append(i)

        return res_dict

    def _generate_jd_list(self, content):
        pattern = re.compile(r'\d+[.]')
        req_list = re.split(pattern, content)
        return req_list

    def _generate_basicgraph_list(self, mode='user', pair='satisfied'):
        res_dict = {}
        if pair == 'satisfied':
            pair = self.satisfied_pair

        if pair == 'deliver':
            pair = self.deliver_pair


        if mode == 'user':
            for tpl in pair:
                user_id = tpl[0]
                jd_no = tpl[1]
                if(user_id not in res_dict):
                    res_dict[user_id] = []
                res_dict[user_id].append(jd_no)

        else:
            for tpl in pair:
                user_id = tpl[0]
                jd_no = tpl[1]
                if(jd_no not in res_dict):
                    res_dict[jd_no] = []
                res_dict[jd_no].append(user_id)

        return res_dict

    def print_pair_cnt(self):
        #print('browse_pair Num: ', len(self.browse_pair))
        print('deliver_pair Num: ', len(self.deliver_pair))
        print('satisfied_pair Num: ', len(self.satisfied_pair))

    def generate_datajson(self, write_path, exp_len=0):
        write_line = {"label": 0, "job_posting": [], "resume": [], "job_id": "", "resume_id": "", "pair_id": ""}
        f_write = open(write_path, 'w', encoding='utf8')
        # 先写最终标记为satisfied的行, label为1
        for pair in self.satisfied_pair:
            user_id = pair[0]
            jd_no = pair[1]
            write_line["label"] = 1
            write_line["job_id"] = jd_no
            write_line["resume_id"] = user_id
            write_line["pair_id"] = jd_no + '|' + user_id
            write_line["resume"] = self.user_dict[user_id]
            if jd_no in self.jd_dict:
                write_line["job_posting"] = self.jd_dict[jd_no]
            else:
                continue
            if(len(write_line["resume"]) >= exp_len):
                f_write.write(json.dumps(write_line) + '\n')

        # "delivered (delivered to hr but not hired finally)" is other status. Here satisfy means
        # success, and my tagging only allows one status called 'satisfied'. more status can be added
        # to demonstrate more detailed recruitment status
        for pair in self.deliver_pair:
            user_id = pair[0]
            jd_no = pair[1]
            write_line["label"] = 0
            write_line["job_id"] = jd_no
            write_line["resume_id"] = user_id
            write_line["pair_id"] = jd_no + '|' + user_id
            write_line["resume"] = self.user_dict[user_id]
            if jd_no in self.jd_dict:
                write_line["job_posting"] = self.jd_dict[jd_no]
            else:
                continue
            if (len(write_line["resume"]) >= exp_len):
                f_write.write(json.dumps(write_line) + '\n')

        f_write.close()
        return

    def dump_json(self, dump_path, mode='user'):
        '''
        mode∈[user, jd]
        '''
        if mode == 'user':
            with open(dump_path, 'w') as f:
                json.dump(self.user_dict, f)
        elif mode == 'jd':
            with open(dump_path, 'w') as f:
                json.dump(self.jd_dict, f)
        elif mode == 'graph_user':
            with open(dump_path, 'w') as f:
                json.dump(self.user_luqu_dict, f)
        elif mode == 'graph_jd':
            with open(dump_path, 'w') as f:
                json.dump(self.jd_luqu_dict, f)
        elif mode == 'graph_nothired_user':
            with open(dump_path, 'w') as f:
                json.dump(self.user_nothired_dict, f)
        elif mode == 'graph_nothired_jd':
            with open(dump_path, 'w') as f:
                json.dump(self.jd_nothired_dict, f)
        return

class RealDataProcessor:
    def __init__(self, dataDir):
        self.jd_file = ''

if __name__ == '__main__':
    dataDir = '...'
