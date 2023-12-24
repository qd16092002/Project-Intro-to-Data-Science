import json
import pickle

def read_json(file_path, encoding='utf8'):
    with open(file_path, 'r', encoding=encoding) as f:
        json_object = json.load(f)
    return json_object

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        pickle_object = pickle.load(f)
    return pickle_object

def save_item_line_by_line_json(items, file_path, encoding='utf8'):
    with open(file_path, 'w', encoding=encoding) as f:
        f.write('[\n')
        for i, item in enumerate(items):
            f.write(json.dumps(item, ensure_ascii=False))
            if i < len(items) - 1:
                f.write(',\n')
        f.write('\n]')
