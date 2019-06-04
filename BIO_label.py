#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Time   : 2019/6/4 10:09
# @Author : libin(leoli)
# @File   : BIO_label.py

import json
import re
import math


def BIO_labeling(json_file_path, mapping_dict):
    """将指定目录下的json文件中的数据进行BIO标注"""
    with open(file=json_file_path, mode='r', encoding='utf-8') as f:
        dict = json.load(f)
        # print(dict)

    # 存储标注完的结果数据
    BIO_labeling_result_list = []

    for record in dict['RECORDS'][0:]:

        """现在处理的东西为
        {
        "g_name":"ANESSA安耐晒 18年新款金瓶防晒霜 SPF50+ PA++++  60ml 4901872073696",
        "keywords":"[\"防晒霜\"]",
        "full_properties":"{\"品牌\":\"安热沙安\",\"净含量\":\"60ml\",\"防晒指数\":\"spf50\",\"防晒分类\":\"防晒霜\"}"
        }
        """
        # 将g_name中的空字符去掉
        g_name = ''
        name_part_list = record['g_name'].split()
        for name_part in name_part_list:
            g_name += name_part
        g_name += '。'
        # print(f'产品的名字是{g_name}')

        # 将文件中的full_properties json类型字符串转换为字典类型
        full_properties = json.loads(record['full_properties'])
        # print(full_properties)

        # 获取每个产品的所有属性值
        prop_key = full_properties.keys()
        # print(prop_key)

        # 新建一个字典列表先将一个g_name的所有的字符标注为O
        BIO_labeling_result = []
        for char in g_name:
            BIO_labeling_result += [{char: 'O'}]
        print(f'标注前{BIO_labeling_result}')

        for key in prop_key:
            # 每个属性对应的值
            value = full_properties[key]
            print(f'prop_value{value}')

            # 该属性值的字符长度
            value_len = len(value)

            # 在g_name中查找该属性值并返回第一个字符的位置，从0开始，没找到返回-1
            offset = g_name.find(value)
            print(offset)

            #如果在g_name中找到该属性，则将第一的字符标注为B，属性值的其余部分标注为I
            if offset != -1:
                char_key1 = list(BIO_labeling_result[offset].keys())[0]
                test = list(BIO_labeling_result[offset].keys())
                print(f'offset_keys{test}')
                print(char_key1)
                #将匹配的第一个字符字典中的值标注为B，即属性的开头字符

                #TODO  此处需要匹配具体的属性
                BIO_labeling_result[offset][char_key1] = 'B-'+ mapping_dict[key]

                #将该属性剩余字符标注为I
                for i in range(offset+1, offset + value_len):
                    char_key2 = list(BIO_labeling_result[i].keys())[0]
                    BIO_labeling_result[i][char_key2] = 'I-' + mapping_dict[key]
            else:
                # 没有匹配到处理下一个
                pass
        print(f'标注后的数据{BIO_labeling_result}')


def Prop_CN_to_EN_Mapping(map_file_path):

    #新建中英文匹配字典
    mapping_dict = {}
    with open(file=map_file_path, mode='r', encoding='utf-8') as f:
        try:
            while 1:
                #读取一行
                line = f.readline().strip()
                if not line:
                    break
                if line.strip() == "":
                    continue
                # print(line)

                #正则匹配英文缩写
                en_abbr = re.search('([A-Z]+)',line).group(0)
                # print(en_abbr)

                #查询英文首字母在本行的位置，以此来提前中文
                offset = line.find(en_abbr)
                zh_cn = line[0:offset]
                # print(zh_cn)

                #将中英文对应的添加到字典
                mapping_dict[zh_cn] = en_abbr
        except Exception as e:
            print(e)

    print(mapping_dict)
    return mapping_dict

def ParsePropMappingFile(mappingFilePath, id_to_tag_filePath, file_to_id_filePath):
    """将产品属性匹配文件处理成指定格式"""
    mappingfile = Prop_CN_to_EN_Mapping(mappingFilePath)
    with open(id_to_tag_filePath,mode='a',encoding='utf-8') as f:
        f.write('0:O\n')
        i = 1
        for value in mappingfile.values():
            for label_type in ['B','I','S','E']:
                f.write(str(i)+':'+ label_type + '-' +value + '\n')
                i += 1
    with open(file_to_id_filePath,mode='a',encoding='utf-8') as f:
        f.write('0:O\n')
        i = 1
        for value in mappingfile.values():
            for label_type in ['B','I','S','E']:
                f.write(label_type + '-' +value+':'+ str(i) + '\n')
                i += 1



if __name__ == '__main__':
    # test = Prop_CN_to_EN_Mapping('data/PropMappingFile_zh-cn=en.txt')
    # BIO_labeling('data/data_outcome.json',test)
    ParsePropMappingFile('data/PropMappingFile_zh-cn=en.txt','id_to_tag.txt','tag_to_id.txt')

