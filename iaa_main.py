from utils.iaa import IAA
from utils.calculate_iaa import print_fleisskappa
import sys

def main(xls_path):
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
        # 라벨링이 아직 안됨
        #'제1차세계대전',
        '공산주의',
        '중국',
        '핵무기',
        # 기타 오류
        '유대인',
        '냉전',
        '유엔', 
    ]
    for item in remove_list:
        available_categories.remove(item)
    print('\n' + '-'*10 + 'categories' + '-'*10)
    for category in available_categories:
        print(category)
    print('-'*30 + '\n')
    iaa = IAA(target_category=available_categories)
    iaa.create_iaa_xlsx()
    print_fleisskappa('/opt/ml/level2_dataannotation_nlp-level2-nlp-10/data/workers_annot.xlsx')

if __name__ == '__main__':
    xls_path = '/opt/ml/level2_dataannotation_nlp-level2-nlp-10/data/workers_annot.xlsx'
    if len(sys.argv) > 1:
        xls_path = sys.argv[1]

    main(xls_path)