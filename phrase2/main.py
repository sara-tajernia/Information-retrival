from __future__ import unicode_literals
import string
from hazm import *
import json
from hazm import stopwords_list
import numpy as np

#read contents
def read_contents():
    f = open('IR_data_news_12k.json')
    # f = open('jsonfile1.json')
    data = json.load(f)
    contents = []
    for i in range(len(data)):
        contents.append(data[str(i)]['content'])
    f.close()
    return contents[:500]

def tfidf(f, N, n):
    return (1+ np.log2(f)) + np.log2(N/n)



def preprocessing(contents):
    dic_list, count = {}, {}
    D = []
    # rootting
    lemmatizer = Lemmatizer()
    stopwords = stopwords_list()
    for i in range(len(contents)):
        #Normalize
        normalizer = Normalizer()
        contents[i] = normalizer.normalize(contents[i])
        #Tokenizer
        contents[i] = word_tokenize(contents[i])
        j = len(contents[i]) - 1
        dic_list = {}
        while j > -1:
            contents[i][j] = lemmatizer.lemmatize(contents[i][j])
            if contents[i][j] in string.punctuation or contents[i][j] == '،' or contents[i][j] in stopwords:
                contents[i].pop(j)
                j -=1
                continue

            if contents[i][j] in dic_list.keys():
                dic_list[contents[i][j]] += 1
            else:
                dic_list[contents[i][j]] = 1

            if contents[i][j] in count.keys():
                count[contents[i][j]] += 1
            else:
                count[contents[i][j]] = 1
            j -= 1
        D.append(dic_list)

    tf_idf = []
    for i in range(len(D)):
        dic = {}
        keys = list(D[i].keys())
        for t in (keys):
            dic[t] = tfidf(D[i][t], len(D), count[t])
        tf_idf.append(dic)

    return D, tf_idf


def input_data():
    print('Search:')
    words = list(input().split())
    i = 0
    dic_query = {}
    while i < len(words):
        if words[i] in dic_query:
            dic_query[words[i]] += 1
        else:
            dic_query[words[i]] = 1
        i += 1

    for i in list(dic_query.keys()):
        dic_query[i] /= len(list(dic_query.keys()))
    return dic_query


def similarity(tf_idf, dic_query):
    sim = {}
    for i in range(len(tf_idf)):
        for t in list(tf_idf[i]):
            if tf_idf[i][t] < 3:
                tf_idf[i].pop(t)
    for i in range(len(tf_idf)):
        sum_ab, sum_a2, sum_b2 = 0, 0, 0
        for t in list(dic_query.keys()):
            if t in list(tf_idf[i].keys()):
                sum_ab += tf_idf[i][t] * dic_query[t]
                sum_b2 += pow(dic_query[t], 2)
                sum_a2 += pow(tf_idf[i][t], 2)
        if sum_a2 != 0 or sum_b2!= 0:
            sim[i] = sum_ab/(np.sqrt(sum_a2) * np.sqrt(sum_b2))
    sim = dict(sorted(sim.items(), key=lambda item: item[1]))
    sim = list(sim.keys())
    return sim



def output(dictionary):
    #read titles
    f = open('IR_data_news_12k.json')
    data = json.load(f)
    title, url = [], []
    for i in range(len(data)):
        title.append(data[str(i)]['title'])
        url.append(data[str(i)]['url'])
    f.close()

    counter = 0
    for k in dictionary:
        if counter < 5:
            print(k, ':', url[k])
            counter += 1
        else:
            break
    if dictionary is None:
        print('NOT FOUND')


if __name__ == '__main__':
    contents = read_contents()
    D, tf_idf = preprocessing(contents)
    dic_query = input_data()
    sim = similarity(tf_idf, dic_query)
    output(sim)
