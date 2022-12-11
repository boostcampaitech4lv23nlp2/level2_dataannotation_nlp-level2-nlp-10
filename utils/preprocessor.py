import os
import json
from collections import defaultdict

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

def make_df(
    html_directory: str, html_file_list: list, json_directory: str, json_file_list: list, legend: dict
) -> pd.DataFrame:
    """
    data directory에 저장되어 있는 html/json 파일들로부터 
    [Id, sentence, subj_entity_type, obj_entity_type, label] 형식의 하나의 데이터프레임을 만듭니다.

    parameters
        html_directory, json_direcoty : html,json 파일이 저장되어 있는 directory
        html_file_list, json_file_list : html, json 파일 이름이 저장되어 있는 list
    """
    df = pd.DataFrame({"Id": [], "sentence": [], "subj_entity_type": [], "obj_entity_type": [], "label" : []})
    idx = int(1)

    for html_file, json_file in tqdm(zip(html_file_list, json_file_list), total = len(html_file_list)):
        if html_file.split('.')[0] != json_file.split('.')[0]:
            # html 파일과 json 파일이 매칭되지 않는다면 종료합니다.
            print('ERROR!!! {} html file does not match with {} json file.'.format(html_file.split('.')[0],
                json_file.split('.')[0]))
            return None

        else:
            # html 파일을 읽어 sentence를 추출합니다.
            html_file_directory = os.path.join(html_directory, html_file)
            with open(html_file_directory, 'r', encoding = 'UTF-8') as f:
                html_text = f.read()
                soup = BeautifulSoup(html_text, 'html.parser')
                target_lines = soup.findAll('pre')
                for target_line in target_lines:
                    sentence = target_line.text

            # json 파일을 읽어 json_data에 저장합니다.
            json_file_directory = os.path.join(json_directory, json_file)
            with open(json_file_directory, 'r', encoding = 'UTF-8') as f:
                json_data = json.load(f)

            # json_data에 entity가 없거나 2개 이상이면 dataframe에 문장만 입력합니다.
            if (not json_data['entities']) or len(json_data['entities']) > 2:
                df_2 = pd.DataFrame({"Id": [int(idx)], "sentence": [sentence], "subj_entity_type": [""], 
                                 "obj_entity_type": [""], "label" : [""]})

            # json_data에 entity가 1개라면 dataframe에 문장과 해당 entity만 입력합니다.
            elif len(json_data['entities']) == 1:
                entity, word = legend[json_data['entities'][0]['classId']], json_data['entities'][0]['offsets'][0]['text']
                entity_list = entity.split('-')
                new_word = "<{}>{}</{}>".format(entity_list[0], word, entity_list[0])
                sentence = sentence.replace(word, new_word)
                # subject entity만 있다면 subject entity만 입력합니다.
                if entity_list[0] == 'subj':
                    df_2 = pd.DataFrame({"Id": [int(idx)], "sentence": [sentence], "subj_entity_type": [entity_list[1].upper()], 
                                     "obj_entity_type": [""], "label" : [""]})
                # object entity만 있다면 object entity만 입력합니다.
                else:
                    df_2 = pd.DataFrame({"Id": [int(idx)], "sentence": [sentence], "subj_entity_type": [""], 
                                     "obj_entity_type": [entity_list[1].upper()], "label" : [""]})

            # json data에 entity가 2개라면 정상적으로 dataframe에 모든 정보를 입력합니다.
            else:
                entity_1, word_1 = legend[json_data['entities'][0]['classId']], json_data['entities'][0]['offsets'][0]['text']
                entity_2, word_2 = legend[json_data['entities'][1]['classId']], json_data['entities'][1]['offsets'][0]['text']

                # relation이 정의되어 있지 않다면 빈 문자열을 넣습니다.
                if not json_data['relations']:
                    label = ''
                else:
                    label = legend[json_data['relations'][0]['classId']]
                    
                entity_type_dict = defaultdict(str)
                entity_list_1, entity_list_2 = entity_1.split('-'), entity_2.split('-')
                entity_type_dict[entity_list_1[0]] = entity_list_1[1].upper()
                entity_type_dict[entity_list_2[0]] = entity_list_2[1].upper()
                
                new_word_1 = "<{}>{}</{}>".format(entity_list_1[0], word_1, entity_list_1[0])
                new_word_2 = "<{}>{}</{}>".format(entity_list_2[0], word_2, entity_list_2[0])
                
                # 문장 속의 entity 단어 양 옆에 entity 토큰을 붙입니다.
                sentence = sentence.replace(word_1, new_word_1)
                sentence = sentence.replace(word_2, new_word_2)
                
                df_2 = pd.DataFrame({"Id": [idx], "sentence": [sentence], "subj_entity_type": [entity_type_dict['subj']], 
                                     "obj_entity_type": [entity_type_dict['obj']], "label" : [label]})

            df = pd.concat([df,df_2], ignore_index = True)
            idx += 1

    df['Id'] = df['Id'].astype(int)

    return df
