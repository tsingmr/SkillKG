import os
import numpy as np
import random
from IO.io import *


class DataBase():
    def __init__(self,path):
        self.root_path = path
        self.rel_list = read_unary(os.path.join(self.root_path, "relations.txt"))
        self.gt_list = read_triple(os.path.join(self.root_path, "gt2id.txt"))
        self.rel_counts = self.count_relation()

    def output_split(self,train_list:list,valid_list:list,test_list:list,save_path=""):
        mkdir(os.path.join(self.root_path,save_path))
        splits = {"train.tsv": train_list, "dev.tsv": valid_list, "test.tsv": test_list}
        for split, l in splits.items():
            output_triple_txt(os.path.join(self.root_path, save_path, split), l)

    def count_relation(self):
        rel_counts = dict.fromkeys(self.rel_list,0)
        for triple in self.gt_list:
            rel_counts[triple[P]] += 1
        return rel_counts

    def unrepeated(self):
        unrepeated_list = []
        for triple in self.gt_list:
            if triple not in unrepeated_list:
                unrepeated_list.append(triple)
            else:
                print(triple)
        output_triple_txt(os.path.join(self.root_path,"gt2id_unrepeated.txt"),unrepeated_list)


