# -*- encoding: utf-8 -*-
'''
file       :evaluate4DTS.py
Description: code for DTS using ChatGPT
Date       :2024/03/05 17:08:48
Author     :Yaxin Fan
Email      : yxfansuda@stu.suda.edu.cn
'''


from GPT import BotManager
from DTS.Parser import Parser
if __name__ == '__main__':
    # using GPT to generate the reponse 
    bot_manager = BotManager()
    processes_num = 50 # num of threads
    api_key = 'sk-xxx'
    base_url = 'https://api.openai.com/v1'
    model = 'gpt-3.5-turbo'
    input_file_name = './DTS/dataset/doc2dialDir/doc2dial_instructions.jsonl'
    pool_output_dir = './DTS/ResponseFile/doc2dialPool/'
    output_file_name = './DTS/ResponseFile/doc2dial_response.json'
    bot_manager.generate_sequences(api_key = api_key,
                                base_url = base_url,
                                model= model,
                                input_file_name = input_file_name,
                                pool_output_dir=pool_output_dir,
                                output_file_name = output_file_name,
                                processes_num= processes_num
    )

    # evaluation
    src_file = './DTS/dataset/doc2dialDir/doc2dial.txt'
    boundary_file = './DTS/BoundaryDir/doc2dialBound.json'
    parser = Parser(source_file=src_file, 
                    response_file=output_file_name, 
                    boundary_file= boundary_file)
    parser.write_boundary()
    parser.evaluate()