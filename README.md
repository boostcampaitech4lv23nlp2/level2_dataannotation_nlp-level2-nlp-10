# 제2차세계대전 데이터 제작 Task
## :computer:프로젝트 소개
**RE(Relation Extraction) task**에 맞는 데이터 제작을 위해 팀원들이 공유할 수 있는 `csv 파일`을 생성하고 `IAA 계산` 및 `데이터 생성`을 목적으로 하는 프로젝트입니다.

## :clock1:프로젝트 기간
- 2022.12.05 ~ 2022.12.16

## :two_men_holding_hands:멤버 구성
- 김남규 : 작업환경 세팅
- 김산 : 데이터 취합 및 IAA 계산
- 엄주언 : 모델링, 데이터 평가
- 이동찬 : 발표, 가이드라인 작성
- 이정현 : 가이드라인 작성

## :wrench:개발환경
- `Ubuntu 18.04`
- `GPU v100`
- `Pytorch 1.12`

## :hammer:프로젝트 구조
    ├─ utils
    │  ├─ calculate_iaa.py
    │  ├─ iaa.py
    │  ├─ fleiss.py
    │  ├─ entity_index.py
    │  └─ preprocessor.py
    ├─ categories.json
    ├─ legend.json
    ├─ graph_notebbok.ipynb
    ├─ main.py
    ├─ iaa_main.py
    ├─ requirements.txt
    └─ .gitignore
   
## :pushpin:주요 기능
### 1. labeling을 위한 csv 파일 생성
- 주어진 데이터셋 문장들을 나누어 각 팀원이 `tagtog`을 사용하여 `subject_entity`와 `object_entity`, 그리고 그 둘의 `Relation`을 태깅한 zip파일을 준비합니다.
- 준비된 zip파일을 `data`폴더 안에 풀어줍니다.
- 다음 명령으로 코드를 실행하면 `result`폴더 안에 `sheet_{파일명}.csv`과 `sheet_{파일명}_no_label.csv`이 생성됩니다.
```shell
python main.py --file=파일명  ## 파일명 : tagging한 파일 이름 (ex. 강대국, 유대인 등)
```
  - `sheet_{파일명}.csv` : relation이 태깅된 파일
  - `sheet_{파일명}_no_label.csv` : relation이 태깅되지 않은 파일
- csv파일은 `[id, sentence, subject_entity, object_entity, label]`의 구조를 가집니다.
- 코드 실행 이후 압축해제한 폴더는 자동으로 삭제됩니다.
- 이후 `sheet_{파일명}_no_label.csv`을 공유하여 다른 팀원들이 태깅을 진행합니다.

### 2. IAA 계산
- 모든 데이터들에 대해 팀원들이 태깅한 csv파일들을 `data/annots`디렉토리 안에 넣어줍니다.
- 다음 코드를 실행하면 IAA 계산 결과를 출력합니다.(**Fleiss' Kappa** 사용)
```shell
python iaa_main.py
```
- 위 코드 실행 시 아래와 같은 결과를 출력합니다.
<img width="320" alt="Untitled (2)" src="https://user-images.githubusercontent.com/28773464/208367799-c59f2678-cc54-4b5c-85e1-dad32ce38a44.png">

- 코드 실행 시 `data`폴더 안에 `iaa_workers.xlsx`파일을 생성하며, 이는 IAA 계산을 위해 필요한 파일입니다.

### 3. 데이터 생성
- 모든 데이터들을 취합하여 모델에 input으로 사용할 수 있는 데이터 csv파일을 생성합니다.
- 아래 명령어로 실행할 수 있으며, 모델 입력으로 사용이 가능한 `data/total_data.csv`로 파일이 생성됩니다.
``` shell
python iaa_main.py --datagen True
```
- 데이터는 `[id, sentence, subject_entity, object_entity, label]`로 구성됩니다.

