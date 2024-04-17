"""构建论文知识图谱

    结合pandas与py2neo将数据进行清洗, 抽取三元组, 构建图数据

Classes:
    DataClean: 数据清洗类
    TripleExtractor: 三元组抽取类
    GraphBuilder: 图数据构建类

Functions:
    convert_string_to_list: 将字符串转换为列表



"""


import os
import ast
import pandas as pd
import datetime
# import tqdm
from py2neo import Graph, Node, Relationship

"""设置工作目录"""

# 定义要创建的目录的路径
output_path = 'data/output'
# 判断目录是否存在, 如果不存在则创建
if not os.path.exists(output_path):
    os.makedirs(output_path)
# 读取当前日期, 用于输入文件名
today = datetime.date.today()
formatted_today = today.strftime('%Y%m%d')
# 读取目录下所有txt文件中的知识
knowledge_directory = 'data/input/rs_general_knowledge/'


class DataClean:
    """数据清洗
    """

    def core_select(self, input_file: any) -> any:
        """核心数据筛选

        对导出的已读论文信息进行数据清洗预处理

        Args:
            input_file (any): 待清洗的文件路径

        Returns:
            output_file (any): 输出文件的路径
        """
        # 提取不带后缀的文件名
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        df = pd.read_csv(input_file)
        # 筛选出目标列
        df = df.loc[:, ["Title", "Publication Title",
                        "Manual Tags", "Automatic Tags"]]
        # 使用 combine_first 合并两个标签
        df["All Tags"] = df['Manual Tags'].combine_first(df['Automatic Tags'])

        # 再次筛选出目标列
        df = df.loc[:, ["Title", "Publication Title", "All Tags"]]
        # 将表头进行简化
        df.columns = ["Title", "Publication", "Tags"]
        output_file = f'{output_path}/{file_name}_coreinfo_{formatted_today}.xlsx'
        df.to_excel(output_file, index=False)
        return output_file

    def build_knowledge_base(self, knowledge_dir: str) -> dict:
        """构建通识知识库

        从指定知识目录中读取所有txt文件中的内容并存储在一个字典中
        键为文件名 (不含扩展名), 值为文件内容组成的列表.

        Args:
            knowledge_dir (str): 包含知识文件的目录路径

        Returns:
            dict: 文件名 (不含扩展名) 到文件内容的映射字典
        """
        knowledge_base = {}
        for file in os.listdir(knowledge_dir):
            if file.endswith(".txt"):
                file_name = file.split('.')[0]
                with open(os.path.join(knowledge_dir, file), 'r', encoding='utf-8') as file:
                    # 去除每行末尾的换行符
                    knowledge_base[file_name] = [line.strip()
                                                 for line in file.readlines()]
        return knowledge_base

    def match_knowledge(self, input_file: any, knowledge_base: dict) -> any:
        """知识匹配

        将Excel表格中的'Tags'列内容与知识库进行精确匹配, 匹配成功的标签存储在对应的知识文件名列中,
        未匹配成功的标签存储在'other_tags'列中, 并输出到新的Excel文件中。

        Args:
            input_file (str): 输入的Excel文件路径.
            knowledge_base (dict): 知识库, 由build_knowledge_base函数生成的字典.

        Returns:
            output_file (str): 输出的CSV文件路径.
        """
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        df = pd.read_excel(input_file)

        matched_dict = {}
        matched_dict['other_tags'] = []
        for knowledge in knowledge_base:
            matched_dict[knowledge] = []

        # 对每一行的Tags进行匹配
        for index, row in df.iterrows():
            # 读取单元格中的标签, 转化为标签列表
            tags = row['Tags']
            tag_list = tags.split('; ')

            unmatched_tags = []

            # 匹配标签与知识库
            for category, knowledge_list in knowledge_base.items():
                # 使用列表间并集提取匹配标签
                common_elements = list(set(tag_list) & set(knowledge_list))
                if len(common_elements) == 0:
                    # 若没有匹配则添加一个空数组 []
                    matched_dict[category].append([])
                else:
                    matched_dict[category].append(common_elements)
                # 使用列表差集提取出剩下的未匹配的元素
                tag_list = list(set(tag_list) - set(knowledge_list))
                unmatched_tags = tag_list

            # 将未匹配的标签保存在 'other_tags' 列
            matched_dict['other_tags'].append(unmatched_tags)

        # 将匹配的结果添加到 DataFrame 中
        for category, matched_tags in matched_dict.items():
            df[category] = matched_tags

        result_df = df.drop('Tags', axis=1)  # 删除原始的 Tags 列
        output_file = f'{output_path}/{file_name}_match.csv'
        result_df.to_csv(output_file, index=False)
        print("Completed! 数据清洗完毕.")
        return output_file


