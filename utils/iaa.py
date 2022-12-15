import pandas as pd
import os
import json
from tqdm import tqdm
import numpy as np
from collections import defaultdict

class IAA:
    def __init__(self, annot_path='data/annots/', categories_path='categories.json', legend_path='legend.json', target_category=None):
        if target_category is None:
            self.categories = load_categories(categories_path)
        else:
            self.categories = target_category
        self.annot_path = annot_path
        self.legend = load_legend(legend_path)
        self.xls_list = [os.path.join(self.annot_path, file) for file in os.listdir(self.annot_path) if '.xlsx' in file]
        self.annot_list = [pd.read_excel(xls_path, sheet_name=None) for xls_path in self.xls_list]
        self.change_sheetname()

        self.xls_list = [os.path.join(self.annot_path, file) for file in os.listdir(self.annot_path) if '.xlsx' in file]
        self.annot_list = [pd.read_excel(xls_path, sheet_name=None) for xls_path in self.xls_list]

        self.workers = len(self.xls_list)
        self.test_annot_validity()

    def change_sheetname(self):
        change_list = [
            ['유엔', '제1차세계대전', '냉전', '중립국', '강대국', '연합국', '자유주의', '공산주의', '중국', '유대인', '핵무기', '전쟁', '세계대전_'],
            ['공산주의', '제1차세계대전', '유엔', '강대국', '연합국', '자유주의', '유대인', '냉전', '중국', '중립국', '핵무기', '전쟁', '세계대전_'],
            ['유대인', '냉전', '중립국', '자유주의', '강대국', '연합국', '유엔', '공산주의', '중국', '세계대전_', '전쟁', '핵무기', '제1차세계대전'],
            ['연합국', '자유주의', '공산주의', '유대인', '냉전', '중립국', '강대국', '제1차세계대전', '유엔', '중국', '핵무기', '세계대전_', '전쟁'],

        ]
        save_dir = 'data/annot_refined_sheetname'
        for i, xls_file in enumerate(os.listdir(self.annot_path)):
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, xls_file)
            writer = pd.ExcelWriter(save_path)
            for j, sheetname in enumerate(self.annot_list[i].keys()):
                self.annot_list[i][sheetname].to_excel(writer, sheet_name=change_list[i][j], index=False)
            writer.save()
        self.annot_path = save_dir
        #quit()

    def test_annot_validity(self):
        validity = True
        validcheck_error_msg = ''
        label_error_msg = ''

        self.remove_data_error()
        for category in self.categories:
            valid_check = np.array([])
            for i, annot in enumerate(self.annot_list):
                sheetname = self.get_sheetname(annot.keys(), category)

                # 1. error_check=True면 모든 sheet에서 삭제합니다.
                error_indices = annot[sheetname]['error_check']
                #print(error_indices)
                #self.remove_data_error(error_indices, category)
                annot = self.annot_list[i].copy()

                # 2. 모든 valid_check가 동일한지 검사합니다.
                valid_values = annot[sheetname]['valid_check'].values
                if valid_check.size == 0:
                    valid_check = valid_values.copy()
                else:
                    if np.array_equal(valid_check, valid_values) is False:
                        validity = False
                        indices = np.where((valid_check == valid_values) == False)
                        print(indices[0])
                        ids = annot[sheetname].iloc[indices[0]]['Id'].values
                        cur_labels = annot[sheetname].iloc[indices[0]]['label'].values
                        
                        validcheck_error_msg += f"{self.xls_list[i]}의 '{category}'에서 valid_error가 서로 다른 항목이 존재합니다. -> Id={ids}, labels={cur_labels}\n"
                
                # 3. valid_check=True지만 label이 안된 것이 없는지 검사합니다.
                condition = (annot[sheetname]['valid_check'] == True)
                filtered_df = annot[sheetname][condition]
                for id, label in zip(filtered_df['Id'].values, filtered_df['label'].values):
                    if pd.isnull(label):
                        validity = False
                        label_error_msg += f"{self.xls_list[i]}의 '{category}'에서 Id={id}인 데이터의 label 값이 지정되지 않았습니다.\n"

        for category in self.categories:
            for i, annot in enumerate(self.annot_list):
                sheetname = self.get_sheetname(annot.keys(), category)
                if annot[sheetname]['error_check'].sum() > 0:
                    print('error check error')
                
        if validity is False:
            error_msg = f'Annotation_file_error\nvalid_check\n{validcheck_error_msg}\nlabel_error\n{label_error_msg}'
            raise Exception(error_msg)
            
    def get_sheetname(self, sheets, category):
        for sheet in sheets:
            if category in sheet:
                return sheet
        raise Exception(f'{category}와 매칭되는 sheet가 없습니다.')
    
    def remove_data_error(self):
        for category in self.categories:
            errors = np.array([])
            for i, annot in enumerate(self.annot_list):
                sheetname = self.get_sheetname(annot.keys(), category)
                error_values = annot[sheetname]['error_check'].values
                if errors.size == 0:
                    errors = error_values.copy()
                else:
                    errors += error_values
            for i, annot in enumerate(self.annot_list):
                sheetname = self.get_sheetname(annot.keys(), category)
                self.annot_list[i][sheetname] = self.annot_list[i][sheetname].drop(self.annot_list[i][sheetname][errors].index)
            #self.annot_list[i][sheetname] = annot_list_clone[i][sheetname].drop(self.annot_list[i][sheetname][error_indices].index)


    def create_iaa_xlsx(self, save_path='data/workers_annot.xlsx'):
        workers = [np.array([], dtype=np.int8) for _ in range(self.workers)]
        workers = {'worker' + str(i): values for i, values in enumerate(workers)}
        #legend_list = list(self.legend.values())
        for category in self.categories:
            for i, annot in enumerate(self.annot_list):
                sheetname = self.get_sheetname(annot.keys(), category)
                df = annot[sheetname]
                condition = (df['valid_check'] == True) & (df['error_check'] == False)
                df = df[condition]
                values = list(map(lambda x: self.legend.tolist().index(x), df['label'].values))
                key = 'worker' + str(i)
                workers[key] = np.append(workers[key], values)
        out_df = pd.DataFrame(workers)
        out_df.to_excel(save_path, index=False)

def load_categories(category_path='categories.json'):
    with open(category_path, 'r') as f:
        categories = json.load(f)
    return categories

def load_legend(legend_path='legend.json'):
    with open(legend_path, 'r') as f:
        legend = json.load(f)
    legend = np.array(list(legend.values()))
    legend = np.unique(legend)
    labels = np.array([])
    for item in legend:
        if 'subj' in item or 'obj' in item:
            continue
        labels = np.append(labels, item)
    return labels