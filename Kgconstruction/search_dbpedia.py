from SPARQLWrapper import SPARQLWrapper, JSON
import os,requests,json,time
from IO.io import *
from data.triple_data import TripleData


sparql = SPARQLWrapper("https://dbpedia.org/sparql/")
important_rel_set = {'ingredient', 'hypernym'}  # 'region','main_ingredient', 'industry'


def filter_data(head,res):
    # head = ['p', 'o'] or  ['s', 'p']
    res_list = []
    for triple in res:
        rel = triple['p'].split('/')[-1]
        if rel in important_rel_set:
            triple['p'] = rel
            if 's' in head:
                triple['s'] = triple['s'].split('/')[-1]
            if 'o' in head:
                triple['o'] = triple['o'].split('/')[-1]
            res_list.append(triple)
    return res_list


def mySparql(keyword):
    print("searching {} from dbpedia api".format(keyword))
    query_po = """
    SELECT ?p ?o {
        <http://dbpedia.org/resource/""" + keyword + """>
            ?p ?o .
    FILTER(LANG(?o) = 'en' || !BOUND(LANG(?o)) )
    }
    """
    query_sp = """
    SELECT ?s ?p {
    	?s?p<http://dbpedia.org/resource/""" + keyword + """> .
    	FILTER(LANG(?s) = 'en' || !BOUND(LANG(?s)) )
    }
    """
    triple_list = []
    for query in [query_po]:  # for query in [query_po,query_sp]:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        try:
            res = sparql.query().convert()
        except Exception as e:
            print(e)
            return -1
        query_head, query_results = parse_result(res)
        triple_res = filter_data(query_head,query_results)
        triple_list.extend(triple_res)
    return triple_list


def parse_result(query_result):
    # 解析结果json，
    try:
        query_head = query_result['head']['vars']
        query_results = list()
        for r in query_result['results']['bindings']:
            temp_dict = dict()
            for h in query_head:
                temp_dict[h] = r[h]['value']
            query_results.append(temp_dict)
        return query_head, query_results
    except KeyError:
        return None, query_result['boolean']


def WikiApi(word):
    """
    :param word:
    :return: return a dict contain redirects and extract(description) of the input
    """
    key = word.replace("_","+")
    print("------------------------------------------")
    print("searching {} from wiki api".format(key))
    url = "https://en.wikipedia.org/w/api.php?redirects&action=query&prop=extracts&explaintext&exintro&exsectionformat=plain&format=json&titles="+key
    try:
        response = requests.get(url)
    except Exception as e:
        print(e)
        return -1
    res = {"redirects":None,"description":None}
    if response.status_code == 200:
        result = json.loads(response.text)['query']['pages']
        # 如何获取字典的第一个value？ 一、将字典的values()转为可迭代对象后用next()，运行效率更高;二、将字典的values()转list后用索引取
        try:
            extract = next(iter(result.values()))["extract"]
            print(word,":", "description:",extract)
            if extract.find("may refer to") == -1:
                res['description'] = extract.replace("\n"," ")
        except:
            print("wikiAPI不存在该词条")
            return None
        try:
            redirects = json.loads(response.text)['query']['redirects'][0]["to"]
            res['redirects'] = redirects
        except:
            pass
    else:
        print(word,"wikiAPI调用失败,请科学上网")
    return res


def main(obj_list:list,rootdir:str,save_path=""):
    db_triple_list = []  # new triple searched from DBpedia
    obj_desc_pairs = []  # [obj,description]
    obj_has_no_desc = []  # entity that has no description,please use chatgpt API by running get_description.py
    new_obj_list = []  # new entity searched from DBpedia
    obj_not_in_wiki = []


    for i,obj in enumerate(obj_list):
        time.sleep(4)
        keyword = obj.capitalize()
        keyword = keyword[0:-2]
        wiki_res = WikiApi(keyword)
        if wiki_res == -1:
            print("Before the {}th object have been searched".format(i))
            break
        if wiki_res is not None:
            if wiki_res['redirects'] is not None:
                keyword = wiki_res['redirects'].replace(' ', '_')
            if wiki_res['description'] is not None:
                obj_desc_pairs.append([obj, wiki_res['description']])
            else:
                obj_has_no_desc.append(obj)
        else:
            obj_not_in_wiki.append(obj)
            continue
        # time.sleep(3)
        # sparql_res = mySparql(keyword)
        # if sparql_res == -1:
        #     print("Before the {}th object have been searched".format(i))
        #     break
        # for triple in sparql_res:
        #     print(triple)
        #     if 'o' in triple.keys():
        #         tail_entity = triple['o'].lower() + ".o"
        #         if tail_entity not in obj_list and tail_entity not in new_obj_list:
        #             new_obj_list.append(tail_entity)  # 记录新增实体，以便后续的abstract扩充
        #         db_triple_list.append([obj, triple['p'], tail_entity])
        #     if 's' in triple.keys():
        #         head_entity = triple['s'].lower() + ".o"
        #         if head_entity not in obj_list and head_entity not in new_obj_list:
        #             new_obj_list.append(head_entity)  # 记录新增实体，以便后续的abstract扩充
        #         db_triple_list.append([head_entity, triple['p'], obj])

    output_triple_txt(os.path.join(rootdir, save_path, "db_triple_list.txt"), db_triple_list)
    output_tuple_txt(os.path.join(rootdir, save_path, "obj_desc.txt"), obj_desc_pairs)
    output_unary_txt(os.path.join(rootdir, save_path, "obj_no_desc.txt"), obj_has_no_desc)
    # output_unary_txt(os.path.join(rootdir, save_path, "new_obj_from_searching.txt"), new_obj_list)
    output_unary_txt(os.path.join(rootdir, save_path, "obj_not_in_wiki.txt"), obj_not_in_wiki)


if __name__ == '__main__':
    rootdir = "./dataset-v7"

    """if you want to search those entity from triple data"""
    # triple_data = TripleData(os.path.join(rootdir,"dataset-v7-raw-wo-db.txt"))
    # obj_list = triple_data.get_obj_list()
    # save_path = "first_search"
    # output_unary_txt(os.path.join(rootdir,"obj_list.txt"),obj_list)

    """if you want to search those entity from new entities"""
    obj_list = read_unary(os.path.join(rootdir,"descs_v2_entity.txt"))
    save_path = ""

    """obj_list for test"""
    # obj_list = ["dustbin.o","bottled_soy_sauce_cover.o","pot.o"]
    # save_path = ""

    main(obj_list,rootdir,save_path)


