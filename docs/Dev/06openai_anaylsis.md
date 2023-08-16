# 开发记录（六）结合 OpenAI 的论文批量分析





安装 OpenAI 相关包以及向量数据库连接包

```sh
pip install openai tiktoken langchain pypdf unstructured pgvector psycopg2-binary
```







```sql
create extension vector;
```





运行时出现了下面的警告：

```
RequestsDependencyWarning: urllib3 (1.26.15) or chardet (5.2.0)/charset_normalizer (2.0.12) doesn't match a supported version!
  warnings.warn(
```





参考：https://github.com/DefectDojo/django-DefectDojo/issues/3270

```sh
pip install -U urllib3 requests
```

