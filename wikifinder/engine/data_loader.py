import queue
import threading
from xml.dom import minidom

from wikifinder.models import Article,WikiDump

class DataLoader():
    def __init__(self, xmlPaths):
        self.xmlPaths = xmlPaths
        self.xmlPages = queue.Queue()
        self.finished_reding_xml =False



    def load_xml_to_queue(self):
        def supertask(xmlPath1, xmlPath2):
            def task(xmlPath):
                qs = WikiDump.objects.filter(name=xmlPath, processed=True)
                if len(qs) == 0 :
                    xmldoc = minidom.parse(xmlPath)
                    pages = xmldoc.getElementsByTagName('page')
                    print(len(pages))
                    for page in pages:
                        title = self.getTextValue(page, 'title')
                        id = self.getTextValue(page, 'id')
                        content = self.getTextValue(page, 'text')
                        self.xmlPages.put(((id, title, content)))
                    w = WikiDump.objects.create(name=xmlPath, processed=True)
                    w.save()
                    if xmlPath == self.xmlPaths[-1]:
                        self.finished_reding_xml = True
            if xmlPath1 is not None:
                thread = threading.Thread(target=task, args=[xmlPath1])
                thread.start()
            if xmlPath2 is not None:
                thread = threading.Thread(target=task, args=[xmlPath2])
                thread.start()

        def runnn():
            i = 0
            while i< len(self.xmlPaths):
                xml1 = self.xmlPaths[i]
                i+=1
                if i< len(self.xmlPaths):
                    xml2 =  self.xmlPaths[i]
                else:
                    xml2 =None

                supertask(xml1, xml2)





        thread = threading.Thread(target=runnn)
        thread.start()


    def getTextValue(self, page, tag):
        return page.getElementsByTagName(tag)[0].lastChild.data

    def build_article(self):
        import time
        processed = 0
        while not self.finished_reding_xml or not self.xmlPages.empty():
            print("work" + str(processed))
            time.sleep(10)
            while not self.xmlPages.empty():
                (id, title, content) =  self.xmlPages.get()
                article = Article(id=id, name=title, text=content)
                article.save()
                processed+=1
        print(processed)


if __name__ == '__main__':
    f = open('/home/przemek/Pulpit/links')



    print("asdas")
    dl = DataLoader("/home/przemek/Dokumenty/agh/projects/my-finder/myfinder/wikifinder/res/enwiki-latest-pages-articles1.xml")
    dl.load_xml_to_queue()
    dl.build_article()
    print('Stated')
