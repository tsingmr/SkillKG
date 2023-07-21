import os
import numpy as np
import random
from IO.io import *
from data.dataset import *
from data.raw_data import *

if __name__ == "__main__":
    root_dir = "./dataset-v6/demo/ReleaseForTest"

    """split raw_data"""
    """please make sure you root dir have [gt2id.txt, relations.txt] !!!! """
    raw_data = RawData(root_dir)
    raw_data.split_by_random(factor=0.038)   # if you want to divide test:valid:train in 1:1:20, factor = 1/22 =0.454

    # meta_raw_data = RawData(os.path.join(root_dir,"SkillKG-meta"))
    # meta_raw_data.split_by_random(factor=0.038,save_path="v1")
    # meta_data.split_by_relation(increase_list=["from","into","on","with","in","beside","under"],decrease_list=["subject","instanceof"],save_path="v5",portion=0.2)

    """count splits"""
    """please make sure you root dir have train,valid,test !!!!"""
    dataset = Dataset(root_dir,train_split="train.tsv",test_split="test.tsv",valid_split="dev.tsv")
    dataset.count_relation_by_split()

    """adjust splits"""
    # meta_data = Dataset(os.path.join(root_dir, "SkillKG-meta"))
    # meta_data.unrepeated()
    # meta_data.move_relation_to_single_split(delete_rel=["instanceof"],ori_split=["test","dev"],tgt_split="train",save_path="v2")
    # meta_data = Dataset(os.path.join(root_dir, "SkillKG-meta", "v2"))
    # meta_data.count_relation_by_split()
    # meta_data.adjust_split_by_relation(increase_list=["subject"],decrease_list=["instanceof","object"],portion=0.052,save_path="v1")
    # meta_data.adjust_split_by_relation(increase_list=["next","object","from","into","contain","start","end","subject",
    #                                                   "on","with","in","beside","under","to","typeof","hypernym","ingredient",
    #                                                   "category",],decrease_list=["instanceof"],portion=0.0450)
    # meta_data.adjust_split_by_relation(increase_list=["contain"],decrease_list=["subject","instanceof"],portion=0.075,save_path="v8")
