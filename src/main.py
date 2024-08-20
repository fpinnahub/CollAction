
from constants import TEXTS
from utils import get_tei_from_plain_text, jsonfy_witnesses, collate_from_json


# get_tei_from_plain_text(TEXTS['inf_2'])

# inferno_inizi = [
#     "..\\dat\\inferno\\inf_1.txt",
#     "..\\dat\\inferno\\inf_2.txt"
# ]
inf_json_lemmas = '..\\etc\\inf.json'
#
# jsonfy_witnesses(inf_json_lemmas, inferno_inizi)


output_folder = '..\\etc'

collate_from_json(inf_json_lemmas, output_folder, seg=True)
# collate_from_json(inf_json_lemmas, output_folder, seg=False)


### adesso viene generato l'XML come input lemmatizzato, ma va fatta una funzione che generi diret-
### tamente il json - vedere falcon-master/main.py, riga 53;
### poi va considerato l'XML generato dalla collazione e rigenerata/corretta la table; infine va
### guardata la categorizzazione (penultimo punto del README.md).
