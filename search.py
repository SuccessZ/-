from py2neo import Graph,RelationshipMatcher,NodeMatcher
import json
import ahocorasick
import os

class MedicalSearch():
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.name_type_path = os.path.join(self.path,'name_type.txt')     #确定数据路径
        self.key_words_path = os.path.join(self.path,'key_words.txt')     
        self.graph = Graph('http://localhost:7474',auth = ('neo4j','zyp12345'))     #连接neo4j
        self.nodeMatcher = NodeMatcher(self.graph)      #节点匹配，用来寻找节点
        self.relMatcher = RelationshipMatcher(self.graph)   #关系匹配，结合节点匹配可以找到与该节点有关的所有节点及关系
        self.key_words = json.load(open(self.key_words_path))    #读取name-type对应表
        self.name_type = json.load(open(self.name_type_path))
        self.actree = self.build_actree(self.key_words.keys())  #模式匹配

    def build_actree(self,words):   #模式匹配
        actree = ahocorasick.Automaton()
        for word in words:
            actree.add_word(word, word)
        actree.make_automaton()
        return actree

    def answer(self,question):  #回答问题
        answer_list = []
        for key_word in self.actree.iter(question): #利用模式匹配找到问题中出现的关键词
            key_word = key_word[1]
            for name in self.key_words[key_word]:   #根据关键词找到相关商品/卖家名称
                for type in self.name_type[name]:   #标准化格式为[name，所属的节点类型]
                    answer_list.append([name,type])

        node_list = []
        for answer in answer_list:
            nodes = list(self.nodeMatcher.match(answer[1]).where(name=answer[0]))   #根据name找到该节点
            rel = list(self.relMatcher.match(nodes,r_type=None))    #找到与该节点相关的节点及关系
            for node in rel:
                node_list.append(str(node))

        if len(node_list) > 0:
            return '与该点有关联的节点及关系为: '+'\t'.join(node_list)  #将结果拼接为字符串
        else:
            return '没有与该点有关联的节点及关系'



if __name__ == '__main__':
    _search = MedicalSearch()
    print(_search.answer('黄片'))


    # while 1:
    #     question = input('输入关键词:')
    #     answer = _search.answer(question)
    #     print('客服机器人:', answer)
