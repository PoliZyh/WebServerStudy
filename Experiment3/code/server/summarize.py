#coding=utf-8
import SparkApi




# 使用星火大模型
def get_content_summarize(que):
    appid = ""   
    api_secret = ""  
    api_key =""    

    domain = "generalv2"    # v2.0版本
    Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址

    text =[]

    def getText(role,content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        text.append(jsoncon)
        return text
    
    def getlength(text):
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    def checklen(text):
        while (getlength(text) > 8000):
            del text[0]
        return text
    
    text.clear

    context = '请你把这个新闻总结为30个汉字之内，新闻如下，可以忽略一部分内容，但是必须要在三十字以内'

    question = checklen(getText("user", context+que))
    SparkApi.answer = ""
    SparkApi.main(appid,api_key,api_secret,Spark_url,domain,question)

    return SparkApi.answer



