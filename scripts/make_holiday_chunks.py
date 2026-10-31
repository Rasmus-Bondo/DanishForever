# make_holiday_chunks.py - holiday descriptions (pasted from the Data Table tool) -> holidays_chunks_en/names_0000.json
import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work"))   # scripts always run with work/ as the working directory
import json, os

TEXTS = [
"After the sun sets, the end of Midsummer is celebrated, with an hourly firework extravaganza. To watch the show, visit any capital city or Booty Bay.",
"Greatfather Winter is visiting the cities of Ironforge and Orgrimmar, courtesy of Smokywood Pastures. And throughout Azeroth, it is the season to be jolly!",
"The feast of Noblegarden has arrived. The proving grounds of each race, the place where young heroes first test their strength, each holds cleverly hidden treasure eggs. How many can you find?",
"Show an orphan what the hero's life is like! Visit Orphan Matron Nightingale in Stormwind or Orphan Matron Battlewail in Orgrimmar and make a child's dream come true.",
"The Darkmoon Faire is here, this time in idyllic Elwynn Forest. Meet Silas Darkmoon and his troupe, play games that test mind and nerve, and behold exotic sights from the four corners of Azeroth... and beyond!",
"The Darkmoon Faire is here, this time at the foot of Thunder Bluff. Meet Silas Darkmoon and his troupe, play games that test mind and nerve, and behold exotic sights from the four corners of Azeroth... and beyond!",
"The battle for Alterac Valley grows intense. Greater honor is given to those who pledge sword to their liege and battle in Alterac.",
"The battle for Warsong Gulch grows intense. Greater honor is given to those who pledge sword to their liege and battle in the Gulch.",
"The battle for Arathi Basin grows intense. Greater honor is given to those who pledge sword to their liege and battle in Arathi.",
"A fishing tournament, held along the coasts of Stranglethorn Vale. Catch as many tastyfish as you can! Will you be the master fisherman who catches forty fish first and wins the grand prize?",
"The Harvest Festival is a time to commemorate those who have sacrificed their lives to help friends and allies. Feasts are held outside Orgrimmar and Ironforge in honor of these fallen heroes.",
"Hallow's End celebrates the break of the Forsaken from the Scourge. Fun and mischief reign as the Innkeepers of Azeroth give treats, and tricks, to whomever asks.",
"Every year the druids of Moonglade hold a celebration of their city's great triumph over an ancient evil. During the Lunar Festival, citizens of Azeroth have the opportunity to honor their elders by celebrating their sage wisdom, sharing in magnificent feasts, and of course... shooting lots of fireworks!",
"Something is in the air in the major cities of Azeroth. Many guards and townsfolk spend their days giving and receiving gifts to other amorous citizens.",
"A time of merriment and celebration, dedicated to the hottest season of the year.",
"The battle at Darkspear Islands is heating up. Join up and prove your might!",
]

texts = sorted(set(TEXTS), key=lambda s: (s.lower(), s))
os.makedirs("holidays_chunks_en", exist_ok=True)
with open("holidays_chunks_en/names_0000.json", "w", encoding="utf-8") as f:
    json.dump([{"i": i, "en": t} for i, t in enumerate(texts)], f, ensure_ascii=False, indent=1)
print(len(texts), "unique holiday descriptions; 1 chunk")
