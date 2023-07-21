import os
import numpy as np
import random
from IO.io import *
from data.data_base import DataBase


class Dataset(DataBase):
    def __init__(self, path,train_split="train.tsv",valid_split="dev.tsv",test_split="test.tsv"):
        super().__init__(path)
        self.test_list = read_triple(os.path.join(self.root_path, test_split))
        self.valid_list = read_triple(os.path.join(self.root_path, valid_split))
        self.train_list = read_triple(os.path.join(self.root_path, train_split))

    def count_relation_by_split(self):
        splits = {"train":self.train_list, "valid":self.valid_list, "test":self.test_list}
        for split_name, split in splits.items():
            count_dict = dict.fromkeys(self.rel_list, 0)
            for triple in split:
                count_dict[triple[P]] += 1
            print("{} split's stats as follow:".format(split_name))
            stats = ""
            for rel,count in count_dict.items():
                stats += "{}: {}\t".format(rel,count)
            print(stats)

    def adjust_split_by_relation(self, increase_list:list, decrease_list:list, portion=0.1, save_path=""):
        """
        :param increase_list: relation to increase in test/valid
        :param decrease_list: relation to decrease in train
        :param portion: portion of the num of specified relation in test/valid, like train:valid:test=2:1:1,portion=0.25
        """
        train_list = self.train_list
        valid_list = self.valid_list
        test_list = self.test_list
        num_of_tgt_rel = dict()
        tgt_rel_in_train = dict.fromkeys(increase_list,
                                         [])  # those triples in train split can be added to valid or test
        for tgt_rel in increase_list:
            num_of_tgt_rel[tgt_rel] = int(self.rel_counts[tgt_rel] * portion)
        for triple in train_list:
            if triple[P] in increase_list:
                tgt_rel_in_train[triple[P]].append(triple)
        for split in [valid_list, test_list]:
            decrease_gt_list = []   # those triples in valid or test split can be replaced by tgt triple
            num_of_increase_rel = dict.fromkeys(increase_list, 0)  # those triples in valid/test that have target relation to increase
            for triple in split:
                if triple[P] in decrease_list:
                    decrease_gt_list.append(triple)
                    continue
                if triple[P] in increase_list:
                    num_of_increase_rel[triple[P]] += 1
            for tgt_rel in increase_list:
                num_of_replace_triple = num_of_tgt_rel[tgt_rel] - num_of_increase_rel[tgt_rel]  # 需要替换的次数=目标数量-现有数量
                if num_of_replace_triple < 0:
                    continue
                if len(decrease_gt_list) < num_of_replace_triple:
                    print("num of replace triple is not enough!!!")
                    print("please increase num of decrease_list or decrease num of increase_list!!!")
                    exit()
                for i in range(num_of_replace_triple):
                    triple_to_replace = tgt_rel_in_train[tgt_rel].pop()
                    train_list.remove(triple_to_replace)
                    split.append(triple_to_replace)
                    triple_to_be_replaced = decrease_gt_list.pop()
                    split.remove(triple_to_be_replaced)
                    train_list.append(triple_to_be_replaced)
        self.output_split(train_list=train_list, valid_list=valid_list, test_list=test_list, save_path=save_path)

    def split_map(self,split_name:str):
        if split_name == "train":
            return self.train_list
        if split_name == "valid" or split_name == "dev":
            return self.valid_list
        if split_name == "test":
            return self.test_list

    def move_relation_to_single_split(self,delete_rel:list,ori_split:list,tgt_split:str,save_path=""):
        mkdir(os.path.join(self.root_path,save_path))
        tgt_list = self.split_map(tgt_split)
        for split in ori_split:
            ori_list = self.split_map(split)
            for triple in ori_list:
                if triple[P] in delete_rel:
                    ori_list.remove(triple)
                    tgt_list.append(triple)
            output_triple_txt(os.path.join(self.root_path,save_path,split+".tsv"),ori_list)
        output_triple_txt(os.path.join(self.root_path,save_path,tgt_split+".tsv"),tgt_list)

