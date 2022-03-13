from asyncio.windows_events import NULL
from email import iterators
import os
import json
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
from py2neo import Node,Graph,NodeMatcher,Relationship
import pandas as pd

class LtpParser:
    def __init__(self):

        path = os.path.dirname(os.path.abspath(__file__))
        LTP_DIR = os.path.join(path,'ltp_data_v3.4.0')     #确定数据路径
        self.segmentor = Segmentor()
        self.segmentor.load(os.path.join(LTP_DIR, "cws.model"))

        self.postagger = Postagger()
        self.postagger.load(os.path.join(LTP_DIR, "pos.model"))

    def get_words(self,name):
        allowed_list = ['ni','n','nh','j','nl','ns','nz']
        words = list(self.segmentor.segment(name))
        postags = list(self.postagger.postag(words))
        return_list = []
        for i in range(len(postags)):
            if postags[i] in allowed_list:
                return_list.append(words[i])
        return return_list
            

        
class MedicalGraph:
    def __init__(self):      
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.path,'chinese_market.csv')     #确定数据路径
        self.graph = Graph('http://localhost:7474',auth = ('neo4j','zyp12345'))     #连接neo4j
        # self.graph.run('MATCH (n) DETACH DELETE n')     #删除之前存在的记录
        self.key_words = {} #关键字-节点name对应字典
        self.name_type = {} #节点name-类型对应字典
        self.parser = LtpParser()

    def read_nodes(self):
        #节点列表
        good_list = []      #商品节点
        img_list = []     #图片节点
        market_list = []    #市场节点
        index_list = []     #索引节点
        seller_list = []    #买房节点
        #关系列表
        good_index_rel = []     #商品查询所用的索引 
        good_img_rel = []     #商品使用的图片
        good_market_rel = []   #商品售卖的市场
        good_seller_rel = []    #商品的卖方

        data_frame = pd.read_csv(self.data_path,encoding='gbk',keep_default_na=False)
        for i,data in data_frame.iterrows():
            good = dict()
            img = dict()
            market = dict()
            index = dict()
            seller = dict()

            ## 商品节点属性
            if not data['_id'] == '':     
                good['_id'] = str(data['_id'])
            if not data['_score'] == '':
                good['_score'] = str(data['_score'])
            if not data['_type'] == '':
                good['_type'] = str(data['_type'])
            if not data['gmt_create'] == '':
                good['gmt_create'] = str(data['gmt_create'])
            if not data['gmt_modified'] == '':
                good['gmt_modified'] = str(data['gmt_modified'])
            if not data['goods_bt_price'] == '':
                good['bt_price'] = str(data['goods_bt_price'])
            if not data['goods_comment'] == '':
                good['comment'] = str(data['goods_comment'])
            if not data['goods_description'] == '':
                good['description'] = str(data['goods_description'])
            if not data['goods_id'] == '':
                good['id'] = str(data['goods_id'])
                name = str(data['goods_name']).split(' - ')
                good['name'] = name[1]
                good['category'] = name[0]
                if name[0] in self.key_words.keys():    #将商品类别也作为关键词存储在key_words字典中，value是该商品的名字
                    self.key_words[name[0]].append(good['name'])
                else:
                    self.key_words[name[0]] = [good['name']]
                words = self.parser.get_words(name[1])  #从商品名字中提取关键词，关键词作为key_words字典中的一个key值，value是该商品的名字
                for word in words:
                    if word in self.key_words.keys():
                        self.key_words[word].append(good['name'])
                    else:
                        self.key_words[word] = [good['name']]
                if good['name'] in self.name_type.keys():   #将该name对应的type存储在name_type字典中
                    self.name_type[good['name']].append('good')
                else:
                    self.name_type[good['name']] = ['good']

            if not data['goods_price'] == '':
                good['price'] = str(data['goods_price'])
            if not data['goods_seller_last_online'] == '':
                good['seller_last_online'] = str(data['goods_seller_last_online'])
            if not data['goods_sold_num'] == '':
                good['sold_num'] = str(data['goods_sold_num'])
            if not data['goods_status'] == '':
                good['status'] = str(data['goods_status'])
            if not data['goods_time'] == '':
                good['time'] = str(data['goods_time'])
            if not data['goods_url'] == '':
                good['url'] = str(data['goods_url'])
            if not data['snap'] == '':
                good['snap'] = str(data['snap'])
            if not data['goods_name'] == '':
                name = str(data['goods_name']).split(' - ')
                good['name'] = name[1]
                good['category'] = name[0]
                good_list.append(good)

                #索引节点
                if not data['_index'] == '':
                    index['name'] = str(data['_index']) 
                    index_list.append(index)
                    good_index_rel.append([good['name'],index['name']])
                
                #图片节点
                if not data['goods_img_url'] == '':
                    img['url'] = str(data['goods_img_url'])
                if not data['goods_img_name'] == '':
                    img['name'] = str(data['goods_img_name'])
                    img_list.append(img)
                    good_img_rel.append([good['name'],img['name']])


                #卖方节点
                if not data['goods_seller'] == '':
                    seller['name'] = str(data['goods_seller'])
                    seller_list.append(seller)
                    good_seller_rel.append([good['name'],seller['name']])
                    if seller['name'] in self.key_words.keys():     #将卖家代号也作为关键词存储在key_words字典中，value是卖家代号
                        self.key_words[seller['name']].append(seller['name'])
                    else:
                        self.key_words[seller['name']] = [seller['name']]
                    if seller['name'] in self.name_type.keys():     #将该name对应的type存储在name_type字典中
                        self.name_type[seller['name']].append('seller')
                    else:
                        self.name_type[seller['name']] = ['seller']

                #市场节点
                if not data['goods_origin_website'] == '':
                    market['url'] = str(data['goods_origin_website'])
                if not data['goods_origin_website_name'] == '':
                    market['name'] = str(data['goods_origin_website_name'])
                    market_list.append(market)
                    good_market_rel.append([good['name'],market['name']])
                    if market['name'] in self.key_words.keys():
                        self.key_words[market['name']].append(good['name'])
                    else:
                        self.key_words[market['name']] = [good['name']]


        good_list = self.deduplicate(good_list,'name')
        index_list = self.deduplicate(index_list,'name')
        seller_list = self.deduplicate(seller_list,'name')
        market_list = self.deduplicate(market_list,'name')
        img_list = self.deduplicate(img_list,'name')

        return good_list,index_list,img_list,seller_list,market_list,good_img_rel,good_index_rel,good_market_rel,good_seller_rel

    def deduplicate(self,dict_list,key):    #dict_list是一个列表，列表中元素类型为字典，key是判断不同字典是否相同的唯一标准
        seen = set()
        new_list = []
        for _dict in dict_list:
            value = _dict[key]
            if value not in seen:
                seen.add(value)
                new_list.append(_dict)
        return new_list

    def swap(self,_list):   #对_list中的每个列表元素中的内容前后调换
        _list = _list[::]
        for each in _list:
            temp = each[0]
            each[0] = each[1]
            each[1] = temp
        return _list[::]

    def create(self):   #将节点与边添加到途中
        good_list,index_list,img_list,seller_list,market_list,good_img_rel,good_index_rel,good_market_rel,good_seller_rel = self.read_nodes()
        self.create_node(good_list,'good')
        self.create_node(index_list,'index')
        self.create_node(img_list,'img')
        self.create_node(seller_list,'seller')
        self.create_node(market_list,'market')
        self.nodeMatcher = NodeMatcher(self.graph)      #节点匹配，用来寻找节点

        self.create_relation('good','index',good_index_rel,'index')
        self.create_relation('good','img',good_img_rel,'use')
        self.create_relation('good','market',good_market_rel,'is sold on')
        self.create_relation('good','seller',good_seller_rel,'is sold by')
        self.create_relation('seller','good',self.swap(good_seller_rel),'sell')
        print('Graph is finished ...... ')
        return

    def create_node(self,node_list,node_type):  #按照给定的节点列表创造节点
        for _node in node_list:
            node = Node(node_type)
            node.update(_node)
            self.graph.create(node)
        return
    
    def create_relation(self,start_node,end_node,edge_list,rel_type):   #按照给定的关系列表创造边
        # 对关系列表查重，关系列表中元素类型是列表，列表中两个值共同作为该元素的唯一标志
        edge_set = set()
        for edge in edge_list:
            edge_set.add('###'.join(edge))
        
        for edge in edge_set:
            # 恢复因查重而更改的数据形式
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            p = self.nodeMatcher.match(start_node).where(name=p).first()    #找到其实节点
            q = self.nodeMatcher.match(end_node).where(name=q).first()      #找到终至节点
            rel = Relationship(p,rel_type,q)       #创建关系
            self.graph.create(rel)

            # 匹配到符合条件的节点，之后创造关系（边）
            
        return

   
    def export_data(self):  #输出名字-类型对应字典和关键字-名字字典
        for key in self.key_words.keys():   #对某一个名字对应的类型去重
            self.key_words[key] = list(set(self.key_words[key]))
        with open(os.path.join(self.path,'key_words.txt'),'w',encoding='gbk') as fp:
            json.dump(self.key_words,fp)

        for key in self.name_type.keys():   #对某一个名字对应的类型去重
            self.name_type[key] = list(set(self.name_type[key]))
        with open(os.path.join(self.path,'name_type.txt'),'w',encoding='gbk') as fp:
            json.dump(self.name_type,fp)
        return
 

if __name__ == '__main__':
    # gragh = MedicalGraph()
    # gragh.create()
    # gragh.export_data()
    parse = LtpParser()
    print(parse.get_words('引色粉自己验证过的方法送两套搭建黄片色情网站教程含源码'))

