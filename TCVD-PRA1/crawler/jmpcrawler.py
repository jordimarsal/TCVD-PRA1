# -*- coding: utf-8 -*-
'''
Created on 20 mar. 2018 - 15 Apr 2018

@author: Jordi Marsal
'''

import urllib2
import re
import lxml.html
import unicodecsv as csv
import hashlib
import ConfigParser
import time
import random


##################################
#     CONFIG
##################################

# Classe Config
# Gestió del arxiu config.ini, on es van guardant el numéro d'iteracions per tal de reprende la descàrrega
# seqüencialment i altres dades usades, inclós avisos.
class Config:
    def __init__(self):
        self.fileName = 'config.ini'
        self.__config = ConfigParser.RawConfigParser()
        self.__config.read(self.fileName)
        iteration = int(self.getIteration())
        if (iteration > 1):
            self.__config.set('Common','iteration',iteration +1)
    
    def saveIteration(self,iteration):
        self.__config.set('Common','iteration',iteration)
        self.commit()
        
    def getIteration(self):
        ret = self.__config.get('Common','iteration')
        return ret
    
    def getMax(self):
        ret = self.__config.get('Common','max')
        return ret
    
    def commit(self):
        with open(self.fileName,'w') as cfgfile:
            self.__config.write(cfgfile)
            
    def saveAlert(self,alert):
        #self.__config.add_section('Alerts'+url)
        self.__config.set('Alerts', 'errorAlert',alert)
        self.commit()


##################################
#     CRAWLER
##################################

class Crawler:
    # Classe per la gestió de la descàrrega, pren una url base a la que s'afegeix una més específica per començar a descarregar
    global RETRIES
    global HEADER_FIREFOX
    RETRIES = 5
    HEADER_FIREFOX = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
    URL_UDM = [130,210,300,390,480,570,660,750,840,930,1020,1110,1200,1290,1380,1470,1560,1650,1740,1830,1920,2100]
    def __init__(self, baseUrl, needScraper=None):
        self.baseUrl = baseUrl
        # per evitar errors quan es crida la classe Crawler dins del Scraper
        if (needScraper is None):
            self.config = Config()
            self.scraper = Scraper()
        self.html = ""
        self.ext = []
        self.setUserAgent('Firefox')
    
    # Mètode downloadUrl
    # Descarrega una url donada
    # * Paràmetre url: url
    # * Paràmetre num_retries: numero d'intents
    def downloadUrl(self,url, num_retries):
        print 'Downloading:', url
        headers = {'User-agent': self.user_agent}
        request = urllib2.Request(url,headers = headers)
        try:
            html = urllib2.urlopen(request).read()
        except urllib2.URLError as e:
            print 'Download error:', e.reason
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    # recursively retry 5xx HTTP errors
                    return self.downloadUrl(url, num_retries-1)
            html = None
        return html
    
    # Mètode getAUrl
    # Crea una url a partir de la iteració
    # * Paràmetre iteration: número d'iteració
    def getAUrl(self, iteration):
        try:
            extension = self.ext[0]
            url = self.baseUrl + extension + str(iteration) + self.getUdm(iteration)
        except IndexError as e:
            print(e)
            url = None
        
        return url
    
    # Mètode getUdm
    # Crea una part de la url que depén de la iteració
    # * Parametre it: número d'iteració
    def getUdm(self,it):
        udm = 0
        if it <= 130:
            udm = 130
        else:
            offset = (it - 130) / 90
            udm = Crawler.URL_UDM[offset]
        return '&udm=' + str(udm)
    
    # Mètode getUdm
    # Bucle principal per grimpar per la web
    def download(self):
        maxim = int(self.config.getMax()) +1
        frm = int(self.config.getIteration())
        
        for i in range(frm,maxim):
            url = self.getAUrl(i)
            self.html = self.downloadUrl(url,RETRIES)
            # la extracció de dades es dóna a la classe Scraper
            isOk = self.scraper.saveBooks(self.html)
            if not isOk:
                self.config.saveAlert('PAGINA BUIDA, ERROR AL UDM? url: '+url)
                print "ERROR: PÀGINA BUIDA S'ha detingut l'execució del programa"
                # s'ha de detenir l'execució perquè no es desin números d'iteració amb resultat buit, seria error del 
                # UDM, ja sigui per error del server o per haber acabat les iteracions.
                # per la cerca que em escollit "més venuts en el trimestre" només hi ha 2090 fulls d'index amb 60 e-books
                # cadascún. Aproximadament 125.000 llibres (hi ha llibres que no tenen la seva url amb contingut correcte)
                exit(0)
            else:           
                self.config.saveIteration(i)
                self.delay(2)
    
    def delay(self,seconds):
        elapse = seconds + seconds * random.random()
        time.sleep(elapse)
    
    def printHtml(self):
        print(self.html)
    
    def addExtension(self,extension):
        self.ext.append(extension)
    
    # Mètode saveHtml
    # La classe també permet descàrregues individuals i guardar el html, per fer proves
    def saveHtml(self, namefile=None, html=None):
        if (namefile == None):
            namefile = "output.html"
        if (html==None):
            html = self.html
        f=open(namefile,"w")

        for r in html:
            f.write(r)

        f.close()
        
    # Setter
    def setUserAgent(self, useragent):
        if (useragent == 'Firefox'):
            useragent = HEADER_FIREFOX
        self.user_agent= useragent
    
    def crawl_sitemap(self,url):
        # no usat, la pàgina que s'analitza no en té
        sitemap = self.downloadUrl(url + '/sitemap.xml',2)
        if (sitemap == None):
            sitemap = 'NONE'
        print 'sitemap:\n' + sitemap
    
    def link_crawler(self,seed_url, link_regex):
        # no usat, pero es manté per si cal en el futur a alguna pàgina concreta
        crawl_queue = [seed_url]
        while crawl_queue:
            url = crawl_queue.pop()
            html = self.download(url)
            # filter for links matching our regular expression
            for link in self.get_links(html):
                if re.match(link_regex, link):
                    crawl_queue.append(link)
    
    def get_links(self,html):
        # Retorna la llista de links del html, usada per link_crawler
        webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',
            re.IGNORECASE)
        return webpage_regex.findall(html)   
    

