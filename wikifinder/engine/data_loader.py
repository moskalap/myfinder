import re
from html.entities import name2codepoint
from xml.dom import minidom

from wikifinder.models import Article, Words

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
        self.xmlPaths = xmlPaths
        self.articles = {}
        self.words = set()
        self.wordsob = []

    def create_db(self):
        xmldoc = minidom.parse(self.xmlPaths[0])
        pages = xmldoc.getElementsByTagName('page')
        a = Article()
        articles = Article.objects.all().values()
        self.words = set(map(lambda x: x.word, Words.objects.all()))
        i = 0
        for page in pages:
            print(i / len(pages))
            i += 1
            title = self.getTextValue(page, 'title')
            id = self.getTextValue(page, 'id')
            if not len(articles.filter(id=id).values()) > 0:
                content = text_only(self.getTextValue(page, 'text'))
                self.post_procces_artice(content)
                print('{} / {}'.format(i, len(pages)))
                article = Article(name=title, text=content, id=id)
                self.articles[id] = article
                # article.save()
                self.post_procces_artice(text=content)
        Article.objects.bulk_create(self.articles.values())
        Words.objects.bulk_create(self.wordsob)

    def getTextValue(self, page, tag):
        try:
            to_ret = page.getElementsByTagName(tag)[0].lastChild.data
            return to_ret
        except Exception:
            print('nil')

            return ''

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
        text = text.replace('.', '').replace(', ', '').replace('"', '')
        for t in text.split():
            if not hasdig(t):
                if t.lower() not in self.words:
                    self.words.add(t.lower())
                    word = Words(word=t.lower())
                    self.wordsob.append(word)


RE_D = re.compile('\d')


def hasdig(string):
    return RE_D.search(string)
