local _, ns = ...

-- Fixed words and phrases, matched on the whole string
ns.Exact = {
    -- binding and item state
    ["Binds when picked up"] = "Bindes ved opsamling",
    ["Binds when equipped"] = "Bindes ved udrustning",
    ["Binds when used"] = "Bindes ved brug",
    ["Binds to account"] = "Bindes til konto",
    ["Soulbound"] = "Sjælebundet",
    ["Quest Item"] = "Opgavegenstand",
    ["Unique"] = "Unik",
    ["Unique-Equipped"] = "Unik-Udrustet",
    ["Conjured Item"] = "Fremtryllet genstand",
    ["This Item Begins a Quest"] = "Denne genstand starter en opgave",
    ["<Right Click to Open>"] = "<Højreklik for at åbne>",
    ["<Right Click to Read>"] = "<Højreklik for at læse>",
    ["Sell Price:"] = "Salgspris:",
    ["Use:"] = "Brug:",
    ["Equip:"] = "Udstyr:",

    -- equipment slots
    ["Head"] = "Hoved", ["Neck"] = "Hals", ["Shoulder"] = "Skulder", ["Back"] = "Ryg",
    ["Chest"] = "Bryst", ["Shirt"] = "Skjorte", ["Tabard"] = "Vapenkjortel", ["Wrist"] = "Håndled",
    ["Hands"] = "Hænder", ["Waist"] = "Talje", ["Legs"] = "Ben", ["Feet"] = "Fødder",
    ["Finger"] = "Finger", ["Trinket"] = "Pyntegenstand", ["Main Hand"] = "Hovedhånd",
    ["Off Hand"] = "Bihånd", ["One-Hand"] = "Enhånds", ["Two-Hand"] = "Tohånds",
    ["Held In Off-hand"] = "Holdt i bihånd", ["Ranged"] = "Afstand", ["Thrown"] = "Kastevåben",
    ["Relic"] = "Relikvie", ["Ammo"] = "Ammunition", ["Projectile"] = "Projektil",

    -- armor and weapon types
    ["Cloth"] = "Stof", ["Leather"] = "Læder", ["Mail"] = "Ringbrynje", ["Plate"] = "Plade",
    ["Shield"] = "Skjold", ["Sword"] = "Sværd", ["Axe"] = "Økse", ["Mace"] = "Kølle",
    ["Dagger"] = "Dolk", ["Staff"] = "Stav", ["Polearm"] = "Stangvåben", ["Fist Weapon"] = "Knytnævevåben",
    ["Bow"] = "Bue", ["Crossbow"] = "Armbrøst", ["Gun"] = "Skydevåben", ["Wand"] = "Tryllestav",
    ["Fishing Pole"] = "Fiskestang", ["Miscellaneous"] = "Diverse",

    -- item classes
    ["Consumable"] = "Forbrugsvare", ["Container"] = "Beholder", ["Quest"] = "Opgave",
    ["Trade Goods"] = "Handelsvarer", ["Reagent"] = "Reagens", ["Recipe"] = "Opskrift",
    ["Key"] = "Nøgle", ["Junk"] = "Skrammel", ["Quiver"] = "Kogger", ["Bag"] = "Taske",

    -- schools
    ["Fire"] = "Ild", ["Frost"] = "Frost", ["Nature"] = "Natur", ["Shadow"] = "Skygge",
    ["Arcane"] = "Arkan", ["Holy"] = "Hellig", ["Physical"] = "Fysisk",

    -- professions and skills
    ["Alchemy"] = "Alkymi", ["Blacksmithing"] = "Smedning", ["Enchanting"] = "Fortryllelse",
    ["Engineering"] = "Ingeniørkunst", ["Herbalism"] = "Urtekundskab", ["Leatherworking"] = "Læderarbejde",
    ["Mining"] = "Minedrift", ["Skinning"] = "Flåning", ["Tailoring"] = "Skrædderi",
    ["Cooking"] = "Madlavning", ["First Aid"] = "Førstehjælp", ["Fishing"] = "Fiskeri",
    ["Lockpicking"] = "Dirkning", ["Riding"] = "Ridning",

    -- classes and races
    ["Warrior"] = "Kriger", ["Paladin"] = "Paladin", ["Hunter"] = "Jæger", ["Rogue"] = "Slyngel",
    ["Priest"] = "Præst", ["Shaman"] = "Shaman", ["Mage"] = "Magiker", ["Warlock"] = "Heksemester",
    ["Druid"] = "Druide", ["Human"] = "Menneske", ["Dwarf"] = "Dværg", ["Night Elf"] = "Natalf",
    ["Gnome"] = "Gnom", ["Orc"] = "Ork", ["Undead"] = "Udøde", ["Tauren"] = "Tauren", ["Troll"] = "Trold",

    -- languages
    ["Orcish"] = "Orkisk", ["Darnassian"] = "Darnassisk", ["Taurahe"] = "Tauraisk",
    ["Dwarvish"] = "Dværgisk", ["Common"] = "Fællessprog", ["Demonic"] = "Dæmonisk",
    ["Titan"] = "Titansk", ["Thalassian"] = "Thalassisk", ["Draconic"] = "Drakonisk",
    ["Kalimag"] = "Kalimagisk", ["Gnomish"] = "Gnomisk", ["Gutterspeak"] = "Rendestenssnak",
    ["Zombie"] = "Zombiesnak", ["Pandaren"] = "Pandarensk", ["Shen'dorei"] = "Shen'doreisk",

    -- item name descriptions (the extra line under an item name)
    ["Red"] = "Rød", ["Blue"] = "Blå", ["Green"] = "Grøn", ["White"] = "Hvid", ["Grey"] = "Grå",
    ["Molten"] = "Smeltende", ["Core Forged"] = "Kernesmedet", ["Bloodied"] = "Blodige",
    ["Shadowflame"] = "Skyggeflamme", ["Timeworn"] = "Tidsslidt", ["Void-Touched"] = "Tomrumsberørt",
    ["Sanctified"] = "Helliget", ["Soulfrost"] = "Sjælefrost", ["Season of Discovery"] = "Opdagelsens Sæson",
    ["Scarlet Uniform"] = "Skarlagenrød Uniform", ["Charm"] = "Amulet",
    ["Vessel of Transmutation"] = "Transmutationsbeholder", ["PTR Only"] = "Kun PTR", ["Test"] = "Test",
    ["Max Rank"] = "Maks. rang", ["Apprentice"] = "Lærling", ["Journeyman"] = "Svend", ["Expert"] = "Ekspert",
    ["Artisan"] = "Håndværker", ["Scarce"] = "Sjælden", ["Crafted"] = "Håndlavet",

    -- talent trees (Fire, Frost, Arcane, Holy and Shadow are in the schools above)
    ["Arms"] = "Arme", ["Protection"] = "Beskyttelse", ["Fury"] = "Vrede", ["Combat"] = "Kamp",
    ["Assassination"] = "Snigmord", ["Subtlety"] = "Snedighed", ["Discipline"] = "Disciplin",
    ["Elemental"] = "Elementar", ["Restoration"] = "Genoprettelse", ["Enhancement"] = "Forstærkning",
    ["Feral Combat"] = "Vildkamp", ["Balance"] = "Balance", ["Destruction"] = "Ødelæggelse",
    ["Affliction"] = "Plage", ["Demonology"] = "Dæmonologi", ["Beast Mastery"] = "Dyrebeherskelse",
    ["Survival"] = "Overlevelse", ["Marksmanship"] = "Skarpskydning", ["Retribution"] = "Gengældelse",

    -- holidays and world events
    ["Fireworks Spectacular"] = "Fyrværkerispektakel",
    ["Feast of Winter Veil"] = "Vinterslørets Festmåltid",
    ["Noblegarden"] = "Adelshaven",
    ["Children's Week"] = "Børnenes Uge",
    ["Darkmoon Faire"] = "Mørkemånens Marked",
    ["Call to Arms: Alterac Valley"] = "Kald til Våben: Alterac-dalen",
    ["Call to Arms: Warsong Gulch"] = "Kald til Våben: Krigssang-Gulch",
    ["Call to Arms: Arathi Basin"] = "Kald til Våben: Arathi-bækkenet",
    ["Call to Arms: Darkspear Islands"] = "Kald til Våben: Mørkspyd-øerne",
    ["Stranglethorn Fishing Extravaganza"] = "Kvælerdorn Fiskeri-Ekstravaganza",
    ["Harvest Festival"] = "Høstfestival",
    ["Hallow's End"] = "Helligaftens Ende",
    ["Lunar Festival"] = "Månefestival",
    ["Love is in the Air"] = "Kærlighed er i Luften",
    ["Midsummer Fire Festival"] = "Sankthans-ildfestival",
}

