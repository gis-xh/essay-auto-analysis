# 腾讯云机器翻译API调用

import json
import pandas as pd
import time
import requests
# 导入腾讯云机器翻译API相关模块
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


# 设置腾讯云 API 密钥和项目 ID
secretId = "……"
secretKey = "……"
projectId = 1111111
# 设置源语言和目标语言
source = "auto"
target = "zh"

# 读取列名并以列表的形式返回内容
def get_words_from_excel(excel_file, column_name):
    # 设置字符限制
    char_limit = 2000
    # 读取指定列的数据
    words = pd.read_excel(excel_file, usecols=[column_name])
    # 选取第一列的数据
    words = words.iloc[:, 0]
    # 转换为列表
    words_list = words.tolist()
    # 初始化结果列表
    result_list = []
    # 初始化临时列表和长度
    temp_list = []
    temp_length = 0
    # 遍历单词列表
    for word in words_list:
        # 计算单词的长度
        word_length = len(word)
        # 如果单词长度超过字符限制，跳过该单词
        if word_length > char_limit:
            continue
        # 如果临时列表的长度加上单词的长度超过字符限制，将临时列表添加到结果列表，并清空临时列表和长度
        if temp_length + word_length > char_limit:
            result_list.append(temp_list)
            temp_list = []
            temp_length = 0
        # 将单词添加到临时列表，并更新长度
        temp_list.append(word)
        temp_length += word_length
    # 如果临时列表不为空，将其添加到结果列表
    if temp_list:
        result_list.append(temp_list)
    # 返回结果列表
    return result_list

# 批量翻译
def translate_words(source_file, source_column):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(secretId, secretKey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)
        
        # words_list = get_words_from_excel(source_file, source_column)
        # 获取源文件中指定列的数据
        source_text_list = get_words_from_excel(source_file, source_column)
        # 初始化待翻译的文本列表
        text_to_translate = []
        # 遍历源文本列表
        for sublist in source_text_list:
            # 将每个子列表转换为一个字符串
            text = ' '.join(sublist)
            # 将字符串添加到待翻译的文本列表
            text_to_translate.append(text)
        
        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.TextTranslateBatchRequest()
        # 设置请求参数，包括待翻译的文本、项目 ID、目标语言和源语言
        params = {
            "Source": source,
            "Target": target,
            "ProjectId": projectId,
            "SourceTextList": text_to_translate
        }
        # 将参数转换为 json 格式并赋值给请求对象
        req.from_json_string(json.dumps(params))
        
        # 每次请求后暂停0.2秒
        time.sleep(0.2)

        # 返回的resp是一个TextTranslateBatchResponse的实例，与请求对象对应
        resp = client.TextTranslateBatch(req)
        
        target_text_list = resp.TargetTextList  # 获取翻译结果值
        return target_text_list
    
    except TencentCloudSDKException as err:
        print(err)

# 翻译结果存储
def write_results(source_file, source_column, target_file, target_column):
    source_df = pd.read_excel(source_file) # 读取原文件为一个DataFrame
    target_text_list = translate_words(source_file, source_column) # 调用翻译函数，返回一个list
    target_df = pd.DataFrame(target_text_list, columns=[target_column]) # 将list转换为一个DataFrame，并指定列名
    new_df = source_df.join(target_df) # 将两个DataFrame按照索引合并为一个新的DataFrame
    new_df.to_excel(target_file, index=False) # 将新的DataFrame直接写入到文件中，指定index参数

    