def convert_string_to_list(s: str) -> list:
    """转换字符串到列表

    将 CSV 中存储的数组由字符串转换成数组
    """
    try:
        return ast.literal_eval(s)
    except ValueError:
        # 如果转换失败，返回原始字符串
        return str(s)


class TripleExtractor:
    """三元组抽取

    """

    def create_triples(self, input_file: any) -> any:
        """创建三元组
            Args:

        """
        # 提取不带后缀的文件名
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        df = pd.read_csv(input_file)
        # 创建一个空列表来存储三元组
        triples = []

        # 应用函数到特定的列
        df['other_tags'] = df['other_tags'].apply(convert_string_to_list)
        df['data_source'] = df['data_source'].apply(
            convert_string_to_list)
        df['indices'] = df['indices'].apply(convert_string_to_list)
        df['research_field'] = df['research_field'].apply(
            convert_string_to_list)
        df['resolution'] = df['resolution'].apply(convert_string_to_list)
        df['study_area'] = df['study_area'].apply(convert_string_to_list)
        df['study_method'] = df['study_method'].apply(
            convert_string_to_list)
        df['study_period'] = df['study_period'].apply(
            convert_string_to_list)

       # 遍历DataFrame中的每一行
        for index, row in df.iterrows():
            title = row["Title"]
            publication = row["Publication"]
            other_tags = row["other_tags"]
            data_source = row["data_source"]
            indices = row["indices"]
            research_field = row["research_field"]
            resolution = row["resolution"]
            study_area = row["study_area"]
            study_method = row["study_method"]
            study_period = row["study_period"]

            # 为标题和出版物创建三元组
            triples.append((title, "published_in", publication))

            # 为标题与其他标签创建三元组
            for tag in other_tags:
                triples.append((title, "tag", tag))
            # 为其他信息创建三元组
            for source in data_source:
                triples.append((title, "use_data", source))
            for index_item in indices:
                triples.append((title, "use_index", index_item))
            for field in research_field:
                triples.append((title, "research_field", field))
            for res in resolution:
                triples.append((title, "resolution", res))
            for area in study_area:
                triples.append((title, "study_area", area))
            for method in study_method:
                triples.append((title, "study_method", method))
            for period in study_period:
                triples.append((title, "study_period", period))

        # 将三元组存入新的Excel文件
        new_df = pd.DataFrame(
            triples, columns=["Subject", "Predicate", "Object"])
        output_file = f"{output_path}/{file_name}_triples.csv"
        new_df.to_csv(output_file, index=False)
        print("Completed! 三元组抽取完毕.")
        return output_file


