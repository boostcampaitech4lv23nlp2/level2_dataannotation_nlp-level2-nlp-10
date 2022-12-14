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
        self.legend = load_legend(legend_path)
        self.xls_list = [os.path.join(annot_path, file) for file in os.listdir(annot_path) if '.xlsx' in file]
        self.annot_list = [pd.read_excel(xls_path, sheet_name=None) for xls_path in self.xls_list]
        self.workers = len(self.xls_list)
        self.test_annot_validity()

    def test_annot_validity(self):
        validity = True
        validcheck_error_msg = ''
        label_error_msg = ''
        for category in self.categories:
            valid_check = np.array([])
            for i, annot in enumerate(self.annot_list):
                sheetname = self.get_sheetname(annot.keys(), category)
                # 1. 모든 valid_check가 동일한지 검사합니다.
                valid_values = annot[sheetname]['valid_check'].values
                if valid_check.size == 0:
                    valid_check = valid_values.copy()
                else:
                    if np.array_equal(valid_check, valid_values) is False:
                        validity = False
                        indices = np.where((valid_check == valid_values) == False)
                        validcheck_error_msg += f"{self.xls_list[i]}의 '{category}'에서 valid_error가 서로 다른 항목이 존재합니다. -> {indices}\n"
                
                # 2. valid_check=True지만 label이 안된 것이 없는지 검사합니다.
                condition = (annot[sheetname]['valid_check'] == True) & (annot[sheetname]['error_check'] == False)
                filtered_df = annot[sheetname][condition]
                for id, label in zip(filtered_df['Id'].values, filtered_df['label'].values):
                    if pd.isnull(label):
                        validity = False
                        label_error_msg += f"{self.xls_list[i]}의 '{category}'에서 Id={id}인 데이터의 label 값이 지정되지 않았습니다.\n"
                
        if validity is False:
            error_msg = f'Annotation_file_error\nvalid_check\n{validcheck_error_msg}\nlabel_error\n{label_error_msg}'
            raise Exception(error_msg)
            
    def get_sheetname(self, sheets, category):
        for sheet in sheets:
            if category in sheet:
                return sheet
        raise Exception(f'{category}와 매칭되는 sheet가 없습니다.')

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