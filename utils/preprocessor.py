import os
import json
from collections import defaultdict
import re

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils.entity_index import entity_index


def make_df(
    html_dir: str,
    html_files: list,
    json_dir: str,
    json_files: list,
    legend: dict,
) -> pd.DataFrame:
    """
    data directory에 저장되어 있는 html/json 파일들로부터
    [Id, sentence, subj_entity_type, obj_entity_type, label] 형식의 하나의 데이터프레임을 만듭니다.

    parameters
        html_dir, json_dir : html,json 파일이 저장되어 있는 directory
        html_files, json_files : html, json 파일 이름이 저장되어 있는 list
    """
    df = pd.DataFrame(
        {
            "Id": [],
            "sentence": [],
            "subj_entity_type": [],
            "obj_entity_type": [],
            "label": [],
        }
    )

    for idx, (html_file, json_file) in tqdm(
        enumerate(zip(html_files, json_files)), total=len(html_files)
    ):
        if html_file.split(".")[0] != json_file.split(".")[0]:
            # html 파일과 json 파일이 매칭되지 않는다면 종료합니다.
            print(
                "ERROR!!! {} html file does not match with {} json file.".format(
                    html_file.split(".")[0], json_file.split(".")[0]
                )
            )
            return None

        else:
            # html 파일을 읽어 sentence를 추출합니다.
            html_file_dir = os.path.join(html_dir, html_file)
            with open(html_file_dir, "r", encoding="UTF-8") as f:
                html_text = f.read()

            soup = BeautifulSoup(html_text, "html.parser")
            target_lines = soup.findAll("pre")
            for target_line in target_lines:
                sentence = target_line.text

            # json 파일을 읽어 json_obj에 저장합니다.
            json_file_dir = os.path.join(json_dir, json_file)
            with open(json_file_dir, "r", encoding="UTF-8") as f:
                json_obj = json.load(f)

            # json_obj에 entity가 없거나 2개 이상이면 dataframe에 문장만 입력합니다.
            if (not json_obj["entities"]) or len(json_obj["entities"]) > 2:
                df_2 = pd.DataFrame(
                    {
                        "Id": [idx],
                        "sentence": [sentence],
                        "subj_entity_type": [""],
                        "obj_entity_type": [""],
                        "label": [""],
                    }
                )

            # json_obj에 entity가 1개라면 dataframe에 문장과 해당 entity만 입력합니다.
            elif len(json_obj["entities"]) == 1:
                entity, word = (
                    legend[json_obj["entities"][0]["classId"]],
                    json_obj["entities"][0]["offsets"][0]["text"],
                )
                start = json_obj["entities"][0]["offsets"][0]["start"]
                len_word = len(word)
                entity_list = entity.split("-")
                new_word = "<{}>{}</{}>".format(entity_list[0], word, entity_list[0])
                sentence = sentence[:start] + new_word + sentence[start + len_word :]

                # subject entity만 있다면 subject entity만 입력합니다.
                if entity_list[0] == "subj":
                    df_2 = pd.DataFrame(
                        {
                            "Id": [idx],
                            "sentence": [sentence],
                            "subj_entity_type": [entity_list[1].upper()],
                            "obj_entity_type": [""],
                            "label": [""],
                        }
                    )

                # object entity만 있다면 object entity만 입력합니다.
                else:
                    df_2 = pd.DataFrame(
                        {
                            "Id": [idx],
                            "sentence": [sentence],
                            "subj_entity_type": [""],
                            "obj_entity_type": [entity_list[1].upper()],
                            "label": [""],
                        }
                    )

            # json data에 entity가 2개라면 정상적으로 dataframe에 모든 정보를 입력합니다.
            else:
                entity_1, word_1 = (
                    legend[json_obj["entities"][0]["classId"]],
                    json_obj["entities"][0]["offsets"][0]["text"],
                )
                start_1 = json_obj["entities"][0]["offsets"][0]["start"]
                entity_2, word_2 = (
                    legend[json_obj["entities"][1]["classId"]],
                    json_obj["entities"][1]["offsets"][0]["text"],
                )
                start_2 = json_obj["entities"][1]["offsets"][0]["start"]

                len_word_1, len_word_2 = len(word_1), len(word_2)

                # relation이 정의되어 있지 않다면 빈 문자열을 넣습니다.
                if not json_obj["relations"]:
                    label = ""
                else:
                    label = legend[json_obj["relations"][0]["classId"]]

                entity_type_dict = defaultdict(str)
                entity_list_1, entity_list_2 = entity_1.split("-"), entity_2.split("-")
                entity_type_dict[entity_list_1[0]] = entity_list_1[1].upper()
                entity_type_dict[entity_list_2[0]] = entity_list_2[1].upper()

                new_word_1 = "<{}>{}</{}>".format(
                    entity_list_1[0], word_1, entity_list_1[0]
                )
                new_word_2 = "<{}>{}</{}>".format(
                    entity_list_2[0], word_2, entity_list_2[0]
                )

                # 문장 속의 entity 단어 양 옆에 entity 토큰을 붙입니다.
                sentence = (
                    sentence[:start_1] + new_word_1 + sentence[start_1 + len_word_1 :]
                )
                new_start_2 = entity_index(word_2, start_2, sentence)
                sentence = (
                    sentence[:new_start_2]
                    + new_word_2
                    + sentence[new_start_2 + len_word_2 :]
                )

                df_2 = pd.DataFrame(
                    {
                        "Id": [idx],
                        "sentence": [sentence],
                        "subj_entity_type": [entity_type_dict["subj"]],
                        "obj_entity_type": [entity_type_dict["obj"]],
                        "label": [label],
                    }
                )

            df = pd.concat([df, df_2], ignore_index=True)

    df["Id"] = df["Id"].astype(int)

    return df