class PaperGraph:
    """构建论文知识图谱
    """

    def __init__(self, input_file) -> None:
        self.csv_file = input_file
        self.graph = Graph(
            "http://localhost:7474",  # neo4j 搭载服务器 ip 地址, ipconfig 可获取到, 监听端口号为 7474
            name="neo4j",  # 数据库 username, 初始默认为 neo4j
            password="cveo123456")
        self.graph.delete_all()
        self.graph.begin()

    def read_nodes(self):
        """读取文件"""
        # 10 类节点
        papers = []  # 论文本体/题目
        publications = []  # 期刊名称
        tags = []  # 标签
        data_source = []  # 使用数据
        indices = []  # 相关指数
        research_field = []  # 研究领域
        resolution = []  # 结果分辨率
        study_area = []  # 研究区域
        study_method = []  # 研究方法
        study_period = []  # 研究时段

        # 论文所有信息
        paper_infos = []

        # 9 种节点实体关系
        rels_published = []  # 论文-期刊
        rels_tags = []  # 论文-标签
        rels_data_source = []  # 论文-使用数据
        rels_indices = []  # 论文-相关指数
        rels_research_field = []  # 论文-研究领域
        rels_resolution = []  # 论文-结果分辨率
        rels_study_area = []  # 论文-研究区域
        rels_study_method = []  # 论文-研究方法
        rels_study_period = []  # 论文-研究时段

        df = pd.read_csv(self.csv_file)
        # 应用函数到特定的列
        df['other_tags'] = df['other_tags'].apply(convert_string_to_list)
        df['data_source'] = df['data_source'].apply(
            convert_string_to_list)
        df['indices'] = df['indices'].apply(convert_string_to_list)
        df['research_field'] = df['research_field'].apply(
            convert_string_to_list)
        df['resolution'] = df['resolution'].apply(convert_string_to_list)
        df['study_area'] = df['study_area'].apply(convert_string_to_list)
        df['study_method'] = df['study_method'].apply(
            convert_string_to_list)
        df['study_period'] = df['study_period'].apply(
            convert_string_to_list)

        # 逐行处理数据
        # count = 0
        for index, row in df.iterrows():
            paper_dict = {}
            # count += 1
            # print(count)
            # 将论文题目作为唯一主体
            paper = row['Title']
            papers.append(paper)
            # 论文独有的特性信息
            paper_dict['name'] = paper
            paper_dict['tags'] = row['other_tags']
            # 生成关系信息
            rels_published.append([paper, row['Publication']])
            publications.append(row['Publication'])
            # 对几个可能为列表类型的数据进行处理, 生成关系信息
            for tag in row['other_tags']:
                rels_tags.append([paper, tag])
            tags += paper_dict['tags']

            for source in row['data_source']:
                rels_data_source.append([paper, source])
            data_source += row['data_source']

            for vi in row['indices']:
                rels_indices.append([paper, vi])
            indices += row['indices']

            for field in row['research_field']:
                rels_research_field.append([paper, field])
            research_field += row['research_field']

            for res in row['resolution']:
                rels_resolution.append([paper, res])
            resolution += row['resolution']

            for area in row['study_area']:
                rels_study_area.append([paper, area])
            study_area += row['study_area']

            for method in row['study_method']:
                rels_study_method.append([paper, method])
            study_method += row['study_method']

            for period in row['study_period']:
                rels_study_period.append([paper, period])
            study_period += row['study_period']

            paper_infos.append(paper_dict)

        # 使用 set() 去除重复项
        return set(publications), set(tags), set(data_source), set(indices), set(research_field), \
            set(resolution), set(study_area), set(study_method), set(study_period), paper_infos, \
            rels_published, rels_tags, rels_data_source, rels_indices, rels_research_field, \
            rels_resolution, rels_study_area, rels_study_method, rels_study_period

    def create_node(self, label: str, nodes) -> None:
        """建立节点"""
        # count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.graph.create(node)
            # count += 1
            # print(count, len(nodes))
        return

    def create_papers_nodes(self, paper_infos) -> None:
        """创建论文本体节点

        创建知识图谱的核心-代表论文本体独有信息的节点
        """
        count = 0
        for paper_dict in paper_infos:
            node = Node(
                "Paper", name=paper_dict['name'], tags=paper_dict['tags'])
            self.graph.create(node)
            count += 1
        print('Paper nodes created:', count)
        return

    def create_graph_nodes(self) -> None:
        """创建其他实体节点

        创建知识图谱论文信息中其他实体节点, 共 10 类节点
            publications, tags, data_source, indices, research_field,
            resolution, study_area, study_method, study_period, paper_infos,
        """
        publications, tags, data_source, indices, research_field, \
            resolution, study_area, study_method, study_period, paper_infos, \
            rels_published, rels_tags, rels_data_source, rels_indices, rels_research_field, \
            rels_resolution, rels_study_area, rels_study_method, rels_study_period = self.read_nodes()
        self.create_papers_nodes(paper_infos)
        self.create_node('Publication', publications)
        self.create_node('Tags', tags)
        self.create_node('Data_Source', data_source)
        self.create_node('Indices', indices)
        self.create_node('Research_Field', research_field)
        self.create_node('Resolution', resolution)
        self.create_node('Study_Area', study_area)
        self.create_node('Study_Method', study_method)
        self.create_node('Study_Period', study_period)
        return

    def create_relationship(self, start_node: str, end_node: str, edges: list, rel_type: str, rel_name: str) -> None:
        """创建实体关联边

        Args:
            start_node (str): 起点节点类型
            end_node (str): 终点节点类型
            edges (list): 实体关系列表
            rel_type (str): 实体关系类型

        Example:
            edges = [['paper1', 'journal1'], ['paper2', 'journal2']]
            rel_type = 'published_in'
            rel_name = '发表期刊'
            create_relationship('Paper', 'Publication', edges, 'published_in', '发表期刊')
        """
        # 去重处理
        set_edges = []
        for edge in edges:
            # 使用 ### 作为不同关系之间分隔的标志
            set_edges.append('###'.join(edge))
        for edge in set(set_edges):
            # 选取数组种前两个关系, 一般关系为一对一
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "MATCH (p:%s), (q:%s) WHERE p.name='%s'AND q.name='%s' CREATE (p)-[rel:%s {name: '%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.graph.run(query)
            except Exception as e:
                print(e)

        return

    def create_graph_rels(self):
        """创建9种实体关系边
        """
        publications, tags, data_source, indices, research_field, \
            resolution, study_area, study_method, study_period, paper_infos, \
            rels_published, rels_tags, rels_data_source, rels_indices, rels_research_field, \
            rels_resolution, rels_study_area, rels_study_method, rels_study_period = self.read_nodes()
        self.create_relationship(
            'Paper', 'Publication', rels_published, 'published_in', '发表期刊')
        self.create_relationship(
            'Paper', 'Tags', rels_tags, 'tag', '标签')
        self.create_relationship(
            'Paper', 'Data_Source', rels_data_source, 'use_data', '使用数据')
        self.create_relationship(
            'Paper', 'Indices', rels_indices, 'use_indices', '使用指数')
        self.create_relationship(
            'Paper', 'Research_Field', rels_research_field, 'research_field', '研究领域')
        self.create_relationship(
            'Paper', 'Resolution', rels_resolution, 'resolution', '分辨率')
        self.create_relationship(
            'Paper', 'Study_Area', rels_study_area, 'study_area', '研究区域')
        self.create_relationship(
            'Paper', 'Study_Method', rels_study_method, 'study_method', '研究方法')
        self.create_relationship(
            'Paper', 'Study_Period', rels_study_period, 'study_period', '研究时段')
        # 将所有节点的关联节点数量设为属性size
        rel_count_query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() WITH n, COUNT(r) AS relCount SET n.size = relCount"
        self.graph.run(rel_count_query)
        return

    def create_graph(self) -> None:
        """创建图谱节点和边"""
        print("生成知识图谱ing")
        self.create_graph_nodes()
        print("生成图谱边ing")
        self.create_graph_rels()
        print("Completed! 图谱生成完毕.")
        return

    def create_graph_from_csv(self, input_file: str) -> None:
        """通过 CSV 直接创建图数据库 - 暂不用"""
        df = pd.read_csv(input_file, encoding='utf-8')
        # 循环创建结点
        for i in range(len(df['Subject'])):
            node1 = Node('Title', name=df['Subject'][i])
            self.graph.merge(node1, 'Title', 'name')
            node2 = Node('Journal', name=df['Object'][i])
            self.graph.merge(node2, 'Journal', 'name')
            rel = Relationship(node1, df['Predicate'][i], node2)
            self.graph.merge(rel)
            print(i, len(df['Subject']))
        print("success!")
        return


if __name__ == '__main__':
    csv_file = 'data/output/毕业论文参考文献.csv'
    print("step1: 论文数据清洗ing")
    core_info = DataClean().core_select(csv_file)
    knowledge_base = DataClean().build_knowledge_base(knowledge_directory)
    match_info = DataClean().match_knowledge(core_info, knowledge_base)
    print("step2: 生成知识图谱ing")
    paper_graph = PaperGraph(match_info)
    paper_graph.create_graph()

    # print("step2: 论文数据三元组构建知识图谱中")
    # triples_info = TripleExtractor().create_triples(match_info)
    # paper_graph = PaperGraph().create_graph_from_csv(triples_info)
