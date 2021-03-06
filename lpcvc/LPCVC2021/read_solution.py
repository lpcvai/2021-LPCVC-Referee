import csv


def convert_frame_number_into_int(list_items):
    try:
        for i, item in enumerate(list_items):
            if 'Frame' in item:
                list_items[i]['Frame'] = int(item['Frame'])
    except ValueError:
        print('Error: Value Error Inside Code')
        exit()


def get_dict_from_solution(file_name):
    try:
        fp = open(file_name)
        csv_read = csv.DictReader(fp)
        response = [i for i in csv_read]
        convert_frame_number_into_int(response)
        fp.close()
    except FileNotFoundError:
        print('Error: File Does not Exists')
        response = None
        exit()
    return response