#######################################
# BOOK
#######################################

# Classe Book
# Model del llibre per desar les dades en fileres
class Book:
    def __init__(self, book, num):
        self.id_b = num
        self.book = book
        titl = 'title-link'
        auth = 'book-header-2-subtitle-author'
        edit = 'mod-libros-editorial'
        prOri = 'priceOriginal'
        prCurr = 'currentPrice'
        
        self.html = lxml.html.tostring(book)
        
        self.links = self.get_links(self.html)
        self.link = self.links[2]
        self.author = self.get_text(book,auth)
        self.title = self.get_text(book,titl)
        ed = self.stripall(self.get_text(book,edit).strip()).split(",")
        self.year = '2018'
        self.editorial = ed[0]
        if (len(ed) > 1):
            self.year = ed[1]
        self.priceOri = self.get_text(book,prOri)
        self.priceCurr = self.get_text(book,prCurr)
        self.date = time.strftime("%d/%m/%Y")
        
        self.toString = self.author + ',' + self.title + ',' + self.editorial + ','+ self.year + ',' + self.priceOri + ',' + self.priceCurr + ',' + self.link
        # el hash serviria per detectar algun canvi al tornar a passar pel link
        self.hash = self.__getHash(self.toString)
    
    # Mètode get_text
    # Crea una part de la url que depén de la iteració
    # * Paràmetre el: element lxml corresponent a un llibre
    # * Paràmetre class_name: classe css d'on s'extreu el text
    def get_text(self,el,class_name):
        els = el.find_class(class_name)
        if els:
            return els[0].text_content()
        else:
            return ''
        
    # Mètode get_links
    # Extreu els enllaços d'un html
    def get_links(self,html):
        webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',
            re.IGNORECASE)
        return webpage_regex.findall(html)
    
    # Mètode stripall
    # Extreu els espais a partir de la coma, per dividir el text "EDITORIAL ALGUNA, ANY"
    def stripall(self,string):
        tmp_list = []
        isDel = False
        for char in string:
            if (isDel):
                if char != " ":
                    tmp_list +=char
            else:
                tmp_list +=char
            if char == ",":
                isDel = True
        return "".join(tmp_list)
    
    # getter
    def getBook(self):
        return self.toString
    
    # setter
    def setStars(self,stars):
        self.stars=stars
    
    # Mètode getRow
    # Crea la filera que es grabarà
    def getRow(self):
        ret = []
        ret.append(self.id_b)
        ret.append(self.author)
        ret.append(self.title)
        ret.append(self.category)
        ret.extend(self.stars)
        ret.append(self.editorial)
        ret.append(self.year)
        ret.append(self.priceOri)
        ret.append(self.priceCurr)
        ret.append(self.link)
        ret.append(self.hash)
        ret.append(self.date)
        return ret
    
    # Mètode __getHash
    # Crea el hash
    def __getHash(self,string):
        hashObject = hashlib.md5(string.encode('utf-8'))
        return hashObject.hexdigest()
    

