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

    def test_annot_validity(self, target_category):
        pass
