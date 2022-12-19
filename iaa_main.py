from utils.iaa import IAA
from utils.data_gen import DataGen
from utils.calculate_iaa import print_fleisskappa
import sys
import argparse

def select_categories():
    available_categories = [
    '제1차세계대전',
    '유엔',
    '강대국',
    '냉전',
    '중국',
    '중립국',
    '공산주의',
    '연합국',
    '자유주의',
    '유대인',
    '핵무기'
    ]
    remove_list = [
        #'제1차세계대전',
        #'냉전',
    ]
    for item in remove_list:
        available_categories.remove(item)
    return available_categories

def print_description(run_type, available_categories):
    print('\n' + '='*10 + f' {run_type} ' + '='*10)
    print('-'*10 + 'categories' + '-'*10)
    for category in available_categories:
        print(category)
    print('-'*30 + '\n')

def run_iaa(xls_path):
    available_categories = select_categories()
    print_description('IAA', available_categories)
    iaa = IAA(target_category=available_categories)
    iaa.create_iaa_xlsx()
    print_fleisskappa('/opt/ml/level2_dataannotation_nlp-level2-nlp-10/data/workers_annot.xlsx')

def run_datagen():
    available_categories = select_categories()
    print_description('Datagen', available_categories)
    datagen = DataGen(target_category=available_categories)
    datagen.create_data()

if __name__ == '__main__':
    default_xls_path = '/opt/ml/level2_dataannotation_nlp-level2-nlp-10/data/workers_annot.xlsx'
    parser = argparse.ArgumentParser()
    parser.add_argument('--iaa_path', default=default_xls_path)
    parser.add_argument('--datagen', default=False)
    arg = parser.parse_args()
    
    xls_path = arg.iaa_path

    for c in ['T', 'True', 'true', 't']:
        if c == arg.datagen:
            arg.datagen = True
        
    if arg.datagen:
        run_datagen()
    else:
        run_iaa(xls_path)