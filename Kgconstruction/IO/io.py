import os

S,P,O = 0, 1, 2

def mkdir(save_path):
    if not os.path.exists(save_path):
        os.mkdir(save_path)

def read_triple(path):
    with open(path,"r",encoding="utf_8") as f:
        ori_list = list(map(lambda s: s.strip().split("\t"), f.readlines()))
    res = []
    for i,t in enumerate(ori_list):
        if len(t) == 3:
            res.append(t)
        else:
            # tmp.append(ori_list[i])
            print("the {}th triple is illegal".format(i))
    print("{} triple have been read from {}".format(len(res), path))
    return res

def read_tuple(path):
    with open(path,"r",encoding="utf_8") as f:
        ori_list = list(map(lambda s: s.strip().split("\t"), f.readlines()))
    res = []
    for i,t in enumerate(ori_list):
        if len(t) == 2:
            res.append(t)
        else:
            print("the {}th tuple is illegal".format(i))
    print("{} tuple have been read from {}".format(len(res), path))
    return res

def read_unary(path):
    with open(path,"r",encoding="utf_8") as f:
        ori_list = list(map(lambda s: s.strip(), f.readlines()))

    res = []
    for i in range(len(ori_list)):
        res.append(ori_list[i])
    print("{} unary have been read from {}".format(len(res),path))
    return res

def output_triple_txt(path,triple_list):
    with open(path, "w", encoding='utf-8') as f:
        for triple in triple_list:
            f.write(
                str(triple[0])
                + "\t" +
                str(triple[1])
                + "\t" +
                str(triple[2])
                + "\n"
            )

def output_tuple_txt(path,tuple_list):
    with open(path,"w",encoding='utf-8') as f:
        for tuple in tuple_list:
            f.write(str(tuple[0]) + "\t" + str(tuple[1]) + "\n")

def output_unary_txt(path,unary_list):
    with open(path,"w",encoding='utf-8') as f:
        for unary in unary_list:
            f.write(str(unary) + "\n")