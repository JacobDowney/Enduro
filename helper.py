import ujson
import pickle
import consts

def write_to_pickle(items, file_name):
    with open(file_name, 'wb') as pickle_file:
        pickle.dump(items, pickle_file)

def read_pickle(file_name):
    with open(file_name, 'rb') as pickle_file:
        return pickle.load(pickle_file)

def write_to_json(items, file_name):
    with open(file_name, "w") as json_file:
        ujson.dump(items, json_file)

def write_to_jsons(items1, file_name1, items2, file_name2):
    write_to_json(items1, file_name1)
    write_to_json(items2, file_name2)

def read_json(file_name):
    with open(file_name) as json_file:
        return ujson.load(json_file)

def update(message):
    with open(consts.updates_txt) as txt_file:
        # TODO(downeyj): write to txt
        x = 4


def is_mtb_ride(act):
    return act['type'] == 'Ride' and not act['trainer'] and not act['manual'] # and not act['commute']

def filter_enduros(activities):
    return [act for act in activities if is_mtb_ride(act)]

# Used to transform seconds integer into 'min:secs' string
def to_min_sec_str(time):
    min = str(int(time / 60))
    sec = str(time % 60)
    return '{}:{}'.format(min, sec.zfill(2))

def storage_type_functions(storage_type, pickle=None, database=None, json=None, none=None):
    # Choses between the different storage types and returns the function or
    # object based on that storage_type.
    if storage_type == consts.PICKLE:
        return pickle
    if storage_type == consts.DATABASE:
        return database
    if storage_type == consts.JSON:
        return json
    return none
