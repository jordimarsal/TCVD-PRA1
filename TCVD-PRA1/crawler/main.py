# -*- coding: utf-8 -*-
'''
Created on 15 abr. 2018

@author: Jordi Marsal
'''

from jmpcrawler import Crawler, Scraper

#######################################
#    POSSIBLES EXECUCIONS
#######################################

url= "https://www.casadellibro.com" 
# Després del igual s'afegirà el número de pàgina i el UDM (una mena d'índex) de forma iterativa
exten='/busqueda-ebooks?idtipoproductopen=0&idtipoproducto=9&spellcheck=1&ordenar=10&idioma=6&nivel=1&itemxpagina=60&page='

cr = Crawler(url) 
# 1 = down
# 2,3,4 = util
run='Select your option'

if (run == '1'):
    # posa en marxa el bucle principal de descàrrega
    cr.addExtension(exten)
    cr.download()
    
if (run == '2'):
    #descarrega la url d'un llibre concret per poder fer-hi proves
    url2 = "https://www.casadellibro.com/ebook-esquemas-rotos-y-brujulas-desviadas-ebook/9788417275143/6308178"
    html=cr.downloadUrl(url2,3).strip()
    cr.saveHtml('book1.html', html)
    print 'book1.html generat'
    
if (run == '3'):
    # Prova d'extracció de qualificacions
    scrap = Scraper()
    scrap.loadFile('book1.html')
    st = scrap.getStars()
    print 'Qualificacions (estels):',st

if (run == '4'):
    # Prova de descàrrega de full d'índex que conté 60 ebooks invariablement, amb els sus link i altres informacions
    # Serveix per completar cada llibre descarregant les categories al seu link particular i imprimir la linia al csv
    # Es una prova del comportament dins del bucle principal
    url3 = "https://www.casadellibro.com/busqueda-ebooks?idtipoproductopen=0&idtipoproducto=9&spellcheck=1\
&ordenar=10&idioma=6&nivel=1&itemxpagina=60&page=20&&udm=20"
    html=cr.downloadUrl(url3,3).strip()
    cr.saveHtml('output.html', html)
    scrap = Scraper()
    scrap.loadFile('output.html')
    scrap.saveBooks()