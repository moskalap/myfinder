import csv
import re

import numpy as np
import scipy.sparse as sp
from nltk.stem.snowball import SnowballStemmer

from wikifinder.models import Article, Words, WordsCount, ArticleToMatrix, WordToMatrix, Matrix


class DataProcessor():
    def __init__(self):
        self.words = {}
        self.wordscount = []
        self.articles_by_index = {}
        self.articles_by_id = {}
        self.words_by_index = {}
        self.words_by_id = {}
        self.stemmer = SnowballStemmer('english')
        self.computet = False
        self.m = Words.objects.count()
        self.n = Article.objects.count()

    def load_matrix_from_csv(self):
        self.m = Words.objects.count()
        self.n = Article.objects.count()
        row = []  # word
        col = []  # article
        data = []
        i = 0
        with open('/home/przemek/Dokumenty/agh/projects/my-finder/myfinder/wikifinder/res/main_wikifinder_matrix.csv',
                  'r') as csvfile:
            for en in csv.reader(csvfile):
                col.append(int(en[1]))
                row.append(int(en[2]))
                data.append(int(en[3]))

        # idf
        from collections import Counter
        self.counts = Counter(row)
        im = len(data)
        for i in range(im):
            if i % 10000 == 0:
                print(i / im)
            nw = self.counts[row[i]]
            data[i] = np.log(self.m / nw) * data[i]

        self.glob_mat = sp.csr_matrix((np.array(data), (np.array(row), np.array(col))), shape=(self.m, self.n))
        self.computet = True

        return self.glob_mat

    def load_matrix(self):
        self.m = Words.objects.count()
        self.n = Article.objects.count()
        print("({}, {})".format(self.m, self.n))
        row = []
        col = []
        data = []
        i = 0
        mats = Matrix.objects.all()
        for mat in mats:
            i += 1
            print(' {} / {}'.format(i, len(mats)))
            row.append(mat.row)
            col.append(mat.col)
            data.append(mat.data)
        return row, col, data, self.m, self.n

    def build_matrix(self):
        articles = Article.objects.all()
        i = 0
        art_to_mat = []
        words_to_mat = []
        for a in articles:
            self.articles_by_index[i] = a.id
            self.articles_by_id[a.id] = i

            art_to_mat.append(ArticleToMatrix(article_id=a.id, col_no=i))

            i += 1
            print('Fetching articles ({}/{})'.format(i, len(articles)))
        words = Words.objects.all()
        self.n = len(self.articles_by_id)
        i = 0
        for w in words:
            self.words_by_index[i] = w.word
            self.words_by_id[w.word] = i
            words_to_mat.append(WordToMatrix(word_id=w.word, row_no=i))
            i += 1
            print('Fetching words ({}/{})'.format(i, len(words)))
        self.m = len(self.words_by_id)
        print("Creating matrix ({}, {})".format(self.m, self.n))
        row = []  # words
        col = []  # article
        data = []
        i = 0
        WordToMatrix.objects.bulk_create(words_to_mat)
        ArticleToMatrix.objects.bulk_create(art_to_mat)
        matrix = []
        wcss = WordsCount.objects.all()
        for a in articles:
            wcs = wcss.filter(article_id=a.id)
            article_index = self.articles_by_id[a.id]
            for w in wcs:
                word_index = self.words_by_id[w.word.word]
                matrix.append(Matrix(row=article_index, col=word_index, data=w.count))
                row.append(article_index)
                col.append(word_index)
                data.append(w.count)

            i += 1
            print('Fetching wc ({} / {})'.format(i, len(articles)))
        print('serialization')
        Matrix.objects.bulk_create(matrix)
        print('serialized')
        from scipy.sparse import csr_matrix
        self.A = csr_matrix((data, (col, row)), shape=(self.m, self.n)).todense()
        print(self.A[0:100, :])

    def build_Db(self):
        ars = Article.objects.all()
        ind = 0
        l = len(ars)
        for a in ars:
            ind += 1
            print(ind / l)
            self.process_contnet(a)

    def fun(self, x):
        self.articles[x.id] = (x.title, x.text)

    def process_contnet(self, article):
        wc_dict = {}
        text = article.text
        text = text.replace(".", " ").replace(",", " ").replace('"', ' ').replace('(', ' ').replace('-', ' ').replace(
            '*', ' ')
        for t in text.split():
            if not hasdig(t):
                n_w = self.stem(t.lower())
                if n_w is not None:
                    word = None
                    if n_w in self.words.keys():
                        word = self.words.get(n_w)
                    else:
                        word = Words(word=n_w)
                        word.save()
                        self.words[n_w] = word

                    if n_w in wc_dict:
                        wc_dict[n_w] = wc_dict[n_w] + 1
                    else:
                        wc_dict[n_w] = 1
        self.serialize(article, wc_dict)

    def stem(self, wor):
        try:
            return self.stemmer.stem(wor)
        except Exception:
            return wor

    def serialize(self, article, wc_dict):
        for k in wc_dict.keys():
            if self.words[k] == None:
                print("SADA")
            self.wordscount.append(WordsCount(article=article, word=self.words[k], count=wc_dict[k]))

    def idf(self):

        pass

    def query(self, query):
        vector = np.zeros((1, self.m))
        print(query)
        for w in query.split():
            w = self.stem(w.lower())
            w2m = WordToMatrix.objects.filter(word_id=w).all()[0]
            if w2m is None:
                print("None")
            else:
                print(w2m.row_no)
                vector[0, w2m.row_no] += 1

        vector = sp.csc_matrix(vector)
        similarity = [np.math.fabs(s) for s in (vector * self.glob_mat).toarray()[0]]
        art2sim = [(similarity[i], i) for i in range(len(similarity))]
        best = sorted(art2sim, key=lambda x: x[0])[-10:]
        scores = {i[1]: i[0] for i in art2sim}
        bes_q = [b[1] for b in best]
        print('quering {}'.format(bes_q))
        ar = {a.col_no: a.article_id for a in ArticleToMatrix.objects.filter(col_no__in=bes_q).all()}
        result = []
        for a in ar.keys():
            result.append((scores[a], Article.objects.filter(id=ar[a]).all()[0]))

        return result


RE_D = re.compile('\d')


def hasdig(string):
    return RE_D.search(string)
