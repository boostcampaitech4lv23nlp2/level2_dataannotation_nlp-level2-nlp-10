class IAA:
    def __init__(self, annot_path='data/annots/', categories_path='categories.json', legend_path='legend.json', target_category=None):
        if target_category is None:
            self.categories = load_categories(categories_path)
        else:
            self.categories = target_category
        self.legend = load_legend(legend_path)
        xls_list = [os.path.join(annot_path, file) for file in os.listdir(annot_path) if '.xlsx' in file]
        self.annot_list = [pd.read_excel(xls_path, sheet_name=None) for xls_path in xls_list]
        self.workers = len(xls_list)
        self.test_annot_validity(target_category)

    def test_annot_validity(self):
        validity = True
        error_msg = ''
        for category in self.categories:
            valid_check = np.array([])
            for annot in self.annot_list:
                sheetname = self.get_sheetname(annot.keys(), category)
                valid_values = annot[sheetname]['valid_check'].values
                if valid_check.size == 0:
                    valid_check = valid_values.copy()
                else:
                    if np.array_equal(valid_check, valid_values) is False:
                        validity = False
                        indices = np.where((valid_check == valid_values) == False)
                        error_msg += f'{category}에서 valid_error가 서로 다른 항목이 존재합니다. -> {indices}\n'
        if validity is False:
            raise Exception(error_msg)
            
    def get_sheetname(self, sheets, category):
        for sheet in sheets:
            if category in sheet:
                return sheet
        raise Exception(f'{category}와 매칭되는 sheet가 없습니다.')