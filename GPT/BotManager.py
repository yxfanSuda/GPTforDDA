import json
import multiprocessing
import os
from tqdm import tqdm
from .PostRobot import PostRobot
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(current_dir)
sys.path.append("..")

class BotManager:
    def __init__(self):
        self.result_output_dir = ""
        self.api_key = None
        self.processes_num = 50
        self.proxy = None
        self.start = None
        self.end = None
        self.sample_list = []
        self.model_name = ""
        self.base_url = ""

    def set_api_key(self, api_key=''):
            self.api_key = api_key

    def set_processes_num(self, processes_num):
        if processes_num!=None:
            self.processes_num = processes_num

    def set_model(self, model='gpt-3.5-turbo'):
        self.model_name = model
        
    def set_base_url(self, base_url="https://api.openai.com/v1", index=0):
            self.base_url = base_url

    def set_result_output_dir(self, result_output_dir=None):
        if result_output_dir is None:
            if self.end is None:
                result_output_dir = str(self.start) + "_" + str(len(self.sample_list) - self.start) + "/"
            else:
                result_output_dir = str(self.start) + "_" + str(self.end) + "/"
        self.result_output_dir = result_output_dir
        if os.path.exists(self.result_output_dir):
            pass
        else:
            os.mkdir(self.result_output_dir)

    def merge_files(self, output_file_name=None):
        _, _, filenames = [i for i in os.walk(self.result_output_dir)][0]
        filenames = sorted(filenames, key=lambda x: int(x.split('.')[0]), reverse=True)
        generated_instructions = [open(os.path.join(self.result_output_dir, filename), encoding="utf-8").read() for
                                  filename
                                  in filenames]
        texts = "\n".join(generated_instructions)
        if output_file_name is None:
            if self.end is None:
                output_file_name = str(self.start) + "_" + str(len(self.sample_list) - self.start) + ".jsonl"
            else:
                output_file_name = str(self.start) + "_" + str(self.end) + ".jsonl"
        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(texts)

    def read_sample(self, file_name, start=0, end=None, role=None):
        result = []
        with open(file_name, "r", encoding="utf-8") as fr:
            lines = fr.readlines()
            count_number = 0
            for line in lines:
                line = line.strip()
                sample = json.loads(line)
                result.append((count_number, sample, role))
                count_number += 1
        self.start = start
        self.end = end
        if end is None:
            self.sample_list = result[start:]
        else:
            self.sample_list = result[start:end]

    def process_sample(self, sample_list):
        index = sample_list[0]
        sample = sample_list[1]
        role = sample_list[2]
        if os.path.exists(self.result_output_dir + str(index) + ".json"):
            return -1
        sample["output"] = self.get_string(sample, role)
        with open(self.result_output_dir + str(index) + ".json", mode="w", encoding="utf-8") as fw:
            json.dump(sample, fw, ensure_ascii=False)
        return index

    def get_string(self, sample, role):
        robot = PostRobot()
        robot.base_url=self.base_url
        robot.model_name=self.model_name
        robot.set_thinking_engine(self.api_key, self.proxy)
        if role is not None:
            robot.set_role(role)
        prompt = robot.get_prompt(sample)
        flag, response = robot.generate(prompt)
        return response

    def multi_process(self):
        with multiprocessing.Pool(processes=self.processes_num) as pool:
            results = [
                pool.apply_async(self.process_sample, args=(sample,))
                for sample in self.sample_list
            ]
            for r in tqdm(results, desc="Processing samples", unit="sample"):
                r.wait()
            result_list = [r.get() for r in results]
            pool.close()
            pool.join()

    def generate_sequences(self, 
                           processes_num = 50,
                           api_key='',
                           model='gpt-3.5-turbo',
                           base_url='https://api.openai.com/v1', 
                           input_file_name="input.jsonl",
                           pool_output_dir = './pool_output_dir',
                           output_file_name="output.jsonl"):
        bot_manager = BotManager()
        bot_manager.set_processes_num(processes_num=processes_num)
        bot_manager.set_api_key(api_key=api_key)
        bot_manager.set_model(model=model)
        bot_manager.set_base_url(base_url=base_url)
        bot_manager.read_sample(file_name=input_file_name)
        bot_manager.set_result_output_dir(result_output_dir=pool_output_dir)
        bot_manager.multi_process()
        bot_manager.merge_files(output_file_name)
