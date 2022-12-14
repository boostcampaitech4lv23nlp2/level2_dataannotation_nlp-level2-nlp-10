import os
import shutil
import argparse
import json
import re
import pandas as pd
from utils.preprocessor import make_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="파일 이름")
    arg = parser.parse_args()

    f = open("./legend.json", "r")
    legend = json.load(f)
    f.close()

    html_dir = os.path.join("./data/RE_task_dataset/plain.html/pool", arg.file)
    json_dir = os.path.join("./data/RE_task_dataset/ann.json/master/pool", arg.file)
    html_files = sorted(os.listdir(html_dir))
    json_files = sorted(os.listdir(json_dir))

    result = make_df(html_dir, html_files, json_dir, json_files, legend)
    result_no_label = result.copy()
    result_no_label["label"] = ""

    result.to_csv("./result/sheet_{}.csv".format(arg.file), index=False)
    result_no_label.to_csv(
        "./result/sheet_{}_no_label.csv".format(arg.file), index=False
    )

    shutil.rmtree("./data/RE_task_dataset")


if __name__ == "__main__":
    main()
