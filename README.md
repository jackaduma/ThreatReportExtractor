<!--
 * @Author: Kun
 * @Date: 2021-09-16 11:11:28
 * @LastEditTime: 2021-09-22 10:09:59
 * @LastEditors: Kun
 * @Description: 
 * @FilePath: /ThreatReportExtractor/README.md
-->

# ThreatReportExtractor
Extracting Attack Behavior from Threat Reports

## environment

support python3; not support python2

### download model for spacy

python -m spacy download en_core_web_lg 


### download nltk when setting param crf is false

import nltk

nltk.download('averaged_perceptron_tagger')

# contain submodules

cd $PROJECT_HOME

git submodule init

git submodule update



### allennlp 的 pretrain model


wget -c -t 0 https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz


mv srl-model-2018.05.25.tar.gz srl-model.tar.gz  # 当前目录下


### install graphviz
Linux: 

Ubuntu: sudo apt install graphviz

Fedora: sudo yum install graphviz

Debian: sudo apt install graphviz

Redhat/Centos: sudo yum install graphviz # Stable and development rpms for Redhat Enterprise, or CentOS systems* available but are out of date.

Mac:

sudo port install graphviz

brew install graphviz


### Command parameters

Run EXTRACTOR with `python3 main.py [-h] [--asterisk ASTERISK] [--crf CRF] [--rmdup RMDUP] [--elip ELIP] [--gname GNAME] [--input_file INPUT_FILE]`.

Depending on the usage, each argument helps to provide a different representation of the attack behavior. 
`[--asterisk true]` creates abstraction and can be used to replace anything that is not perceived as IOC/system entity into a wild-card. This representation can be used to be searched within the audit-logs.  

`[--crf true/false]` allows activating or deactivating of the co-referencing module. 

`[--rmdup true/false]` enables removal of duplicate nodes-edge. 

`[--elip true/false]` is to choose whether to replace ellipsis subjects using the surrounding subject or not.

`[--input_file path/filename.txt]` is to pass the text file to the application. 

`[--gname graph_name]` is to specify the name output graph (two files will be created, e.g., graph.pdf and graph.dot).


#### Example
`python3 main.py --asterisk true --crf true --rmdup true --elip true --input_file input.txt --gname mygraph`


python main.py --asterisk false --crf false --rmdup false --input_file input.txt # 生成了dot和pdf，但是节点过多了吧

python main.py --asterisk false --crf true --rmdup false --input_file input.txt # 太耗费资源了 算不出来！！！ WTF

python main.py --asterisk true --crf true --rmdup true --elip true --input_file input.txt --gname mygraph # crf 这个参数 需要再研究下，特别的慢 是因为 neuralcoref 这个package吗？

python main.py --asterisk true --crf false --rmdup true --elip true --input_file input.txt --gname mygraph # 

### graphviz generate image file

dot pic.dot -T png -o pic.png