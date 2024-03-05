# -*- encoding: utf-8 -*-
'''
file       :parse_response.py
Description:parsing response for evaluation
Date       :2024/03/05 21:19:44
Author     :Yaxin Fan
Email      : yxfansuda@stu.suda.edu.cn
'''

import re
import json

class Parser:
    def __init__(self, input_file, outut_file, ifAdj = False):
        self.input_file = input_file
        self.outut_file = outut_file
        self.realtion_list =  {
        'Comment':0,
        'comment':0,
        "Clarification_question":1,
        'Clarification question':1,
        'clarification_question':1,
        "Elaboration":2,
        'elaboration':2,
        'Acknowledgment':3,
        "Acknowledgement":3,
        'Acknowlegement':3,
        'acknowledgement':3,
        'Acnowledgement':3,
        'Acknowledge':3,
        "Explanation":4,    
        "Conditional":5, 
        'Condition':5,  
        'Conditoinal':5, 
        "QAP":6, 
        'Q-A pairs':6,  
        "Question-answer_pair":6,
        "Question":6,
        "Answer":6,
        'Question-Answer pairs':6,
        "Question-answer pairs":6,
        "Alternation":7,
        "Alternative":7,
        "Q-Elab":8,
        'Q-ELab':8,
        "Result":9,
        "Background":10,
        "Narration":11,
        "Correction":12,
        "Parallel":13,
        "Contrast":14,
        "Continuation":15,
        'continuation':15}  
        self.ifAdj = ifAdj

    def load_file(self, file):
        with open(file, "r", encoding="utf-8") as fr:
            lines  = fr.readlines()
        data = []
        for line in lines:
            data.append(json.loads(line))
        return data
    
    def write_structure(self):
        total_not_meet = 0
        data = self.load_file(self.input_file)
        with open(self.outut_file, "a+", encoding='utf8') as fw:
            for example in data:
                output = {}
                edus = example['edus']
                id = example["id"]
                relations = example['relations']
                if self.ifAdj:
                    hypothesis = self.parse_example_adj_matrix(example=example)
                else:
                    hypothesis,annlabel = self.parse_example_sparse_matrix(example=example)
                    total_not_meet+=annlabel
                    
                reference = self.GetRelations(relations)
                output['hypothesis']  = hypothesis
                output['reference']  = reference
                output['id'] = id
                output['edu_num'] = len(edus)
                fw.write(json.dumps(repr(output))+'\n')
        print('not meet',total_not_meet)

    def parse_example_sparse_matrix(self, example):
        id = example['id']
        response = example['output']
        triplets = self.re_find_triplets(response)
        filtered_triples,annolabel = self.filter_triplets(triplets)
        if filtered_triples:
            OrderTriples = self.check_triples_inOrder(filtered_triples)
            return OrderTriples,annolabel
        else:
            return {},annolabel

    def check_triples_inOrder(self, filtered_triples):
      
        Ordertriples = {}
        for key, value in filtered_triples.items():
            if key[1]<key[0]:
                if (key[1],key[0]) not in Ordertriples:
                    Ordertriples[(key[1],key[0])] = value
            else:
                if key not in Ordertriples:
                    Ordertriples[key] = value
        return Ordertriples
    
    def re_find_triplets(self, text):
        triples = re.findall(r'\[.*?\]', text)
        triples2 = re.findall(r'\(.*?\)', text)
        final_triplets  = triples+triples2
        return final_triplets
    
   
    def check_re(self, relation_list, string):
        for relation in relation_list:
            if relation in string:
                return relation,False
        else:
            return 'Question-answer_pair',True
        
    def filter_triplets(self, triplets):
        filtered_triplets = {}
        new_triplets = []
        for triple  in triplets:
            if triple !='':
                new_triplets.append(triple)
        anno_label = False
        for triplet in new_triplets:
            triplet = triplet.strip()
            index_list = re.findall(r'\d+',triplet)
            te_Rela, anno_label = self.check_re(self.realtion_list.keys(), triplet)
            if len(index_list) == 2 and te_Rela!= None:
                index1 = int(index_list[0])
                index2 = int(index_list[1])
                relation = self.realtion_list[te_Rela]
                filtered_triplets[(index1,index2)] = relation
        return filtered_triplets,anno_label

    def GetRelations(self, relations):
        relations_dic = {}
        for relation in relations:
            x = relation["x"]
            y = relation["y"]
            type = self.realtion_list[relation["type"]]
            relations_dic[(x, y)] = type
        return relations_dic

if __name__ == "__main__":
    pass
