import os
import numpy as np
import random
from IO.io import *
from data.data_base import DataBase


class RawData(DataBase):
    def __init__(self, path):
        super().__init__(path)

    def split_by_relation(self, increase_list:list, decrease_list:list, factor=0.07, portion=0.2,save_path=""):
        # first:split raw_data randomly
        train_list, valid_list, test_list = self.split_randomly(factor)

        # second:adjust split by increase_list and decrease_list
        num_of_tgt_rel = dict()
        tgt_rel_in_train = dict.fromkeys(increase_list,[])  # those triples in train split can be added to valid or test
        for tgt_rel in increase_list:
            num_of_tgt_rel[tgt_rel] = int(self.rel_counts[tgt_rel]*portion)
        for triple in train_list:
            if triple[P] in increase_list:
                tgt_rel_in_train[triple[P]].append(triple)
        for split in [valid_list,test_list]:
            decrease_gt_list = []  # those triples in valid or test split can be replaced by tgt triple
            num_of_increase_rel =dict.fromkeys(increase_list,0)
            for triple in split:
                if triple[P] in decrease_list:
                    decrease_gt_list.append(triple)
                    continue
                if triple[P] in increase_list:
                    num_of_increase_rel[triple[P]] += 1
            for tgt_rel in increase_list:
                num_of_replace_triple = num_of_tgt_rel[tgt_rel]-num_of_increase_rel[tgt_rel]  # 需要替换的次数=目标数量-现有数量
                if num_of_replace_triple <= 0:
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
        self.output_split(train_list=train_list,valid_list=valid_list,test_list=test_list,save_path=save_path)

    def split_randomly(self,factor=0.07):
        tmp_list = self.gt_list
        random.shuffle(tmp_list)
        test_size = int(len(tmp_list)*factor)
        valid_list = tmp_list[0:test_size]
        test_list = tmp_list[test_size:test_size*2]
        train_list = tmp_list[test_size*2:]
        return train_list,valid_list,test_list

    def split_by_random(self, factor=0.07, save_path=""):
        train_list, valid_list, test_list = self.split_randomly(factor)
        self.output_split(train_list=train_list,valid_list=valid_list,test_list=test_list,save_path=save_path)