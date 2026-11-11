local _, ns = ...

-- Small hand-made lookup sets: resources, creature families, forms, dispel types, mechanics, totem categories,
-- quest and achievement categories, classes, races, PvP ranks and honor titles. Entries already in ns.Exact are kept.
local t = {
    -- bottom bar (micro button) tooltips; the keybinding "(C)" is split off by tr() in Core.lua
    ["Character Info"] = "Karakterinfo", ["Spellbook & Abilities"] = "Besværgelsesbog & Evner", ["Talents"] = "Begavelser",
    ["Quest Log"] = "Quest-logbog", ["Social"] = "Socialt", ["World Map"] = "Verdenskort", ["Main Menu"] = "Spilmenu",
    ["Achievements"] = "Bedrifter", ["Guild"] = "Klan", ["Collections"] = "Samlinger", ["Adventure Guide"] = "Eventyrvejledning",
    ["Group Finder"] = "Gruppefinder", ["Dungeon Finder"] = "Fangehulsfinder", ["Professions"] = "Erhverv",
    ["Game Menu"] = "Spilmenu", ["Help"] = "Hjælp", ["Shop"] = "Butik", ["Bags"] = "Tasker", ["Backpack"] = "Rygsæk",
    -- "Unique-Equipped: <category> (n)": these are item limit category names, not item names
    ["Jeweled Healing Focus"] = "Juvelbesat Helingsfokus", ["Crystallized Tear"] = "Krystalliseret Tåre",
    -- character window stat labels
    ["Armor:"] = "Rustning:", ["Defense:"] = "Forsvar:", ["Damage:"] = "Skade:", ["Power:"] = "Kraft:", ["Attack:"] = "Angreb:",
    ["Attack Power:"] = "Angrebskraft:", ["Speed:"] = "Hastighed:", ["Rating:"] = "Vurdering:", ["Crit Chance:"] = "Kritisk chance:",
    ["Dodge:"] = "Undvigelse:", ["Parry:"] = "Parering:", ["Block:"] = "Blokering:", ["Resilience:"] = "Sejhed:",
    ["Balance"] = "Ligevægt", ["All Runes"] = "Alle Runer",
    -- power types
    ["Mana"] = "Mana", ["Rage"] = "Raseri", ["Focus"] = "Fokus", ["Energy"] = "Energi", ["Happiness"] = "Lykke",
    ["Runes"] = "Runer", ["Runic Power"] = "Runekraft", ["Combo Points"] = "Kombopoint", ["Health"] = "Helbred",
    ["Soul Shards"] = "Sjælesplinter", ["Holy Power"] = "Hellig Kraft", ["Chi"] = "Chi", ["Insanity"] = "Vanvid",
    ["Fury"] = "Vrede", ["Pain"] = "Smerte", ["Maelstrom"] = "Malstrøm", ["Lunar Power"] = "Måne-kraft",
    ["Arcane Charges"] = "Arkane Ladninger", ["Alternate"] = "Alternativ",

    -- creature families (hunter pets)
    ["Bat"] = "Flagermus", ["Bear"] = "Bjørn", ["Boar"] = "Vildsvin", ["Carrion Bird"] = "Ådselsfugl", ["Cat"] = "Kat",
    ["Crab"] = "Krabbe", ["Crocolisk"] = "Krokolisk", ["Gorilla"] = "Gorilla", ["Hyena"] = "Hyæne", ["Raptor"] = "Rovfugl",
    ["Scorpid"] = "Skorpid", ["Serpent"] = "Slange", ["Spider"] = "Edderkop", ["Tallstrider"] = "Højstrider",
    ["Turtle"] = "Skildpadde", ["Wind Serpent"] = "Vindslange", ["Wolf"] = "Ulv", ["Dragonhawk"] = "Dragehøg",
    ["Felhunter"] = "Fæl-jæger", ["Imp"] = "Smådjævel", ["Voidwalker"] = "Tomrumsvandrer", ["Succubus"] = "Succubus",
    ["Doomguard"] = "Undergangsvagt", ["Infernal"] = "Helvedesbæst", ["Water Elemental"] = "Vandelementar",
    ["Ghoul"] = "Ghul", ["Mechanical"] = "Mekanisk", ["Nether Ray"] = "Nethergrad", ["Ravager"] = "Hærgerdyr",
    ["Sporebat"] = "Sporeflagermus", ["Warp Stalker"] = "Fordrejningsluskerne", ["Moth"] = "Møl", ["Chimaera"] = "Kimære",
    ["Devilsaur"] = "Djævlesaurus", ["Silithid"] = "Silithid", ["Worm"] = "Orm", ["Rhino"] = "Næsehorn", ["Wasp"] = "Hveps",
    ["Core Hound"] = "Kernehund", ["Spirit Beast"] = "Åndedyr", ["Monkey"] = "Abe", ["Aquatic"] = "Vanddyr",
    ["Dog"] = "Hund", ["Beetle"] = "Bille", ["Tiger"] = "Tiger", ["Bird of Prey"] = "Rovfugl", ["Owl"] = "Ugle",
    ["Hawk"] = "Høg", ["Pig"] = "Gris", ["Ram"] = "Vædder", ["Goat"] = "Ged", ["Horse"] = "Hest", ["Skeleton"] = "Skelet",

    -- shapeshift forms and stances
    ["Bear Form"] = "Bjørneform", ["Dire Bear Form"] = "Frygtbjørne-form", ["Cat Form"] = "Katteform",
    ["Aquatic Form"] = "Vandform", ["Travel Form"] = "Rejseform", ["Moonkin Form"] = "Månekin-form",
    ["Tree of Life"] = "Livets Træ", ["Tree of Life Form"] = "Livets Træ-form", ["Flight Form"] = "Flyveform",
    ["Swift Flight Form"] = "Hurtig Flyveform", ["Ghost Wolf"] = "Spøgelsesulv", ["Shadowform"] = "Skyggeform",
    ["Battle Stance"] = "Kampstilling", ["Defensive Stance"] = "Forsvarsstilling", ["Berserker Stance"] = "Berserkerstilling",
    ["Stealth"] = "Snigen", ["Metamorphosis"] = "Metamorfose", ["Spirit of Redemption"] = "Forløsningens Ånd",
    ["Devotion Aura"] = "Hengivenhedsaura", ["Retribution Aura"] = "Gengældelsesaura", ["Concentration Aura"] = "Koncentrationsaura",
    ["Crusader Aura"] = "Korsfarer-aura", ["Fire Resistance Aura"] = "Ildmodstandsaura", ["Frost Resistance Aura"] = "Frostmodstandsaura",
    ["Shadow Resistance Aura"] = "Skyggemodstandsaura", ["Sanctity Aura"] = "Hellighedsaura",

    -- dispel types and damage mechanics
    ["Magic"] = "Magi", ["Curse"] = "Forbandelse", ["Disease"] = "Sygdom", ["Poison"] = "Gift", ["Enrage"] = "Raseri-udbrud",
    ["Bleed"] = "Bløde", ["Charm"] = "Forhekse", ["Disarm"] = "Afvæbne", ["Disorient"] = "Desorientere", ["Distract"] = "Distrahere",
    ["Fear"] = "Frygt", ["Fumble"] = "Famle", ["Grip"] = "Greb", ["Root"] = "Rodfæste", ["Pacify"] = "Pacificere",
    ["Silence"] = "Tavshed", ["Sleep"] = "Søvn", ["Snare"] = "Snare", ["Stun"] = "Bedøve", ["Freeze"] = "Fryse",
    ["Knockout"] = "Slå Bevidstløs", ["Bleeding"] = "Bløder", ["Polymorph"] = "Forvandle", ["Banish"] = "Forvise",
    ["Shield"] = "Skjold", ["Shackle"] = "Lænke", ["Turn"] = "Vende", ["Horror"] = "Rædsel", ["Invulnerability"] = "Usårlighed",
    ["Interrupt"] = "Afbryde", ["Daze"] = "Fortumle", ["Discovery"] = "Opdagelse", ["Immune Shield"] = "Immunskjold",
    ["Sapped"] = "Slået Ned", ["Enraged"] = "Rasende", ["Wounded"] = "Såret", ["Infected"] = "Smittet",

    -- totem categories (tools for professions)
    ["Skinning Knife"] = "Flåkniv", ["Earth Totem"] = "Jordtotem", ["Air Totem"] = "Lufttotem", ["Fire Totem"] = "Ildtotem",
    ["Water Totem"] = "Vandtotem", ["Mining Pick"] = "Minehakke", ["Blacksmith Hammer"] = "Smedehammer",
    ["Arclight Spanner"] = "Buelys-skruenøgle", ["Gyromatic Micro-Adjustor"] = "Gyromatisk Mikrojustering",
    ["Runed Copper Rod"] = "Runebesat Kobberstav", ["Runed Silver Rod"] = "Runebesat Sølvstav",
    ["Runed Golden Rod"] = "Runebesat Guldstav", ["Runed Truesilver Rod"] = "Runebesat Ægte-sølvstav",
    ["Runed Arcanite Rod"] = "Runebesat Arkanit-stav", ["Master Totem"] = "Mestertotem",

    -- quest categories (quest log headers that are not zones) and quest types
    ["Class Quests"] = "Klasseopgaver", ["Professions"] = "Håndværk", ["Daily"] = "Daglig", ["Weekly"] = "Ugentlig",
    ["Group"] = "Gruppe", ["Dungeon"] = "Fangekælder", ["Raid"] = "Togt", ["Heroic"] = "Heroisk", ["Elite"] = "Elite",
    ["Life"] = "Liv", ["PvP"] = "PvP", ["Escort"] = "Eskorte", ["Seasonal"] = "Sæson", ["Legendary"] = "Legendarisk",
    ["Epic"] = "Episk", ["Rare"] = "Sjælden", ["Uncommon"] = "Usædvanlig", ["Common"] = "Almindelig", ["Poor"] = "Ringe",
    ["Artifact"] = "Artefakt", ["Heirloom"] = "Arvestykke", ["Miscellaneous"] = "Diverse", ["Other"] = "Andet",
    ["Complete"] = "Færdig", ["Failed"] = "Mislykkedes", ["Available"] = "Tilgængelig", ["Tracked"] = "Fulgt",

    -- achievement categories
    ["Achievements"] = "Bedrifter", ["Summary"] = "Oversigt", ["General"] = "Generelt", ["Quests"] = "Opgaver",
    ["Exploration"] = "Udforskning", ["Player vs. Player"] = "Spiller mod Spiller", ["Dungeons & Raids"] = "Fangekældre & Togter",
    ["Reputation"] = "Omdømme", ["World Events"] = "Verdensbegivenheder", ["Feats of Strength"] = "Styrkeprøver",
    ["Legacy"] = "Arv", ["Eastern Kingdoms"] = "Østlige Kongeriger", ["Kalimdor"] = "Kalimdor", ["Outland"] = "Outland",
    ["Northrend"] = "Nordland", ["Pandaria"] = "Pandaria", ["Draenor"] = "Draenor", ["Broken Isles"] = "De Knuste Øer",
    ["Kul Tiras"] = "Kul Tiras", ["Zandalar"] = "Zandalar", ["Shadowlands"] = "Skyggelandene", ["Dragon Isles"] = "Drageøerne",
    ["Battlegrounds"] = "Slagmarker", ["Arena"] = "Arena", ["Rated Battleground"] = "Rangeret Slagmark", ["Honor"] = "Ære",
    ["Collections"] = "Samlinger", ["Mounts"] = "Ridedyr", ["Pets"] = "Kæledyr", ["Toys"] = "Legetøj", ["Appearances"] = "Udseender",
    ["Combat"] = "Kamp", ["Death"] = "Død", ["Gold"] = "Guld", ["Consumables"] = "Forbrugsvarer",
    ["Secondary Skills"] = "Sekundære Færdigheder", ["Primary Professions"] = "Primære Håndværk",
    ["Secondary Professions"] = "Sekundære Håndværk", ["Class Skills"] = "Klassefærdigheder", ["Weapon Skills"] = "Våbenfærdigheder",
    ["Armor Proficiencies"] = "Rustningsfærdigheder", ["Languages"] = "Sprog", ["Riding"] = "Ridning", ["Gathering"] = "Indsamling",
    ["Crafting"] = "Håndværk", ["Production"] = "Fremstilling", ["Specializations"] = "Specialiseringer",

    -- classes (female forms and plurals are not needed in Danish) and the rest of the races
    ["Mage"] = "Magiker", ["Priest"] = "Præst", ["Shaman"] = "Shaman", ["Warlock"] = "Heksemester",
    ["Death Knight"] = "Dødsridder", ["Monk"] = "Munk", ["Demon Hunter"] = "Dæmonjæger", ["Evoker"] = "Fremkalder",
    ["Blood Elf"] = "Blodalf", ["Draenei"] = "Draenei", ["Goblin"] = "Goblin", ["Worgen"] = "Worgen", ["Pandaren"] = "Pandaren",
    ["Void Elf"] = "Tomrumsalf", ["Nightborne"] = "Nattefødt", ["Highmountain Tauren"] = "Højbjerg-tauren",
    ["Lightforged Draenei"] = "Lysformet Draenei", ["Dark Iron Dwarf"] = "Mørkjern-dværg", ["Mag'har Orc"] = "Mag'har-ork",
    ["Zandalari Troll"] = "Zandalari-trold", ["Kul Tiran"] = "Kul Tiraner", ["Vulpera"] = "Vulpera", ["Mechagnome"] = "Mekagnom",
    ["Dracthyr"] = "Dracthyr", ["Earthen"] = "Jordbåren", ["Haranir"] = "Haranir",

    -- PvP ranks and honor titles (the plain words; the game adds the player name)
    ["Private"] = "Menig", ["Corporal"] = "Korporal", ["Sergeant"] = "Sergent", ["Master Sergeant"] = "Oversergent",
    ["Sergeant Major"] = "Stabssergent", ["Knight"] = "Ridder", ["Knight-Lieutenant"] = "Ridder-Løjtnant",
    ["Knight-Captain"] = "Ridder-Kaptajn", ["Knight-Champion"] = "Ridder-Mester", ["Lieutenant Commander"] = "Kommandørløjtnant",
    ["Commander"] = "Kommandør", ["Marshal"] = "Marskal", ["Field Marshal"] = "Feltmarskal", ["Grand Marshal"] = "Stormarskal",
    ["Scout"] = "Spejder", ["Grunt"] = "Fodsoldat", ["Stone Guard"] = "Stenvagt", ["Blood Guard"] = "Blodvagt",
    ["Legionnaire"] = "Legionær", ["Centurion"] = "Centurion", ["Champion"] = "Mester", ["Lieutenant General"] = "Generalløjtnant",
    ["General"] = "General", ["Warlord"] = "Krigsherre", ["High Warlord"] = "Højkrigsherre",
    ["Gladiator"] = "Gladiator", ["Duelist"] = "Duellant", ["Rival"] = "Rival", ["Challenger"] = "Udfordrer",
    ["Merciless Gladiator"] = "Skånselsløs Gladiator", ["Vengeful Gladiator"] = "Hævngerrig Gladiator",
    ["Brutal Gladiator"] = "Brutal Gladiator", ["Battlemaster"] = "Kampmester", ["Justicar"] = "Retfærdiggører",
    ["Conqueror"] = "Erobrer", ["Champion of the Naaru"] = "Naaruernes Mester", ["Elder"] = "Ældste",
    ["Hand of A'dal"] = "A'dals Hånd", ["Salty"] = "Salt", ["Chef"] = "Kok", ["Explorer"] = "Opdagelsesrejsende",
    ["Jenkins"] = "Jenkins", ["Bloodsail Admiral"] = "Blodsejl-admiral", ["Ambassador"] = "Ambassadør",
    ["Patron"] = "Mæcen", ["Brewmaster"] = "Ølmester", ["Matron"] = "Madam", ["Seeker"] = "Søger",
    ["Loremaster"] = "Vidensmester", ["Archmage"] = "Ærkemagiker", ["Twilight Vanquisher"] = "Tusmørkets Overvinder",
}
for en, da in pairs(t) do
    if ns.Exact[en] == nil then ns.Exact[en] = da end
end

-- Profession names: the generated tables disagree (Fortryllings / Fortryllingskunst / Fortryllelse ...), so force one name everywhere.
local professions = {
    ["Alchemy"] = "Alkymi", ["Blacksmithing"] = "Smedning", ["Enchanting"] = "Fortryllingskunst",
    ["Engineering"] = "Ingeniørkunst", ["Herbalism"] = "Urtekundskab", ["Leatherworking"] = "Læderarbejde",
    ["Mining"] = "Minedrift", ["Skinning"] = "Flåning", ["Tailoring"] = "Skrædderi", ["Cooking"] = "Madlavning",
    ["First Aid"] = "Førstehjælp", ["Fishing"] = "Fiskeri", ["Lockpicking"] = "Låsepikning",
    ["Jewelcrafting"] = "Juvelsmedekunst", ["Inscription"] = "Indskrift", ["Poisons"] = "Gifte", ["Riding"] = "Ridning",
}
for en, da in pairs(professions) do ns.Exact[en] = da end
