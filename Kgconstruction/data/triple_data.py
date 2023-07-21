import os
from IO.io import *


class TripleData():
    def __init__(self, path):
        self.root_path = path
        self.triple_list = read_triple(path)

    def get_obj_list(self):
        """
        :return: a list contain all nodes exclude action node and task node for DBpedia searching
        """
        obj_list = []
        for t in self.triple_list:
            for i in [S, O]:
                if t[i] not in obj_list and t[i][-2:] in ['.o', '.l', '.i']:
                    obj_list.append(t[i])
        return obj_list

    def delete_hash(self,s,k):
        if s[-2:] == '.a':
            ss = s[0:-9] + '.a'
            if ss == '.a' or ss[-3:] == "_.a":
                print("the {}th row err!".format(k), s)
                return None
            return ss
        else:
            return None

    def get_action_without_hash(self):
        """
        :return: a list contain all action nodes without hash
        """
        actions_without_hash = []
        for k, triple in enumerate(self.triple_list):
            # 删除哈希值
            for i in [S, O]:
                action = self.delete_hash(triple[i],k)
                if action is not None:
                    if action not in actions_without_hash:
                        actions_without_hash.append(action)
        return actions_without_hash

    def get_task_list(self):
        """
        :return: a list contain all task nodes
        """
        task_list = []
        for t in self.triple_list:
            for i in [S, O]:
                if t[i] not in task_list and t[i][-2:] == '.t':
                    task_list.append(t[i])
        return task_list

    def get_triples_without_relations(self,del_rel:list):
        triples = []
        for triple in self.triple_list:
            if triple[P] not in del_rel:
                triples.append(triple)
        return triples

    def get_triples_in_relations(self,rels:list):
        triples = []
        for triple in self.triple_list:
            if triple[P] in rels:
                triples.append(triple)
        return triples
