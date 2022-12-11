# 제2차세계대전 데이터 제작 Task

## 코드의 목적
- tagtog으로 각자 tagging한 파일을 스프레드시트에서 tagging이 가능하도록 csv파일을 만들기 위함

## CSV 파일 구조
- Id, sentence, subject_entity_type, object_entity_type, label

## 코드 실행 시 Output
- sheet_{파일명}.csv
  - relation이 태깅된 파일
- sheet_{파일명}_no_label.csv
  - relation 태깅되지 않은 파일

## How to use
- tagtog으로 태깅한 zip파일을 저장하고 해당 zip파일을 data 디렉토리에 압축풀기
  
```shell
python main.py --file=파일명
```

- 파일명은 본인이 tagtog에서 담당한 파일 이름(ex.강대국, 유대인 등)

- 결과 csv 파일은 result 디렉토리에 저장

- 결과 파일 저장 완료 후 data 디렉토리에 저장되었던 압축해제폴더는 자동삭제
