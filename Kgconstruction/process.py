import os.path
import numpy as np
from IO.io import *


def delete_hash(s,k):
    if s[-2:] == '.a':
        ss = s[0:-9]+'.a'
        if ss == '.a' or ss[-3:] == "_.a":
            print("the {}th row err!".format(k), s)
            return s
        if ss not in actions:
            actions.append(ss)
        return ss
    else:
        return s


def store_map(symbol_map, filename):
    with open(filename, "w") as f:
        for symbol, index in symbol_map.items():
            f.write(f"{index}\t{symbol}\n")


def create_meta_node(s,unrepeated_meta_list):
    if s[-2:] == '.a':
        ss = s[0:-9]+'.a'
        res = [s,"instanceof",ss]
        if res not in unrepeated_meta_list:
            unrepeated_meta_list.append(res)
            return res
        else:
            return None
    else:
        return None


def text2id(triple_list,entities_map,relations_map):
    """
    all the triple become id, for example(a,to,b)->(1,0,2)
    :param triple_list:
    :param entities_map:
    :param relations_map:
    :return:
    """
    id_triples = []
    for triple in triple_list:
        id_triples.append([entities_map[triple[S]], relations_map[triple[P]], entities_map[triple[O]]])
    return id_triples


def entity2id(triple_list,entities_map):
    """
    only entity become id, for example(a,to,b)->(1,to,b)
    :param triple_list:
    :param entities_map:
    :return:
    """
    id_triples = []
    for triple in triple_list:
        id_triples.append([entities_map[triple[S]], triple[P], entities_map[triple[O]]])
    return id_triples


def process(rootdir,save_path,triple_file,desc_file):
    """
    this function specially produce dataset for Relphormer,if you want to produce dataset in your own format,
    please modify the function by yourself.
    :param rootdir:
    :param save_path:
    :param triple_file:
    :param desc_file:
    """
    ori_list = read_triple(os.path.join(rootdir, triple_file))
    triple_list = []
    tmp = []
    scenes = []
    actions = []
    agents = []
    entities = {}
    relations = {}
    objects = []
    locations = []
    ent_id = 0
    rel_id = 0
    S, P, O = 0, 1, 2
    unrepeated_meta_list = []

    for k, triple in enumerate(ori_list):
        if len(triple) == 3:
            # 删除哈希值
            # if WITHOUT_HASH == True:
            #     for i in [S,O]:
            #         triple[i] = delete_hash(triple[i],k)
            if CREATE_META_NODE == True:
                for i in [S, O]:
                    new_triple = create_meta_node(triple[i],unrepeated_meta_list)
                    if new_triple != None:
                        triple_list.append(new_triple)
            triple_list.append(triple)
        else:
            tmp.append(triple)
    print("num of illegal triples: {}".format(tmp))
    print("num of meta_action_triple: {}".format(len(unrepeated_meta_list)))

    for t in triple_list:
        if t[P] not in relations:
            relations[t[P]] = rel_id
            rel_id += 1
        for i in [S, O]:
            if t[i] not in entities:
                entities[t[i]] = ent_id
                ent_id += 1
                if t[i][-2:] == '.o':
                    objects.append(t[i])
                elif t[i][-2:] == '.a':
                    actions.append(t[i])
                elif t[i][-2:] == '.t':
                    scenes.append(t[i])
                elif t[i][-2:] == '.l':
                    locations.append(t[i])
                elif t[i][-2:] == '.i':
                    agents.append(t[i])
                elif t[i][-2:] == '.a':
                    pass
                else:
                    print("this node doesn't have label: {}".format(t[i]))
    # store_map(relations, os.path.join(rootdir, save_path, "relation_ids.txt"))

    """output the final dataset for training, different model need different format, you can make your own format """
    # the example of produce a dataset for Relphormer training
    store_map(entities, os.path.join(rootdir, save_path, "entity2text.txt"))
    output_unary_txt(os.path.join(rootdir, save_path, "entities.txt"), entities.values())
    output_unary_txt(os.path.join(rootdir, save_path, "relations.txt"), relations.keys())
    id_triples = entity2id(triple_list, entities)
    # id_triples = text2id(triple_list, entities, relations)
    output_triple_txt(os.path.join(rootdir, save_path, "gt2id.txt"), id_triples)
    rel_rel = []
    for relation in relations.keys():
        rel_rel.append([relation, relation])
    output_tuple_txt(os.path.join(rootdir, save_path, "relation2text.txt"), rel_rel)

    id_entities = read_tuple(os.path.join(rootdir, save_path, "entity2text.txt"))
    entity_desc_pair = read_tuple(os.path.join(rootdir, desc_file))
    id_entities_dict = dict(id_entities)
    entity_desc_dict = dict(entity_desc_pair)
    id_desc = []
    for id, entity in id_entities_dict.items():
        # if entity[-2:] == ".t":
        #     desc = entity.lower().replace("_"," ")[:-2]
        # else:
        if entity[-2:] == ".a" and entity not in entity_desc_dict.keys():  # if this entity is action node with hash
            keyword = entity[0:-9] + '.a'  # delete hash
        else:
            keyword = entity
        try:
            if keyword[-2:] == ".t":
                desc = keyword
            else:
                desc = entity_desc_dict[keyword]
        except:
            print("{} does not have a desc!".format(keyword))
            exit()
        id_desc.append([id, desc])
    output_tuple_txt(os.path.join(rootdir,save_path,"entity2textlong.txt"),id_desc)

    # if WITHOUT_HASH == True:
    #     without_hash_filename = "without_hash_v2.txt"
    #     path = os.path.join(rootdir, without_hash_filename)
    #     output_triple_txt(path,triple_list)

    with open(os.path.join(rootdir, save_path, "data_info.txt"), "w") as f:
        f.write("num of triples: {}\n".format(len(triple_list)))
        f.write("num of entities: {}\n".format(len(entities)))
        f.write("num of relations: {}\n".format(len(relations)))
        f.write("--------------------------------------\n")
        f.write("num of scenes: {}\n".format(len(scenes)))
        for scene in scenes:
            f.write(str(scene) + "\n")
        f.write("--------------------------------------\n")
        f.write("num of actions:{}\n".format(len(actions)))
        for action in actions:
            f.write(str(action) + "\n")
        f.write("--------------------------------------\n")
        f.write("num of objects:{}\n".format(len(objects)))
        for obj in objects:
            f.write(str(obj) + "\n")
        f.write("--------------------------------------\n")
        f.write("num of locations:{}\n".format(len(locations)))
        for loc in locations:
            f.write(str(loc) + "\n")
        f.write("--------------------------------------\n")
        f.write("num of agents:{}\n".format(len(agents)))
        for agt in agents:
            f.write(str(agt) + "\n")


if __name__ == "__main__":


    CREATE_META_NODE = True

    """Make sure your current work dir have triple_file and description_file, then run the function: process()"""
    rootdir = "./dataset-v7"
    save_path = "SkillKG-meta"
    triple_file = "dataset-v7-raw-v2.txt"
    desc_file = "descs_final.txt"
    process(rootdir=rootdir,save_path=save_path,triple_file=triple_file,desc_file=desc_file)
