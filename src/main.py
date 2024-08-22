
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




# meravigliosamente = [
#     "..\\dat\\fake_input\\Meravigliosamente\\prova1.txt",
#     "..\\dat\\fake_input\\Meravigliosamente\\prova2.txt",
#     "..\\dat\\fake_input\\Meravigliosamente\\prova3.txt",
# ]
merav_json_lemmas = '..\\etc\\merav.json'
# jsonfy_witnesses(merav_json_lemmas, meravigliosamente)





output_folder = '..\\etc'

# collate_from_json(inf_json_lemmas, output_folder, seg=True)
# collate_from_json(inf_json_lemmas, output_folder, seg=False)



collate_from_json(merav_json_lemmas, output_folder + '\\merav', seg=True)


### adesso viene generato l'XML come input lemmatizzato, ma va fatta una funzione che generi diret-
### tamente il json - vedere falcon-master/main.py, riga 53;
### poi va considerato l'XML generato dalla collazione e rigenerata/corretta la table; infine va
### guardata la categorizzazione (penultimo punto del README.md).
