
from ResListsLoaderClass import LoadExternalLists
from SentenceSplitterClass import SentenceSplitter
from TextSegmentorClass import TextSegmentor
import codecs, itertools, subprocess, json
from SymmetricalSummarizingClass import *

class SUMMARIZER():

    def __init__(self):
        self.language = 'ru'

        self.external_lst = LoadExternalLists()
        self.titled_stopwords = self.external_lst.loadTitledStopwords()
        self.ABBREVIATIONS = self.external_lst.loadAbbreviations()

        self.stopwords = self.external_lst.loadStopWordsRU()
        self.terms_dict = self.external_lst.loadCorpusRU()
        self.VERBTRANSFORMS = ''
        self.NOUNTRANSFORMS = ''
        self.lexicon_de = ''
        self.ger_nn = ''
        self.ger_ne = ''

        self.stem_sents = SentenceSplitter(self.stopwords, self.VERBTRANSFORMS, self.NOUNTRANSFORMS, self.lexicon_de, self.language)

    def summarize(self):
        file = open('text.txt', 'r')
        OPENTEXT = file.read();

        # разбиваем в LIST_OF_SENTENCES входной текст
        textsegmentor = TextSegmentor(self.titled_stopwords, self.ABBREVIATIONS, self.language)
        LIST_OF_SENTENCES, TTL = textsegmentor.segment(OPENTEXT)

        # склеиваем все списки в один простой список ALLSENTENCES для статистики по предложениям
        ALLSENTENCES = list(itertools.chain.from_iterable(LIST_OF_SENTENCES))

        # для методики симметричного реф-я нужно не менее 3-х предложений
        if len(ALLSENTENCES) >= 3:
            # стеммируются предложения
            # список предложений из основ слов, предложения сгруппированны по абзацам
            STEMMED_SENTENCES = self.stem_sents.tokenizeListParagraphs(LIST_OF_SENTENCES)

            # стеммируется заголовок
            if len(TTL) > 0:
                TITLE_PAIRS = list(itertools.chain.from_iterable(self.stem_sents.tokenizeListSentences(TTL)))
                TITLE = [pair[0] for pair in TITLE_PAIRS]

            else:
                TITLE = []

            # список предложений без границ абзацев, предложения разбиты на основы
            NO_PARAGRAPHS = list(itertools.chain.from_iterable(STEMMED_SENTENCES))
            # большой список всех основ слов для подсчета частотности (TF/IDF)
            BIG_LIST_OF_PAIRS = list(
                itertools.chain.from_iterable(itertools.chain.from_iterable(STEMMED_SENTENCES)))
            BIG_LIST_OF_STEMS = [pair1[0] for pair1 in BIG_LIST_OF_PAIRS]

            # общее количество стем в тексте
            TOTAL_STEMS_IN_TEXT = len(BIG_LIST_OF_STEMS)
            # общее количество предложений в тексте
            TOTAL_SENTS_IN_TEXT = len(ALLSENTENCES)

            if len(BIG_LIST_OF_STEMS) > 0:
                w_count = CountTermWeights(self.language)

                # список кортежей (слово, его частота), усечённый по средней частоте
                TOTAL_STEM_COUNT, ABSOLUTE_COUNT = w_count.simpleTermFreqCount(BIG_LIST_OF_STEMS)

                # список "имён собственных"
                PROPER_NOUNS, STEMMED_PNN = FindProperNouns(self.language).lookForProper(ALLSENTENCES, self.stopwords,
                                                                                         self.VERBTRANSFORMS,
                                                                                         self.NOUNTRANSFORMS,
                                                                                         self.lexicon_de, self.ger_nn,
                                                                                         self.ger_ne)

                # список терминов с весовыми коэффициентами (кортежи)
                SORTED_TFIDF = w_count.countPureTFIDF(TOTAL_STEM_COUNT, self.terms_dict)
                FINAL_SORTED_TFIDF = w_count.countFinalWeights(SORTED_TFIDF, TITLE, STEMMED_SENTENCES, ALLSENTENCES,
                                                               TOTAL_STEMS_IN_TEXT, TOTAL_SENTS_IN_TEXT, self.stopwords,
                                                               self.VERBTRANSFORMS, self.NOUNTRANSFORMS, STEMMED_PNN,
                                                               self.lexicon_de)
                KEYWORDS = w_count.showKeywords(BIG_LIST_OF_PAIRS, FINAL_SORTED_TFIDF, ABSOLUTE_COUNT, PROPER_NOUNS)

                # объект класса для вычисления симметричной связи предложений
                # вычисляем вес каждого предложения
                symmetry = SymmetricalSummarizationWeightCount()

                # словари каждого предложения с частотностью по словам
                S_with_termfreqs = symmetry.countTermsInsideSents(NO_PARAGRAPHS)
                SYMMETRICAL_WEIGHTS = symmetry.countFinalSymmetryWeight(FINAL_SORTED_TFIDF, S_with_termfreqs,
                                                                        TOTAL_STEMS_IN_TEXT, TOTAL_SENTS_IN_TEXT,
                                                                        STEMMED_PNN)
                ORIGINAL_SENTENCES = symmetry.convertSymmetryToOrdinary(SYMMETRICAL_WEIGHTS, ALLSENTENCES)

                q, rate = symmetry.selectFinalSents(ORIGINAL_SENTENCES)

            else:
                print("There are no words to process!")

        else:
            q = ''

            print("Text should be at least 3 sentences long.")

        output_file = open('output.txt', 'w')
        for sent3 in range(len(q)):
            output_file.write(q[sent3][0] + '\n')
            print(q[sent3][0])

def main():

    maint_text = open('text.txt')
    test = maint_text.read()

    test1 = SUMMARIZER()

    test1.summarize()

if __name__ == '__main__':
    main()