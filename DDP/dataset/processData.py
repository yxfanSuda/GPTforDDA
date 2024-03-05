# -*- encoding: utf-8 -*-
'''
file       :processData.py
Description:
Date       :2024/03/05 22:44:32
Author     :Yaxin Fan
Email      : yxfansuda@stu.suda.edu.cn
'''


import jsonlines
import json

        
class FileProcessing:
    def __init__(self) -> None:
        
        pass
    def loadtxt(self, file) -> None:
        with open(file,'r',encoding='utf8') as fr:
            content = fr.read().strip()
        return content
    
    def write2txt(self, response, des_file):
        with open(des_file,'a+',encoding='utf8')as fw:
            fw.write(response)

    def write2json(self, response, des_file):
        with open(des_file,'w',encoding='utf8') as fw:
            json.dump(response,fw,ensure_ascii=False, indent=4)





class Load_Dialogue_Dataset:
    def __init__(self) -> None:
        pass
    def load_json(self, file):
        with open(file,"r",encoding='utf8') as fr:
            data = json.load(fr)
        return data
    
    def GetItemsOfData(self, ItemDic: dict):
        edus = ItemDic['edus']
        relations = ItemDic['relations']
        item_id = ItemDic["id"]
        return edus, relations, item_id
    

    def GetSpeakerUtt(self, edus):
        pass


    def check_predict_Alignto_reference(self, reference_file, predict_file):
        reference_data = self.load_json(reference_file)
        id_set = set()
        for da in reference_data:
            _,_, id = self.GetItemsOfData(da)
            id_set.add(id)
        
        predict_id_set = set()
        with open(predict_file,'r',encoding='utf8')as fr:
            lines = fr.readlines()
        data = []
        for line in lines:
            line = line.strip()
            data.append(eval(json.loads(line)))
        for da in data:
            predict_id_set.add(da['id'])
        predict_id_list = list(predict_id_set)
        uncovered_ids  = []
        for id in id_set:
            if id not in predict_id_list:
                uncovered_ids.append(id)
        print('uncovered ids')
        print(uncovered_ids)

class GenerateInputSamples:
    def __init__(self, source_file, prompt_file, des_file):
        self.fileprocessor = FileProcessing()
        self.data_loader = Load_Dialogue_Dataset()
        self.prompt = self.fileprocessor.loadtxt(prompt_file)
        self.datas = self.data_loader.load_json(source_file)
        self.samples_list = []
        self.des_file = des_file
    
    def parse_edus(self, edus):
        new_edu_text = ''
        for index, edu in enumerate(edus):
            temp_str  = "{}: ".format(index) + edu['speaker']+' said, '+ edu['text']+'\n'
            new_edu_text += temp_str
        return new_edu_text
    """{"instruction": "Give three tips for staying healthy.", "input": "", "output": ""}"""
    def generate_Samples(self,):
        for da in self.datas:
            temp_dict = {}
            temp_dict['id'] = da['id']
            temp_dict['edus'] = da['edus']
            temp_dict['relations'] = da['relations']
            
            temp_dict['input'] = ''
            temp_dict['output'] = ''
            edu_text = self.parse_edus(edus=da['edus'])
            instruction = self.prompt + '\n' + edu_text 
            temp_dict['instruction'] = instruction
            self.samples_list.append(temp_dict)
          
    def write_file(self):
        self.generate_Samples()
        with jsonlines.open(self.des_file,'w') as fw:
            for sample in self.samples_list:
                fw.write(sample)
        
        

        

if __name__ == "__main__":

    
    testDataFile = './STAC/test.json'
    promptFile = 'prompt.txt'
    outputFile = 'STAC_instructions.jsonl'
    generatesamples = GenerateInputSamples(testDataFile, 
                                        promptFile,
                                        outputFile)
    generatesamples.write_file()
    

      
   
    
   