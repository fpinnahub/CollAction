
from constants import TEXTS
from utils import get_tei_from_plain_text, jsonfy_witnesses


# get_tei_from_plain_text(TEXTS['inf_2'])
inferno_inizi = [
    "..\\dat\\inferno\\inf_1.txt",
    "..\\dat\\inferno\\inf_2.txt"
]
jsonfy_witnesses('..\\etc\\inf.json', inferno_inizi)


### adesso viene generato l'XML come input lemmatizzato, ma va fatta una funzione che generi diret-
### tamente il json - vedere falcon-master/main.py, riga 53;
### poi va considerato l'XML generato dalla collazione e rigenerata/corretta la table; infine va
### guardata la categorizzazione (penultimo punto del README.md).
