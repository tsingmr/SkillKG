import os
import openai
import random
import pickle
import json
import requests
import time
from IO.io import *
from data.triple_data import TripleData

openai.api_key = "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"


def translate(word):
    # 有道词典 api
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    # 传输的参数，其中 i 为需要翻译的内容
    key = {
        'type': "AUTO",
        'i': word,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "true"
    }
    # key 这个字典为发送给有道词典服务器的内容
    response = requests.post(url, data=key)
    # 判断服务器是否相应成功
    if response.status_code == 200:
        print(word)
        result = json.loads(response.text)
        # return result['translateResult'][0][0]['tgt']
        result = result['translateResult'][0]
        res = ""
        for pair in result:
            res += pair['tgt']
        print(res)
    else:
        print("有道词典调用失败")
        return None


def get_reuslt(repsonse):
    # 通过 json.loads 把返回的结果加载成 json 格式
    result = json.loads(repsonse)
    print("输入的词为：%s" % result['translateResult'][0][0]['src'])
    print("翻译结果为：%s" % result['translateResult'][0][0]['tgt'])


def WikiApi(word):
    key = word.replace("_", "+")
    url = "https://en.wikipedia.org/w/api.php?redirects&action=query&prop=extracts&explaintext&exintro&exsectionformat=plain&format=json&titles=" + key
    response = requests.post(url)
    if response.status_code == 200:
        result = json.loads(response.text)['query']['pages']
        # 如何获取字典的第一个value？ 一、将字典的values()转为可迭代对象后用next()，运行效率更高;二、将字典的values()转list后用索引取
        try:
            result = next(iter(result.values()))["extract"]
            print(word, ":", result)
            return result
        except:
            print(word, "wikiAPI不存在该词条")
            return None
    else:
        print(word, "wikiAPI调用失败")
        return None


def store_dict(dicts, filename):
    with open(filename, "wb") as f:
        pickle.dump(dicts, f)


def load_dict(filename):
    with open(filename, "rb") as f:
        dicts = pickle.load(f)
    return dicts


def store_map(symbol_map, filename):
    # 以字符串格式输出字典
    with open(filename, "w") as f:
        for index, symbol in symbol_map.items():
            f.write(f"{index}\t{symbol}\n")


def chatgptApi(word):
    key = word.replace("_", " ")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="tell me a most common definition of \"{}\" as a verb, please give me a short and clear answer.".format(
            key),
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )

    res = response.choices[0]["text"].replace("\n", "")
    print(key, ":", res)
    return res


def get_description_from_chatgpt(rootdir,save_path,triple_file,obj_no_desc,obj_not_in_wiki,output_file):
    """
    :param rootdir: current work dir
    :param save_path: save dir for output
    :param triple_file: raw triple's filename
    :param obj_no_desc: obj_no_desc's filename
    :param obj_not_in_wiki: obj_not_in_wiki's filename
    :param output_file: output's filename
    :return: a list contain all description pairs searched from chatGPT API
    """
    triple_data = TripleData(os.path.join(rootdir,triple_file))
    action_list = triple_data.get_action_without_hash()
    task_list = triple_data.get_task_list()
    """make sure you have [obj_no_desc.txt, obj_not_in_wiki.txt] in your work path"""
    obj_has_no_desc = read_unary(os.path.join(rootdir, obj_no_desc))
    obj_not_in_wiki = read_unary(os.path.join(rootdir, obj_not_in_wiki))

    entities_has_no_desc = action_list + obj_has_no_desc + obj_not_in_wiki
    entity_desc_pair = []
    for entity in entities_has_no_desc:
        res = chatgptApi(entity[:-2])
        entity_desc_pair.append([entity, res])
        time.sleep(1)
    for task_entity in task_list:
        desc = task_entity.lower().replace('_', ' ')[:-2]
        entity_desc_pair.append([task_entity, desc])
    output_tuple_txt(os.path.join(rootdir, save_path, output_file), entity_desc_pair)
    return entity_desc_pair


def integrate_all_description(rootdir,save_path,obj_desc_file,entity_desc_file,output_file):
    obj_desc_pairs = read_tuple(os.path.join(rootdir, save_path, obj_desc_file))
    entity_desc_pairs = read_tuple(os.path.join(rootdir,save_path,entity_desc_file))
    all_desc_pair = entity_desc_pairs + obj_desc_pairs
    output_tuple_txt(os.path.join(rootdir, save_path, output_file), all_desc_pair)


def check_all_description(rootdir,triple_file,all_desc_file):
    triple_data = TripleData(os.path.join(rootdir, triple_file))
    action_list = triple_data.get_action_without_hash()
    task_list = triple_data.get_task_list()
    obj_list = triple_data.get_obj_list()
    all_desc_pairs = read_tuple(os.path.join(rootdir,all_desc_file))
    entities_without_hash = obj_list + action_list + task_list
    check_dict = dict.fromkeys(entities_without_hash, -1)
    for i, pair in enumerate(all_desc_pairs):
        if pair[0] in check_dict.keys():
            if check_dict[pair[0]] == -1:
                check_dict[pair[0]] = i + 1
            else:
                print("the {}th row and the {}th row are repeated! please check it!".format(i + 1, check_dict[pair[0]]))
        else:
            print("the {}th row's entity not in dataset,please check it: {}".format(i + 1, pair[0]))
    for k in check_dict.keys():
        if check_dict[k] == -1 and k[-2:] != ".t":
            print("{} does not have description!".format(k))



if __name__ == "__main__":

    """Run the following three function step by step! """
    """Don't run the whole .py directly!"""

    """First: get description from chatGPT"""
    """at first you should specify the filename, then run the function"""
    # rootdir = "./dataset-v6/demo"
    # triple_file = "dataset-v6-raw-v6.txt"
    rootdir = "./dataset-v7"
    triple_file = "dataset-v7-raw-v2.txt"
    save_path = ''
    obj_has_no_desc = "obj_has_no_desc.txt"
    obj_not_in_wiki = "obj_not_in_wiki.txt"
    # output_file = "entity_desc.txt"
    entity_desc_pair = get_description_from_chatgpt(rootdir=rootdir,save_path=save_path,triple_file=triple_file,
                                                    obj_no_desc=obj_has_no_desc,obj_not_in_wiki=obj_not_in_wiki,
                                                    output_file="entity_desc.txt")

    """Second: integrate all description"""
    """make sure you have [obj_desc.txt, entity_desc.txt] in your work path,then run the function"""
    obj_desc_file = "obj_desc.txt"  # you can specify your own filename,the following is the same
    entity_desc_file = "entity_desc.txt"
    # output_file = "all_desc.txt"
    integrate_all_description(rootdir=rootdir,save_path=save_path,obj_desc_file=obj_desc_file,entity_desc_file=entity_desc_file,output_file="all_desc.txt")

    """At last: check description!!"""
    """this section will help you check [all_desc.txt], but you should check it in person"""
    all_desc_file = "descs_final.txt"
    check_all_description(rootdir=rootdir,triple_file=triple_file,all_desc_file=all_desc_file)

    """Once you make sure all description are ok and have check [all_desc.txt] in person, please run process.py"""


