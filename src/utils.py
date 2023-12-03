import json
import os

from src.class_result import Result


def check_str(cur_str):
    for smb in cur_str:
        if not ('а' <= smb <= 'я'):
            return False

    return True


def open_txt(file_name):
    with open(file_name, 'r', encoding='UTF-8') as file:
        return file.read().splitlines()


def write(text, file_path):
    with open(file_path, 'w') as f:
        json.dump(text, f)


def open_json(file_name):
    with open(file_name) as file:
        return json.load(file)


def make_results():
    cur_dict = open_json(os.path.join('src', 'saved_results.json'))
    results = {}

    for key in cur_dict.keys():
        result = Result()

        result.name = cur_dict[key][0]
        result.win = cur_dict[key][1]
        result.game = cur_dict[key][2]

        results.update({key: result})

    return results


def right_spell(count):
    if count > 4:
        return "попыток"
    elif count == 1:
        return "попытка"
    else:
        return "попытки"


def rewrite_res(results):
    cur_dict = {}

    for key in results.keys():
        cur_dict.update({key: [results[key].name, results[key].win, results[key].game]})
        print(key, results[key].name, results[key].win, results[key].game)

    write(cur_dict, os.path.join('src', 'saved_results.json'))


def id_check(cur_id, results):
    for key in results:
        if key == str(cur_id):
            return True

    return False


def end_game(cur_id, name, win_fail, results):
    for key in results.keys():
        print(key, results[key].name, results[key].win, results[key].game)

    cur_id = str(cur_id)

    if not (id_check(cur_id, results)):
        res = Result()
        res.name = name
        res.game += 1
        if win_fail is True:
            res.win += 1
        results.update({cur_id: res})
    else:
        results[cur_id].game += 1
        if win_fail is True:
            results[cur_id].win += 1

    rewrite_res(results)


def cur_name_define(first_name, second_name):
    if second_name is None:
        cur_name = first_name
    elif first_name is None:
        cur_name = second_name
    else:
        cur_name = first_name + " " + second_name
    return cur_name