-- Phrases with numbers or words in them: %d = number, %s = text, %f = decimal number.
-- The Danish text uses the same placeholders in the order they should be filled in.
local patterns = {}                                  -- patterns[first character] = list
local DIGITS = { "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" }

local function add(en, da)
    local pat = en:gsub("[%^%$%(%)%%%.%[%]%*%+%-%?]", "%%%0")
    pat = pat:gsub("%%%%d", "(%%d+)")
    pat = pat:gsub("%%%%s", "(.+)")
    pat = pat:gsub("%%%%f", "([%%d%%.]+)")
    local entry = { pat = "^" .. pat .. "$", fmt = (da:gsub("%%[dsf]", "%%s")), n = #en }
    local first = en:sub(1, 1)
    local keys = { first }
    if en:sub(1, 2) == "%d" then keys = DIGITS end
    for _, k in ipairs(keys) do
        patterns[k] = patterns[k] or {}
        table.insert(patterns[k], entry)
    end
end

add("Item Level %d", "Genstandsniveau %d")
add("Requires Level %d", "Kræver niveau %d")
add("Requires %s (%d)", "Kræver %s (%d)")
add("Requires %s", "Kræver %s")
add("Unique (%d)", "Unik (%d)")
add("Classes: %s", "Klasser: %s")
add("Races: %s", "Racer: %s")
add("%d Player", "%d Spillere")           -- raid sizes: "10 Player", "20 Player", "40 Player"
add("Set: %s", "Sæt: %s")
add("Use: %s", "Brug: %s")
add("Equip: %s", "Udstyr: %s")
add("Chance on hit: %s", "Chance ved træf: %s")
add("Duration: %s", "Varighed: %s")
add("Cooldown remaining: %s", "Nedkøling tilbage: %s")
add("Durability %d / %d", "Holdbarhed %d / %d")
add("%d Charges", "%d Opladninger")
add("%d Slot %s", "%d Pladser %s")
add("<%s>", "<%s>")                       -- NPC titles under a name: "<Innkeeper>"
add("Rank %d", "Rang %d")
add("Raid Unique (%d)", "Raid-Unik (%d)")
add("%d Armor", "%d Rustning")
add("%d Block", "%d Blok")
add("%d - %d Damage", "%d - %d Skade")
add("%d - %d %s Damage", "%d - %d %s Skade")
add("+%d - %d %s Damage", "+%d - %d %s Skade")
add("(%f damage per second)", "(%f skade pr. sekund)")
add("Speed %f", "Hastighed %f")

local stats = {
    Strength = "Styrke", Agility = "Smidighed", Stamina = "Udholdenhed", Intellect = "Intelligens",
    Spirit = "Ånd", Armor = "Rustning",
    ["Arcane Resistance"] = "Arkanmodstand", ["Fire Resistance"] = "Ildmodstand",
    ["Frost Resistance"] = "Frostmodstand", ["Nature Resistance"] = "Naturmodstand",
    ["Shadow Resistance"] = "Skyggemodstand", ["Holy Resistance"] = "Helligmodstand",
}
for en, da in pairs(stats) do
    add("+%d " .. en, "+%d " .. da)
    add("-%d " .. en, "-%d " .. da)
end

for _, list in pairs(patterns) do
    table.sort(list, function(a, b) return a.n > b.n end)   -- most specific first
end

-- translate each comma-separated part ("Warrior, Rogue") when the whole text has no translation
local function translateCapture(c, tr)
    local v = tr(c)
    if v ~= c or not c:find(",", 1, true) then return v end
    local out, changed = {}, false
    for part in c:gmatch("[^,]+") do
        local t = part:gsub("^%s+", "")
        local x = tr(t)
        if x ~= t then changed = true end
        out[#out + 1] = x
    end
    return changed and table.concat(out, ", ") or c
end

-- Random-suffix item names: the game builds "<base name> of the Whale" itself.
ns.ItemSuffix = {
    ["of Intellect"] = "af Intelligens", ["of Spirit"] = "af Ånd", ["of Stamina"] = "af Udholdenhed",
    ["of Agility"] = "af Smidighed", ["of Strength"] = "af Styrke", ["of Power"] = "af Kraft",
    ["of Magic"] = "af Magi", ["of Healing"] = "af Helbredelse", ["of Defense"] = "af Forsvar",
    ["of Regeneration"] = "af Regeneration", ["of Concentration"] = "af Koncentration",
    ["of Eluding"] = "af Undvigelse",
    ["of the Owl"] = "af Uglen", ["of the Eagle"] = "af Ørnen", ["of the Whale"] = "af Hvalen",
    ["of the Bear"] = "af Bjørnen", ["of the Gorilla"] = "af Gorillaen", ["of the Falcon"] = "af Falken",
    ["of the Boar"] = "af Vildsvinet", ["of the Wolf"] = "af Ulven", ["of the Tiger"] = "af Tigeren",
    ["of the Monkey"] = "af Aben",
    ["of Arcane Protection"] = "af Arkanbeskyttelse", ["of Fire Protection"] = "af Ildbeskyttelse",
    ["of Frost Protection"] = "af Frostbeskyttelse", ["of Nature Protection"] = "af Naturbeskyttelse",
    ["of Shadow Protection"] = "af Skyggebeskyttelse",
    ["of the Sorcerer"] = "af Troldmanden", ["of the Elder"] = "af den Ældre",
    ["of the Channeler"] = "af Kanalisatoren", ["of the Physician"] = "af Lægen",
    ["of the Hierophant"] = "af Hierofanten", ["of the Bandit"] = "af Banditten",
    ["of the Beast"] = "af Udyret", ["of the Champion"] = "af Mesteren",
    ["of the Defender"] = "af Forsvareren", ["of the Knight"] = "af Ridderen",
    ["of the Prophet"] = "af Profeten",
    ["of Arcane Wrath"] = "af Arkan Vrede", ["of Fiery Wrath"] = "af Brændende Vrede",
    ["of Frozen Wrath"] = "af Frossen Vrede", ["of Holy Wrath"] = "af Hellig Vrede",
    ["of Nature's Wrath"] = "af Naturens Vrede", ["of Shadow Wrath"] = "af Skyggens Vrede",
    ["of Arcane Resistance"] = "af Arkanmodstand", ["of Fire Resistance"] = "af Ildmodstand",
    ["of Frost Resistance"] = "af Frostmodstand", ["of Nature Resistance"] = "af Naturmodstand",
    ["of Shadow Resistance"] = "af Skyggemodstand",
}

-- "Bent Staff of the Whale": translate the base name, then add the Danish suffix
function ns.translateSuffix(text)
    if #text > 100 or not text:find(" of ", 1, true) then return nil end
    for en, da in pairs(ns.ItemSuffix) do
        local n = #en
        if #text > n + 1 and text:sub(-n) == en and text:sub(-n - 1, -n - 1) == " " then
            local base = ns.ItemNames and ns.ItemNames[text:sub(1, -n - 2)]
            if base then return base .. " " .. da end
        end
    end
    return nil
end

local cache, cached, depth = {}, 0, 0

-- returns the Danish text, or nil when no pattern fits
function ns.translatePattern(text, tr)
    if #text > 200 then return nil end
    local hit = cache[text]
    if hit ~= nil then return hit or nil end              -- false = known miss
    local result = false
    local list = patterns[text:sub(1, 1)]
    if list and depth < 2 then
        for i = 1, #list do
            local p = list[i]
            local caps = { text:match(p.pat) }
            if caps[1] then
                depth = depth + 1
                for k, c in ipairs(caps) do
                    if not c:match("^[%d%.]+$") then caps[k] = translateCapture(c, tr) end
                end
                depth = depth - 1
                result = p.fmt:format(unpack(caps))
                break
            end
        end
    end
    cached = cached + 1
    if cached > 4000 then cache, cached = {}, 1 end
    cache[text] = result
    return result or nil
end
