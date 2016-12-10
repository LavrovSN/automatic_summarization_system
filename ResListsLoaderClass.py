# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import codecs, json


# stopwords - содержит список стоп-слов.
# titled_stopwords - содержит список стоп-слов с повышенной первой бувой (необходим для разбиения на предлоежния)
# abbreviations - соержит список аббревиатур с точкой, после которых не разбивать на предлоежния.


class LoadExternalLists(object):
    
    """
    Загружаем в память файл стоп-слов (+ с ББ), файл с неправ. формами глаголов 
    и файл с неправ. формами множ. числа сущ-х., файл сокращений для сплиттера,
    лексикон для немецкого и корпуса для tfidf.
    """

    def __init__(self):

        self.stopwords_common = set()
        self.stopwords_ru = set()

        self.titled_stopwords = set()
        self.abbreviations = set()

        self.corpus_RU = {}

        
    def loadCommonStopWords(self):
        # print "Loading stopwords"
        with codecs.open(r"./txt_resources/stopwords_common.txt",'r','utf-16') as file_openstopw:
            self.stopwords_common = set(file_openstopw.read().split('\r\n'))

        return self.stopwords_common


    def loadStopWordsRU(self):
        print ("Loading stopwordsRU")
        with codecs.open(r"./txt_resources/stopwords_ru.txt",'r','utf-16') as file_openstopw:
            self.stopwords_ru = set(file_openstopw.read().split('\r\n'))

        return self.stopwords_ru


    def loadTitledStopwords(self):
        print('Making titled stopwords')
        self.titled_stopwords = tuple([word.title() for word in self.loadCommonStopWords()])

        return self.titled_stopwords


    def loadAbbreviations(self):
        print('Loading abbreviations')
        with codecs.open(r'./txt_resources/abbrevs_common.txt','r', 'utf-16') as file_openabbrev:
            self.abbreviations = set(file_openabbrev.read().split('\r\n'))

        return self.abbreviations


    def loadCorpusRU(self):
        print ('Loading RU Corpus')
        ##with open(r"./corpus/RUCorpusDict_158099.json", 'r') as infile:
            ##self.corpus_RU = json.load(infile)

        return self.corpus_RU