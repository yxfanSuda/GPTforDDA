# -*- encoding: utf-8 -*-
'''
file       :Parser.py
Description: parsing the response for evaluation
Date       :2024/03/05 18:24:33
Author     :Yaxin Fan
Email      : yxfansuda@stu.suda.edu.cn
'''


import re
import json
from segeval.window.pk import pk
from segeval.window.windowdiff import window_diff as WD
from sklearn.metrics import f1_score

class Parser:
    def __init__(self, source_file, response_file, boundary_file):
        self.source_file = source_file
        self.response_file = response_file
        self.boundary_file = boundary_file

    def load_file(self, file):
        """
        加载输出文件
        """
        datas = []
        with open(file, "r", encoding="utf-8") as fr:
            lines  = fr.readlines()
        for line in lines:
            datas.append(json.loads(line.strip()))
        return datas
    
    # 将字符串转为列表
    def convert_triple_to_list(self, triple):
        """
        """
        # 找到数字[]
        rex = r'\d+'
        result = re.findall(rex,triple)
        # 将str转为数字
        return [int(a) for a in result]
    
    def del_exceed_bounary(self, boundary_list, dialogue_len):
       
    
        new_boundary_list = []
        for boundary in boundary_list:
            new_bound  = []
            for item in boundary:
                if item < dialogue_len:
                    new_bound.append(item)
            if new_bound:
                new_boundary_list.append(new_bound)
        return new_boundary_list


    def convert_bound_to_consecutive(self, bound):
        '''
        convert = [1,5] to [1,2,3,4,5]
        [0,0] ->[0]
        '''
        if len(bound) == 0:
            return[bound[0]]
        else:
            return [a for a in range(bound[0],bound[1]+1)]
    
    def re_find_boundary(self, text, dialogue_len):
      
        not_follow = False
        triples = re.findall(r'\[.*?\]', text)
        new_triplets = []
        for triplet in triples:
            new_triplets.append(self.convert_triple_to_list(triplet))
        # 分割
        split_striplets = []
        not_follow1 = False
        for triplet in new_triplets:
            split_chunsk, not_follow1 = self.split_cont_chunks(triplet)
            split_striplets+=split_chunsk
        # 排序
        sorted_split_striplets = sorted(split_striplets, key= lambda x: x[0])
        # 超过的删除
        sorted_split_striplets = self.del_exceed_bounary(sorted_split_striplets, dialogue_len)
       
        # 增添，缺少的添上
        total_index = [ ]
        for a in sorted_split_striplets:
            total_index += a
        added_list = []# 需要增加的索引
        for index in range(dialogue_len):
            if index not in total_index:
                added_list.append(index)
        # 将add_index 分割，增加到排序后的，然后再进行排序得到所有的
        not_follow2 = False
        not_follow3 = False
        if added_list:
            not_follow2 = True
            split_chunsk, not_follow3 = self.split_cont_chunks(added_list)
            sorted_split_striplets+=split_chunsk
        sorted_split_striplets = sorted(sorted_split_striplets, key= lambda x: x[0])
        # 去除重复的
        sorted_split_striplets, not_follow4 = self.remove_dup_boundaries(sorted_split_striplets)
        # 去掉overlap的[0,1].[0]二者去掉一个
           # 去除overlap的
        sorted_split_striplets ,not_follow4= self.remove_overlap_boundary(sorted_split_striplets)
        # 去除重复的可能造成缺少，将缺少的补上
        total_index_2 = [ ]
        for a in sorted_split_striplets:
            total_index_2 += a
            
         
        not_follow5 = False
        not_follow6 = False
        added_list2 = []# 需要增加的索引
        for index in range(dialogue_len):
            if index not in total_index_2:
                added_list2.append(index)
        if added_list2:
            not_follow5 = True
            split_chunsk, not_follow6 = self.split_cont_chunks(added_list2)
            sorted_split_striplets+=split_chunsk

        sorted_split_striplets = sorted(sorted_split_striplets, key= lambda x: x[0])
        new_triplets = []

        for plet in sorted_split_striplets:
            star_and_end = self.re_find_start_end(plet)
            new_triplets.append(star_and_end)
     
        
        if True in [not_follow1, not_follow2, not_follow3, not_follow4,not_follow5, not_follow6]:
            not_follow = True
        return new_triplets, not_follow
  
    def re_find_start_end(self, item):
        """
        """
        if len(item)==1:
            return [item[0], item[0]]
        elif len(item)==2:
            return item
        else:
            return[item[0],item[-1]]

    def split_cont_chunks(self, chunk_list):
        """

        将不连续的序列拆成连续的多个子序列

        拆出连续的序列[5, 6, 9, 10] 拆成[5,6] [9,10]
        
        """
        not_follow = False
        chunk_list = sorted(chunk_list)
        start = 0
        total_consecutive_list = []
        temp_chunk = []
        for end in range(len(chunk_list)):
           
            if end==0:
                temp_chunk.append(chunk_list[end])
                continue
            if chunk_list[end]-chunk_list[end-1]==1:
                temp_chunk.append(chunk_list[end])
            else:
                start = end
                total_consecutive_list.append(temp_chunk)
                temp_chunk = [chunk_list[start]]
        
        if temp_chunk:
            total_consecutive_list.append(temp_chunk)
        if len(total_consecutive_list)>1:
            not_follow = True
        return total_consecutive_list, not_follow
         
    def get_dialogue_len(self, instruction):
        last_utterances =  instruction.split('\n')[-1]
        rex = r'\d+'
        result = re.findall(rex,last_utterances)
        return int(result[0])+1
    
    def remove_dup_boundaries(self, lst):
        not_follow =False
        from collections import Counter
        lst = (tuple(a) for a in lst)
        counter = Counter(lst)
        sorted_bound_list = sorted(counter.keys(), key=lambda x:x[0])
        for va in counter.values():
            if va>1:
                not_follow = True
        return [list(a) for a in sorted_bound_list], not_follow

    def write_boundary(self):
        """
        解析一个样例
        """
        not_follow_num =0
        examples = self.load_file(self.response_file)
        with open(self.boundary_file, "a+", encoding='utf8') as fw:
            for example in examples:
                response = example['output']
                dialogue_len = self.get_dialogue_len(example['instruction'])
                boundaries,not_Follow_temp = self.re_find_boundary(response,dialogue_len)
                not_follow_num += not_Follow_temp
                temp_dic = {}
                temp_dic['id'] = example['id']
                temp_dic["boundary"] = boundaries
                fw.write(json.dumps(temp_dic)+'\n')

    def convertsourcelabel2mass(self, sourcelabel):
        """sourcekabel = [0,0,0,0,1,1,1,1,3,3,3,3,4,4,4,4]
        return [4,4,4,4,4]
        """ 
        mass = []
        from collections import Counter
        arr_dic = Counter(sourcelabel)
        arr_list = [[key,value] for key,value in arr_dic.items()]
        arr_list = sorted(arr_list,key=lambda x:x[0])
        for value in arr_list:
            mass.append(value[-1])
        return mass
    
    def convertmass2binary(self, masslabel):
        """sourcekabel = [4,4,4,4,4]
        return [4,4,4,4,4]
        """ 
        mass = []
        binary_list=  []
        for num in masslabel:
            for i in range(num-1):
                binary_list.append(0)
            binary_list.append(1)
        binary_list[-1] = 0
        assert len(binary_list) == sum(masslabel)
        return binary_list
    
    def convertboundary2mass(self, boundary_list):
        """
        #按照列表中元素的最后一个来分割     
        boundary_list = [["0", "5"], ["6", "12"], ["13", "15"], ["16", "25"]]
        return [6,7,3,10]
        """
        #按照第一个元素进行排序
        new_boundary_list = []
        # print('boundary_list')
        # print(boundary_list)
        for item in boundary_list:
            if len(item)==2:
                new_boundary_list.append([int(item[0]), int(item[1])])
            else:
                # print(item)
                new_boundary_list.append([int(item[0])])
        new_boundary_list = sorted(new_boundary_list, key=lambda x:x[0])  
        split_indexes = [-1]
        for bound_list in new_boundary_list:
            split_indexes.append(int(bound_list[-1]))
        mass = []
        for i, j in zip(split_indexes, split_indexes[1:]):
            mass.append(abs(j-i))
        return mass
    
    def convertBoundary2Binary(self, boundary_list):
        """
        [[0, 3], [4, 7]]--->[0,0,0,1,0,0,0,0]
        """
        binary_label = []
        if len(boundary_list) == 1:
            binary_label = [0]*(boundary_list[0][-1]+1)
        else:
            for boundary in boundary_list:
                for _ in range(boundary[0],boundary[1]):
                    binary_label.append(0)
                binary_label.append(1)
            binary_label[-1] = 0#最后一个为0
        assert len(binary_label) == boundary_list[-1][-1]+1
        return binary_label
    
    def fetch_predict_label_by_id(self, id_num, predicted_boundary):
        """
        """
        for item in predicted_boundary:
            if item['id'] == id_num:
                return item['boundary']

    def index_in_bound_list(self,boud_list, index):
        """
        判断index 是否在剩余的部分
        [[0,], [0, 0], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]]
        比如判断(0,0)中的元素是否在剩余的部分  [[0, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]]
        存在，则删除跨度最大的
        """
        for bound in boud_list:
            if index in bound:
                return bound
        return []
    
    def remove_overlap_boundary(self, bound_list):
        # 二者删除1,删除跨度最大的那个
        not_Follow = False
        new_boundary_list = []
        for index in range(len(bound_list)):
            rest_bound_list = bound_list[index+1:]
           
            cur_bound = bound_list[index]

            overlap = False
            for temp_index in cur_bound:
                if self.index_in_bound_list(rest_bound_list, temp_index):
                    overlap = True
           
            if not overlap:
                new_boundary_list.append(cur_bound)
        if len(new_boundary_list) != len(bound_list):
            not_Follow = True
        return new_boundary_list, not_Follow
        # for bound in bound_list:
        #     for 

    def load_src_file(self,file):
        import re   
        with open(file, "r", encoding='utf8') as fr:
            text = fr.read()
        text_list = re.split(r'call_id_',text)
        text_list = text_list[1:]
        data_list = []
        for item in text_list:
            data_list.append(self.split_text_pieces(item))
        
        return data_list

    def split_text_pieces(self, sub_text):
        """
        修改bug，有的数字是两位数
        """
        text_list = sub_text.strip().split("\n")
        id = 'call_id_{}'.format(text_list[0])
        utterance_list  = []
        label_list = []
        for text in text_list[1:]:
            nums = re.findall(r'\d+',text)
            label = nums[0]
            if len(nums[0])==1:
                utterance = text[1:].strip()
            elif len(nums[0])==2:
                utterance = text[2:].strip()
            else:
                print('topic number errors')
                raise KeyError
            utterance_list.append(utterance)
            label_list.append(int(label))
        temp_dic = {}
        temp_dic["id"] = id
        temp_dic["utterances"] = utterance_list
        temp_dic["labels"] = label_list
        return temp_dic

    def evaluate(self):
        """
        """
        reference_datas = self.load_src_file(self.source_file)
        predicted_boundary = self.load_file(self.boundary_file)
   
        total_equal_num = 0
        score_pk = 0
        score_wd = 0 
        score_f1 = 0
        total_reference_labels = []
        total_predict_labels = []
        for da in reference_datas:
            id = da['id']
            reference_labels = da['labels']
            reference_mass = self.convertsourcelabel2mass(reference_labels)
            reference_binary_labels = self.convertmass2binary(reference_mass)

            predicted_labels = self.fetch_predict_label_by_id(id, predicted_boundary)
            predicted_mass = self.convertboundary2mass(predicted_labels)

            predicted_binary_labels = self.convertmass2binary(predicted_mass)
            total_reference_labels.extend(reference_binary_labels)
            total_predict_labels.extend(predicted_binary_labels)
            assert sum(reference_mass) == sum(predicted_mass)

            total_equal_num += 1
            if len(reference_mass) == len(predicted_mass) == 1:
                temp_PK = 0
                temp_WD = 0
                temp_f1 = 1
            elif sum(reference_mass) ==2:
                temp_PK = 0
                temp_WD = 0
                temp_f1 = 1
            else:
                temp_PK = pk(predicted_mass
                            ,reference_mass,
                            one_minus = False)
                temp_WD = WD(predicted_mass
                            ,reference_mass)
                temp_f1 = f1_score(reference_binary_labels, predicted_binary_labels, 
                                    average='macro',zero_division=0)
                    
                      
                score_pk += temp_PK
                score_wd += temp_WD
                score_f1 += temp_f1
                  
        print(total_equal_num)
        print('pk is {}'.format(score_pk/total_equal_num))
        print('wd is {}'.format(score_wd/total_equal_num))
        print('f1 is {}'.format(score_f1/total_equal_num))
      
if __name__ == "__main__":


   pass