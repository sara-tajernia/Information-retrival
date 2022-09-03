from __future__ import unicode_literals
import string
from hazm import *
import json
from hazm import stopwords_list
import matplotlib.pyplot as plt
import numpy as np

#read contents
def read_contents():
    f = open('IR_data_news_12k.json')
    data = json.load(f)
    contents = []
    for i in range(len(data)):
        contents.append(data[str(i)]['content'])
    f.close()
    return contents[:500]

def preprocessing(contents):
    count = 0
    list_count_total, list_count = [], []
    dic_list, count_total, count_single = {}, {}, {}
    # rootting
    # lemmatizer = Lemmatizer()
    stemmer = Stemmer()
    stopwords = stopwords_list()
    for i in range(len(contents)):
        count += len(contents[i].split())
        list_count.append(count)
        #Normalize
        normalizer = Normalizer()
        contents[i] = normalizer.normalize(contents[i])
        #Tokenizer
        contents[i] = word_tokenize(contents[i])
        j = len(contents[i]) - 1
        while j > -1:
            # contents[i][j] = lemmatizer.lemmatize(contents[i][j])
            contents[i][j] = stemmer.stem(contents[i][j])
            if contents[i][j] in string.punctuation or contents[i][j] == '،' or contents[i][j] in stopwords:
                contents[i].pop(j)
                j -=1
                continue
            if contents[i][j] in dic_list.keys():
                count_total[contents[i][j]] += 1
                if i in dic_list[contents[i][j]].keys():
                    dic_list[contents[i][j]][i].append(j)
                    count_single[contents[i][j]][i] += 1
                else:
                    dic_list[contents[i][j]][i] = [j]
                    count_single[contents[i][j]][i] = 1
            else:
                dic_list[contents[i][j]] = {i: [j]}
                count_single[contents[i][j]] = {i: 1}
                count_total[contents[i][j]] = 1
            j -= 1
        list_count_total.append(len(count_total))
    # print('number of tokens', len(count_total))
    # print('number of vocabulary = ', count)
    # print(list_count_total)
    # print(list_count)
    # heaps(list_count, list_count_total)

    return contents, dic_list, count_total, count_single

#save datas and where they are
def spatial_index(contents):
    dic_list, count_total,count_single = {}, {}, {}
    for i in range(len(contents)):
        for j in range(len(contents[i])):
            if contents[i][j] in dic_list.keys():
                count_total[contents[i][j]] += 1
                if i in dic_list[contents[i][j]].keys():
                    dic_list[contents[i][j]][i].append(j)
                    count_single[contents[i][j]][i] += 1
                else:
                    dic_list[contents[i][j]][i] = [j]
                    count_single[contents[i][j]][i] = 1
            else:
                dic_list[contents[i][j]] = {i: [j]}
                count_single[contents[i][j]] = {i: 1}
                count_total[contents[i][j]] = 1
    return dic_list, count_total, count_single

# get input and split them by "", !
def input_data():
    print('Search:')
    words = list(input().split())
    single_words, multi_words, not_words = [], [], []
    i = 0
    while i < len(words):
        if words[i][0] == '“':
            mlist = []
            while words[i][len(words[i])-1] != '”':
                mlist.append(words[i].replace('“', ''))
                i += 1
            mlist.append(words[i].replace('”', ''))
            multi_words.append(mlist)
        elif words[i][0] == '!':
            not_words.append(words[i].replace('!', ''))
        else:
            single_words.append(words[i])
        i += 1
    return single_words, multi_words, not_words


def query(dic_list, count_total, count_single, single_words, multi_words, not_words):
    #find sing words in documents
    words_dic = {}
    for i in range(len(single_words)):
        if single_words[i] in count_single:
            for j in (list(count_single[single_words[i]])):
                if j not in words_dic:
                    words_dic[j] = count_single[single_words[i]][j]
                    if single_words[i] in dic_list:
                        sentence = []
                        sentence.append(single_words[i])
                else:
                    words_dic[j] += count_single[single_words[i]][j]

    #find "" words in documents
    last_word = {}
    for i in range(len(multi_words)):
        for j in range(len(multi_words[i])):
            if j == 0 and multi_words[i][j] in dic_list:
                last_word = dic_list[multi_words[i][j]]
            else:
                for k in list(last_word):
                    counter = 0
                    for l in last_word[k]:
                        if l+1 in dic_list[multi_words[i][j]][k]:
                            counter += 1
                    if k not in words_dic:
                        words_dic[k] = counter
                    else:
                        words_dic[k] += 1

    #find !words in documents
    not_dic = []
    for i in range(len(not_words)):
        if not_words[i] in count_single:
            for j in count_single[not_words[i]].keys():
                if j not in not_dic:
                    not_dic.append(j)

    #remove documents that hast !word
    for i in not_dic:
        if i in words_dic.keys() and len(words_dic) > 5:
            words_dic.pop(i)

    return words_dic

def output(single_dic):
    #sort dictionary
    dictionary = reversed(list(dict(sorted(single_dic.items(), key=lambda item: item[1]))))
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
        print(k)
        if counter < 5:
            print(k, ':', url[k])
            counter += 1
        else:
            break
    if dictionary is None:
        print(12345678)
    print(dictionary)

def zipf(count_total):
    frequency = list(count_total.values())
    frequency.sort(reverse=True)
    xs = []
    for i in range(1, len(frequency)+1):
        xs.append(i)
    plt.plot(np.log10(xs), np.log10(frequency))
    plt.show()

def heaps(M, T):
    plt.plot(np.log10(M), np.log10(T))
    plt.show()

if __name__ == '__main__':
    contents = read_contents()
    contents, dic_list, count_total, count_single = preprocessing(contents)
    single_words, multi_words, not_words = input_data()
    single_dic = query(dic_list, count_total, count_single, single_words, multi_words, not_words)
    # zipf(count_total)
    output(single_dic)