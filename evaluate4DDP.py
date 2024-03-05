
'''
file       :evaluate4DDP.py
Description: GPT for DDP
Date       :2024/03/05 21:17:16
Author     :Yaxin Fan
Email      : yxfansuda@stu.suda.edu.cn
'''



from GPT import BotManager
from DDP.Parser import Parser
from DDP.utils import DataAnalysis

if __name__ == '__main__':

    # using GPT to generate the reponse 
    bot_manager = BotManager()
    processes_num = 50 # num of threads
    api_key = 'sk-xxx'
    base_url = 'https://api.openai.com/v1'
    model = 'gpt-3.5-turbo'
    input_file_name = './DDP/dataset/Molweni/Molweni_instructions.jsonl'
    pool_output_dir = './DDP/ResponseFile/MolweniPool/'
    output_file_name = './DDP/ResponseFile/MolweniResponse.json'
    bot_manager.generate_sequences(api_key = api_key,
                                base_url = base_url,
                                model= model,
                                input_file_name = input_file_name,
                                pool_output_dir=pool_output_dir,
                                output_file_name = output_file_name,
                                processes_num= processes_num
    )

    # evaluation
    structure_output_file = "./DDP/StructureDir/MolweniStructure.json"
    parser = Parser(output_file_name, structure_output_file)
    parser.write_structure()
    data_analysis = DataAnalysis(structure_output_file, '')
    data_analysis.compute_f1_all_file()
    data_analysis.compute_the_Accuracy_Of_Different_RelaType()
