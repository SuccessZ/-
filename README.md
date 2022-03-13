## 运行文件

#### 准备工作

1. 请确保安装有 neo4j 图数据库，以及确保图数据库正常执行的其他依赖（如 `jdk-11.0.13`）

2. 请在 `build_goodsgragh.py` 第36行 `self.graph = Graph('http://localhost:7474',auth = ('用户名','密码'))` 根据自身情况正确输入 neo4j 的用户名和密码。

3. 数据因十分敏感且传播违法，不予提供。请在当前目录（`build_goodsgraph,py` 所属目录）下创建 `chinese_market.csv` 文件，并根据下列要求填入数据

   | 表头                      | 中文解释             | 知识图谱存在形式 |
   | ------------------------- | -------------------- | ---------------- |
   | _id                       | 商品唯一标识         | 商品节点的属性   |
   | _index                    | 索引                 | 索引节点名字     |
   | _score                    | 评分                 | 商品节点的属性   |
   | _type                     | 商品文件格式         | 商品节点的属性   |
   | gmt_create                | 销售信息创建日期     | 商品节点的属性   |
   | gmt_modified              | 销售信息最后修改日期 | 商品节点的属性   |
   | goods_bt_price            | 按比特币计算的价格   | 商品节点的属性   |
   | goods_comment             | 商品评价             | 商品节点的属性   |
   | goods_description         | 商品描述             | 商品节点的属性   |
   | goods_id                  | 商品id               | 商品节点的属性   |
   | goods_img_name            | 商品图片名字         | 图片节点名字     |
   | goods_img_url             | 商品图片网址         | 图片节点属性     |
   | goods_name                | 商品名称             | 商品节点名字     |
   | goods_origin_website      | 商品售卖网站url      | 网站节点属性     |
   | goods_origin_website_name | 商品售卖网站         | 网站节点名字     |
   | goods_price               | 商品价格             | 商品节点的属性   |
   | goods_seller              | 商品卖方id           | 卖方节点名字     |
   | goods_seller_last_online  | 商品最后一次售卖时间 | 商品节点的属性   |
   | goods_sold_num            | 商品售卖数量         | 商品节点的属性   |
   | goods_status              | 商品状态             | 商品节点的属性   |
   | goods_time                | 商品时间？？         | 商品节点的属性   |
   | goods_url                 | 商品网址             | 商品节点的属性   |
   | snap                      | 不知道有啥用         | 商品节点的属性   |



#### 运行文件

1. 命令行界面运行 `neo4j console` 启动图数据库
2. 运行 `build_goodsgragh.py` 文件，依据 csv 存储数据构建图数据库
3. 运行 `search.py`，输入查询关键字即可得到结果（例如"教程"）。