#######################################
#     SCRAPER
#######################################

class Scraper:
    CBOOK = 1
    CCATEGORY = 2 
    CSTARS = 3
    def __init__(self):
        self.html = ''
        self.__initCsv()
    
    def __initCsv(self):
        # inicialitza el csv, creant-lo si no hi és o contant les fileres si ja existia, per tal de continuar la descàrrega
        f = None
        try:
            f = open('books.csv','r')
        except:
            pass
        
        if f:
            reader = csv.reader(f, delimiter = ',')
            self.row_count = sum(1 for row in reader)
            f.close()
            self.writer = csv.writer(open('books.csv','a'), encoding='utf-8',errors='ignore')
        else:
            self.writer = csv.writer(open('books.csv', 'w'), encoding='utf-8',errors='ignore')
            self.fields = ('id','author', 'tittle','category','stars5','stars4','stars3','stars2','stars1', 'editorial', 'year','original_price',
               'current_price', 'link','hash','date')
            self.row_count = 1
            self.writer.writerow(self.fields)
        
    def loadFile(self,filename):
        # carrega un arxiu de text com a html
        f=open(filename,"r")
        self.html = f.read()
        
    def setHtml(self,html):
        # settet
        self.html = html
        
    def __printh(self):
        print self.html
        
    def __get_lxml(self,html,clase):
        # retorna l'arbre (tree) per una clase css indicada d'un html subministrat
        tree = lxml.html.fromstring(html)
        td = tree.cssselect(clase)
        return td
    
    def __get_lxmlWhat(self,html,what):
        # assigna la classe css per a cada un del casos
        if (what == Scraper.CBOOK):
            clase = 'div.mod-list-item'
        elif (what == Scraper.CCATEGORY):
            clase = 'li.expmat'
        elif (what == Scraper.CSTARS):
            clase = 'div.book-values-detail-a'
        return self.__get_lxml(html,clase)
    
    def saveBooks(self,html=None):
        # extreu les dades de la pàgina índex i per cada llibre el completa amb dades del seu propi link
        # escriu finalment cada filera amb les dades d'un llibre
        if (html != None):
            self.html = html
        books=[]
        lxmlbooks = self.__get_lxmlWhat(self.html,Scraper.CBOOK)
        for num, book in enumerate(lxmlbooks,start=int(self.row_count -1)):
            tB = Book(book,num)
            tB = self.depthCompletion(tB)
            books.append(tB.getRow())
        
        i = self.row_count - 1
        for row in books:
            print row
            self.writer.writerow(row)
            i+=1
        self.row_count = i
        print str(self.row_count) + " lines"
        if not lxmlbooks:
            return False
        else: return True
        
    def depthCompletion(self,book):
        url= "https://www.casadellibro.com"
        crw = Crawler(url, False)
        self.delay(0.5)
        try:
            html = crw.downloadUrl(url+book.link, 3).strip()
        except: html = None
        if (html is None or len(html)==0):
            book.category = "-"
            book.setStars([0,0,0,0,0])
        else:
            book.category = self.getCategory(html)
            book.setStars(self.getStars(html))
        return book
    
    def delay(self,seconds):
        elapse = seconds + seconds * random.random()
        time.sleep(elapse)
        
    def getCategory(self,html):
        catElement = self.__get_lxmlWhat(html, Scraper.CCATEGORY)
        if type(catElement) is list:
            cat=[]
            for i,el in enumerate(catElement,start=0):
                hel = el.text_content().strip()               
                substring = hel.split('\n')
                hel = substring[0]
                cat.append(hel)
            stringCat = '-'.join(cat)
        else: stringCat = catElement.text_content().strip()
        print stringCat
        return stringCat
    
    def getStars(self,html=None):
        if (html == None):
            html = self.html
        stElem = self.__get_lxmlWhat(html, Scraper.CSTARS)
        #ht2 = lxml.html.tostring(stElem[0])
        try:
            stList = stElem[0].text_content().split()
        except:
            return [0,0,0,0,0]
        stars = []
        for i,el in enumerate(stList):
            if (i > 1):
                it = int(re.sub("[^0-9]","",el))
                stars.append(it)
        print stars
        return stars
    
        
        
