# TCVD-PRA1
## Descripció
En aquesta pràctica s’elabora un cas pràctic orientat a aprendre a identificar les dades rellevants per un projecte analític i usar les eines d’extracció de dades.
Sota l'assignatura de **Tipologia i Cicle de Vida de les Dades** del Màster de Ciència de Dades de la UOC, s'ha creat un programa en **Python 2.7** per tal d'obtenir un *dataset* amb el contingut dels llibres més venuts en l'ultim trimestre a la web de [casadellibro.com](https://www.casadellibro.com).


## Membres del equip
Aquesta pràctica s'ha efectuat a títol individual pel **Jordi Marsal Poy**.


## Fitxers inclosos
* **main.py**: punt d'entrada al programa, on hi ha vàries opcions d'execució segons sigui necessari.
* **jmpcrawler.py**: conté les classes Python. Crawler, Scraper i Book s'utilitzan per implementar la descàrrega i creació del *dataset*.
* **config.ini**: arxiu de configuració per mantenir la última fulla d'índex descarregada i posar un topall a la descàrrega.
* **ConfigParser.py**: imphttps://github.com/jordimarsal/TCVD-PRA1/edit/master/README.mdlementació per Python 2.7 de la classe ConfigParser.py, que és una utilitat per gestionar arxius del tipus **.ini**. S'afegeix per les dificultats d'instalació a Mac, ja que no forma part de la biblioteca estàndard de Python.


## Recursos
Lawson, R. (2015). *Web Scraping with Python*. Packt Publishing Ltd. Capítols 1 i 2.


 :small_blue_diamond:
 

## Dataset
### Títol: books.csv
### Subtítol: més venuts al trimestre
### Imatge
![dataset_books csv](https://user-images.githubusercontent.com/7162023/38779497-af3b6836-40c9-11e8-8868-693fe206a648.jpg)

### Context
El conjunt de dades és la recopilació dels llibres més venuts en l'últim trimestre.


### Contingut
Les dades dels llibres que es recopilen inclouen:
id, author, tittle, category, stars5, stars4, stars3, stars2, stars1, editorial, year, original_price, current_price, link, hash, date
#### A destacar:
 * **id**: NO és el ISBN, identificador únic d'un llibre, no s'ha volgut recopilar aquesta dada intencionadament. En el seu lloc s'ha posat el número d'ordre de més venut, sent més venut el número 1.

 * **category**: inclou totes les categories i subcategories en la que està enmarcada l'obra.

 * **starsN**: número de votacions de N estels.

 * **hash**: format amb el id, nom author, preu i alguna dada més, identifica el canvi d'alguna d'aquestes dades si és modificat.

Les dades s'han recollit descarregant-les entre els dies 08/04/2018 i el 15/04/2018 deixant un MacBook Pro descarregant durant dies o nits, encara que els primers dies havia errors no controlats que detenien la descàrrega.

### Agraïments
Segons sentències a EEUU, la Unió Europea i Australia, només les dades que tenen un autor identificable poden ser susceptibles de drets de copyright. De totes maneres s'agraeix a la web casadellibro.com, on estan ubicades, per no impedir la seva descàrrega.

### Inspiració
És interessant si es té intenció d'aplicar les dades en models de mineria de dades, ja que aquestes es poden agrupar en *clusters* amb poques modificacions, ja sigui per temàtica, preu, autor, etc. A més es poden fer anàlisis d'evolucions de preus i de rànking amb datasets tornats a descarregar cada més, potser per un subconjunt més interessant, com el més votats, ja que són els que la comunitat valora més.

### Llicència
La classe ConfigParser.py té la seva pròpia llicència Python SoftwareFoundation (PSF, http://www.python.org/psf/), que és compatible GPL, és a dir, *opensource*.

Del *dataset*: es publica sota la llicència **Open Database License (ODbL)** que permet als usuaris compartir, modificar i utilitzar lliurement una base de dades mantenint aquesta mateixa llibertat per als demés.

### Notes a l'execució
L'execució està comprobada i s'ha efectuat en un **MacBook Pro** amb **macOS Sierra versió 10.126**. La versió utilitzada de Python és la 2.7.3 (per compatibilitat amb la llibreria **lxml**) amb pip 9.0.2, unicodecsv-0.14.1 i lxxml
