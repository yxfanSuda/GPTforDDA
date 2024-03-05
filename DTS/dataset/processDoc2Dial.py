# -*- encoding: utf-8 -*-
'''
file       :processDoc2Dial.py
Description:
Date       :2024/03/05 18:44:54
Author     :Yaxin Fan
Email      : yxfansuda@stu.suda.edu.cn
'''



import os
import jsonlines

def get_files(dir):
    filenames = os.listdir(dir)
    filepath = [dir+'/dialogue_{}.txt'.format(id) for id in range(len(filenames))]
    
    return filepath

def read_file(file):
    """
    返回utterancelist and the boundary
    """
    with open(file,'r',encoding='utf8')as fr:
        lines = fr.readlines()
    utterances = []
    labels = []
    index = 0
    for line in lines:
        line = line.strip()
        if line !='================':
            utterances.append(line)
            labels.append(index)
        else:
            index+=1
    return utterances, labels

def construct_Test_file(source_dir, des_file):
    file_list = get_files(source_dir)
    print(file_list)
    data_list = []
    for index, file in enumerate(file_list):
        data_list.append('call_id_{}'.format(index))
        utterances, labels = read_file(file=file)
        assert len(utterances)==len(labels)
        for label, utt in zip(labels, utterances):
            data_list.append(str(label)+' '+utt)
    print(len(data_list))
    with open(des_file, 'w', encoding='utf8')as fw:
        for da in data_list:
            fw.write(da+'\n')

def read_prompt(file):
    with open(file,'r',encoding='utf8')as fr:
        prompt = fr.read()
    return prompt.strip()


def construction_instructions(source_dir,prompt_file, des_file):
    """
    构造指令形式,id input, output,instruction
    """
    prompt = read_prompt(prompt_file)
    filepaths = get_files(source_dir)
    with open(des_file,'w',encoding='utf8')as fw:
        writer = jsonlines.Writer(fw)
        for index, filepath in enumerate(filepaths):
            utterances, _ = read_file(filepath)
            utterances_list = [str(index)+'. ' + utterance for index, utterance in enumerate(utterances)]
            utterance_text = '\n'.join(utterances_list)
            instruction = prompt+'\n'+utterance_text
            id = 'call_id_{}'.format(index)
            input = ''
            output = ''
            tempdict = {}
            tempdict['id'] = id
            tempdict['input'] = input
            tempdict['output'] = output
            tempdict['instruction'] = instruction
            writer.write(tempdict)
construct_Test_file('./doc2dialDir/doc2dial', './doc2dial.txt')
construction_instructions('/doc2dialDir/doc2dial', 
                          'prompt.txt',
                          './doc2dialDir/doc2dial_instructions.jsonl')

    
