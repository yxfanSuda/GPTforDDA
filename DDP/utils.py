import json
import numpy as np
from tqdm import tqdm

class DataAnalysis:
    def __init__(self, result, source):
        self.resultfile = result
        self.sourcefile = source

    def read_result(self,file):
        with open(file,'r',encoding='utf8')as fr:
            lines = fr.readlines()
        data = []
        for line in lines:
            line = line.strip()
            data.append(eval(json.loads(line)))
        new_data_dic  = {}
        for da in data:
            temp_dic = {}
            id = da['id']
            temp_dic['hypothesis']= da['hypothesis']
            temp_dic['reference']  = da['reference']
            temp_dic['edu_num'] = da['edu_num']
            new_data_dic[id] = temp_dic
        return new_data_dic


    def get_eval_matrix(self, eval_matrix, predicted_result):
        for k, v in eval_matrix.items():

            if v is None:
                if isinstance(predicted_result[k], dict):
                    eval_matrix[k] = [predicted_result[k]]
                else:
                    eval_matrix[k] = predicted_result[k]
            elif isinstance(v, list):
                eval_matrix[k] += [predicted_result[k]]
            else:
                eval_matrix[k] = np.append(eval_matrix[k], predicted_result[k])


    def compute_f1_all_file(self):
        predict_list_dic = self.read_result(self.resultfile)
        edu_set = set([predict['edu_num'] for predict in predict_list_dic.values()])

        eval_matrix = {
            'hypothesis': None,
            'reference': None,
            'edu_num': None
        }

        for edu_num in edu_set:
            temp_predict_list = {}
            for key, value in predict_list_dic.items():
                if value['edu_num'] == edu_num:
                    temp_predict_list[key] = value
            for predict in temp_predict_list.values():
                self.get_eval_matrix(eval_matrix, predict)
        print(self.tsinghua_F1(eval_matrix))

    def tsinghua_F1(self,eval_matrix):
        cnt_golden, cnt_pred, cnt_cor_bi, cnt_cor_multi = 0, 0, 0, 0
        for hypothesis, reference, edu_num in zip(eval_matrix['hypothesis'], eval_matrix['reference'],
                                                eval_matrix['edu_num']):
            cnt = [0] * edu_num
            for r in reference:
                cnt[r[1]] += 1
            for i in range(edu_num):
                if cnt[i] == 0:
                    cnt_golden += 1
            cnt_pred += 1
            if cnt[0] == 0:
                cnt_cor_bi += 1
                cnt_cor_multi += 1
            cnt_golden += len(reference)
            cnt_pred += len(hypothesis)
            for pair in hypothesis:
                if pair in reference:
                    cnt_cor_bi += 1
                    if hypothesis[pair] == reference[pair]:
                        cnt_cor_multi += 1
        prec_bi, recall_bi = cnt_cor_bi * 1. / cnt_pred, cnt_cor_bi * 1. / cnt_golden
        f1_bi = 2 * prec_bi * recall_bi / (prec_bi + recall_bi)
        prec_multi, recall_multi = cnt_cor_multi * 1. / cnt_pred, cnt_cor_multi * 1. / cnt_golden
        f1_multi = 2 * prec_multi * recall_multi / (prec_multi + recall_multi)
        print('link precision is {}'.format(prec_bi))
        return f1_bi, f1_multi

    def compute_the_Accuracy_Of_Different_RelaType(self):
        """
        计算不同关系类型的正确率
        :return:
        """
        total_relation_dic = {}
        correct_relation_dic = {}
        predictlabelset = set()
        predict_list_dic = self.read_result(self.resultfile)
        total_ref_rel_num = 0
        for id, item in predict_list_dic.items():
            hypo = item['hypothesis']
            ref = item['reference']
            total_ref_rel_num += len(ref)
            for _,rel in hypo.items():
                predictlabelset.add(rel)
            for ref_link, ref_rel in ref.items():
                if ref_rel in total_relation_dic:
                    total_relation_dic [ref_rel] += 1
                else:
                    total_relation_dic [ref_rel] = 1
                if ref_link in hypo and ref_rel == hypo[ref_link]:
                    if ref_rel in correct_relation_dic:
                        correct_relation_dic[ref_rel] += 1
                    else:
                        correct_relation_dic[ref_rel] = 1
        label2id = {'Comment': 0, 'Clarification_question': 1, 'Elaboration': 2, 'Acknowledgment': 3, 'Explanation': 4,
                    'Conditional': 5,
                    'Question-answer_pair': 6, 'Alternation': 7, 'Q-ELab': 8, 'Result': 9, 'Background': 10,
                    'Narration': 11,
                    'Correction': 12, 'Parallel': 13, 'Contrast': 14, 'Continuation': 15}


        id2label = {}
        for key, value in label2id.items():
            id2label[value] = key
        new_correct_relation_dic  = {}
        new_total_relation_dic  = {}
        for id,value in correct_relation_dic.items():
            new_correct_relation_dic[id2label[id]] = value

        for id, value in total_relation_dic.items():
            new_total_relation_dic[id2label[id]] = value
        print(new_correct_relation_dic)
        print(new_total_relation_dic)
        print(total_ref_rel_num)
        print('percentage of relation type')
        for key, value in new_total_relation_dic.items():
            print(key , round(value/total_ref_rel_num,4))

        print('accuracy of different relation type')
        for key, value in new_correct_relation_dic.items():
            print(key + ':' + str(round(value/new_total_relation_dic[key],4)))
    



if __name__ == "__main__":
    
    pass