# Hierarchical Representation in Robotic Manipulation: A Knowledge-based Framework

![overview](overview.png)

## Kgconstruction
This code is lastly tested with:
* python3.8

How to run
1. First create a folder to store the initial data: "./dataset-v6/demo", ensure that the folder contains an initial triplet file: "dataset-v6-raw-v6.txt"
2. Search DBpedia and run search_dbpedia.py to fetch new triples and new entities based on the data file you specify
3. Obtain the description of all nodes, run get_description.py, and manually correct the node as prompted
4. Integrate all the captured data and run process.py
And create the dataset according to the specified format: "./dataset-v6/demo/ReleaseForTest"
5. Run the split_raw_data.py command to split the data set according to the specified requirements. By default, the data set is divided randomly

## SkillKG
Data files generated during the construction of the dataset, including two searches of DBpedia, and the final version of SkillKG(triples: 11074) / SkillKG-meta(triples: 13154).

## Embedding
This code is lastly tested with:
* python 3.7.x
* pytorch 1.7.x
* torch_geometric 1.7.x, with torch_scatter 2.0.6 and torch_sparse 0.6.9