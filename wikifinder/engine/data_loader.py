import queue
import re
import threading
from html.entities import name2codepoint
from threading import RLock
from xml.dom import minidom

from multiprocessing import Process

from wikifinder.models import Article,WikiDump, Words
import re

# Media and categories; the codes for these differ per language.
# We have the most popular ones (>900.000 articles as of July 2012) here,
# as well as Latin, which is useful for testing.
# Add other languages as required.
_MEDIA_CAT = """
  [Ii]mage|[Cc]ategory      # English
 |[Aa]rchivo                # Spanish
 |[Ff]ile                   # English, Italian
 |[CcKk]at[ée]gor[íi][ea]   # Dutch, German, French, Italian, Spanish, Polish, Latin
 |[Bb]estand                # Dutch
 |[Bb]ild                   # German
 |[Ff]icher                 # French
 |[Pp]lik                   # Polish
 |[Ff]asciculus             # Latin
"""

_UNWANTED = re.compile(r"""
  (:?
    \{\{ .*? \}\}                           # templates
  | \| .*? \n                               # left behind from templates
  | \}\}                                    # left behind from templates
  | <!-- .*? -->
  | <div .*?> .*? </div>
  | <math> .*? </math>
  | <nowiki> .*? </nowiki>
  | <ref .*?> .*? </ref>
  | <ref .*?/>
  | <span .*?> .*? </span>
  | \[\[ (:?%s): (\[\[.*?\]\]|.)*? \]\]
  | \[\[ [a-z]{2,}:.*? \]\]                 # interwiki links
  | =+                                      # headers
  | \{\| .*? \|\}
  | \[\[ (:? [^]]+ \|)?
  | \]\]
  | '{2,}
  )
""" % _MEDIA_CAT,
re.DOTALL | re.MULTILINE | re.VERBOSE)


def text_only(text):
    return _UNWANTED.sub("", text)

class DataLoader():
    def __init__(self, xmlPaths):
        self.lock = RLock()
        self.xmlPaths = xmlPaths
        self.xmlPages = queue.Queue()
        self.articles_to_serialize = queue.Queue()
        self.words_to_serialize = queue.Queue()
        self.words = set()
        self.finished_reding_xml =False


    def create_db(self, xmlPath):
        xmldoc = minidom.parse(xmlPath)
        pages = xmldoc.getElementsByTagName('page')
        for page in pages:
            title = self.getTextValue(page, 'title')
            id = self.getTextValue(page, 'id')
            content = text_only(self.getTextValue(page, 'text'))
            self.post_procces_artice(content)





    def load_xml_to_queue(self):
        self.build_article()
        def supertask(xmlPath1, xmlPath2,ar_q, w_q, words):
            def task(xmlPath, ar_q, w_q, words):
                qs = WikiDump.objects.filter(name=xmlPath, processed=True)
                if len(qs) == 0 :
                    print('--ar q {}'.format(ar_q))
                    print('--w q {}'.format(w_q))
                    xmldoc = minidom.parse(xmlPath)
                    pages = xmldoc.getElementsByTagName('page')
                    print('supertaskdone'+ str(len(pages)))
                    for page in pages:




                    w = WikiDump.objects.create(name=xmlPath, processed=True)
                    w.save()
                if xmlPath == self.xmlPaths[-1]:
                   self.finished_reding_xml = True
            if xmlPath1 is not None:
                print('xml1', xmlPath1)
                thread1 = Process(target=task, args=[xmlPath1, ar_q, w_q, words])
                thread1.start()
            if xmlPath2 is not None:
                print('xml2', xmlPath2)
                thread2 = Process(target=task, args=[xmlPath2,ar_q, w_q, words])
                thread2.start()

            thread1.join()

        def runnn(r_q, w_q, words):
            i = 0
            while i< len(self.xmlPaths):
                xml1 = self.xmlPaths[i]
                i+=1
                if i< len(self.xmlPaths):
                    xml2 =  self.xmlPaths[i]
                    i+=1
                else:
                    xml2 =None

                supertask(xml1, xml2, r_q, w_q, words)





        thread = Process(target=runnn, args=[self.articles_to_serialize, self.words_to_serialize, self.words])
        thread.start()


    def getTextValue(self, page, tag):
        try:
            to_ret =  page.getElementsByTagName(tag)[0].lastChild.data
            return to_ret
        except Exception:
            print('nil')

            return ''

    def build_article(self):
        import time
        def words_serializator(wrc):
            print('word q {}'.format(wrc))
            word_proccessed = 0
            while not self.finished_reding_xml or not wrc.empty():
                time.sleep(10)
                while not wrc.empty():
                    word_proccessed += 1
                    try:
                        word = wrc.get()
                        Words.objects.create(word=word).save()
                    except Exception:
                        print('ups')

                print('word proccesed {}'.format(word_proccessed))



        def article_serializator(arc):
            print('article q {}'.format(arc))
            processed_ar = 0
            while not self.finished_reding_xml or not arc.empty():
                time.sleep(10)
                while not arc.empty():
                    (id, title, content) = arc.get()
                    try:

                        article = Article(id=id, name=title, text=content, processed=True).save()

                    except Exception:
                        print('ups')

                    processed_ar += 1
                print('article proccesed {}'.format(processed_ar))

        t1 = Process(target=article_serializator, args=[self.articles_to_serialize])
        t2 = Process(target=words_serializator, args = [self.words_to_serialize])
        t1.start()
        t2.start()




    def unescape(self, text):
        """
        Removes HTML or XML character references and entities from a text string.
        :param text The HTML (or XML) source text.
        :return The plain text, as a Unicode string, if necessary.
        """

        def fixup(m):
            text = m.group(0)
            code = m.group(1)
            try:
                if text[1] == "#":  # character reference
                    if text[2] == "x":
                        return chr(int(code[1:], 16))
                    else:
                        return chr(int(code))
                else:  # named entity
                    return chr(name2codepoint[code])
            except:
                return text  # leave as is

        return re.sub("&#?(\w+);", fixup, text)

    def post_procces_artice(self, text):
        text = text.replace('.', '').replace(', ', '').replace('"','')
        for t in text.split():
            if not hasdig(t):
                if t.lower() not in words:
                    words.add(t.lower())
                    w_q.put(t.lower())



RE_D = re.compile('\d')
def hasdig(string):
    return RE_D.search(string)





if __name__ == '__main__':
    f = open('/home/przemek/Pulpit/links')
    print("asdas")
    dl = DataLoader("/home/przemek/Dokumenty/agh/projects/my-finder/myfinder/wikifinder/res/enwiki-latest-pages-articles1.xml")
    dl.load_xml_to_queue()
    dl.build_article()
    print('Stated')
