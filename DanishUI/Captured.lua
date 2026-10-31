local _, ns = ...

-- Text captured in game that no other table covered, translated afterwards (build_capture_lua.py).
local exact = {
    ["(Complete)"] = "(Fuldfør)",
    ["(Dungeon)"] = "(Fangehul)",
    ["(PvP)"] = "(PvP)",
    ["(Raid)"] = "(Razzia)",
    ["<Click to Engrave Rune>"] = "<Klik for at gravere rune>",
    ["<The cat yawns and regards you through heavily-lidded eyes.>"] = "<Katten gaber og betragter dig med halvtunge øjne.>",
    ["All Runes"] = "Alle Runer",
    ["Alliance Towers Controlled"] = "Alliancens Tårne Kontrolleret",
    ["Available Channels"] = "Tilgængelige Kanaler",
    ["Blood Guard Pepmeddres"] = "Blodvagt Pepmeddres",
    ["Capture Crown Guard Tower, Eastwall Tower, Northpass Tower and Plaguewood Tower in the Eastern Plaguelands, then return to Emmisary Gormok at Light's Hope Chapel."] = "Erobr Kronvagtens Tårn, Østmur-tårnet, Nordpas-tårnet og Pestskov-tårnet i de Østlige Pestlande, og vend derefter tilbage til Udsending Gormok ved Lysets Håb-kapellet.",
    ["Click this button to clean up your bags.|n|nIt auto-sorts and moves items out of the way to make room for new items."] = "Klik på denne knap for at rydde op i dine tasker.|n|nDen sorterer automatisk og flytter genstande af vejen for at gøre plads til nye genstande.",
    ["Collapse options |A:editmode-up-arrow:16:11:0:3|a"] = "Sammenfold indstillinger |A:editmode-up-arrow:16:11:0:3|a",
    ["Damage:"] = "Skade:",
    ["Defense:"] = "Forsvar:",
    ["Deliver the Call to Arms Announcement to the Keeper of the Rolls at Light's Hope Chapel in the Eastern Plaguelands."] = "Lever Kald til Våben-kundgørelsen til Protokolvogteren ved Lysets Håb-kapellet i de Østlige Pestlande.",
    ["Enter Naxxramas and uncover the Fate of Ramaladni."] = "Skriv Naxxrammas ind og afdæk Ramaladdis Skæbne.",
    ["Filler Text"] = "Fyldtekst",
    ["Greetings, Pepmeddres. I am Duke Nicholas Zverenhoff of the Argent Dawn."] = "Hilsner, Pepmeddres. Jeg er Hertug Nikolaj Dyrehoff fra Sølvdæmringen.",
    ["Hej, druid. Undskyld mig, jeg har en samtale i gang med Rumlat. Han mener, at selv dette land ikke er uden for redning. "] = "Hej, druid. Undskyld mig, jeg har en samtale i gang med Rumlat. Han mener, at selv dette land ikke er uden for redning. ",
    ["Hello, Rayne. What brings the Cenarion Circle to the Plaguelands?"] = "Hej, Regn. Hvad fører Cenarion-kredsen til Pestlandene?",
    ["Hello, druid. Please excuse me as I am having a conversation with Rimblat. He believes that even this land is not beyond saving."] = "Hej, druide. Undskyld mig, jeg fører en samtale med Rumlat. Han mener, at selv dette land ikke er uden for redning.",
    ["Horde Territory"] = "Hordens Territorium",
    ["Horde Towers Controlled"] = "Hordens Tårne Kontrolleret",
    ["I would like to buy from you."] = "Jeg vil gerne købe hos dig.",
    ["I'm far too busy to be playing 'guess the smell' with you, tauren. State your business or get out of my sight!"] = "Jeg er alt for travl til at lege 'gæt lugten' med dig, tyrefolket. Sig, hvad du vil, eller forsvind mig af syne!",
    ["I'm what you call a capitalist, tauren."] = "Jeg er, hvad man kalder en kapitalist, tyrefolket.",
    ["Idol"] = "Idol",
    ["Invasion"] = "Invasion",
    ["Item Name"] = "Genstandsnavn",
    ["Level level race class"] = "Niveau niveau race klasse",
    ["Master craftsman Omarion just vanished one night. Like a toot in the wind... Poof! Gone! Bah, now I'm the only one left to craft the goods for the boys on the front lines. "] = "Mester-håndværker Omarjon forsvandt bare én nat. Som en prut i vinden... Puf! Væk! Bah, nu er jeg den eneste tilbage til at fremstille varerne til drengene på frontlinjen. ",
    ["Pepmeddres"] = "Pepmeddres",
    ["Power:"] = "Kraft:",
    ["PvP"] = "PvP",
    ["Pyntegenstand"] = "Pyntegenstand",
    ["Quest Title"] = "Questtitel",
    ["Rayne, where should I look for savage fronds?"] = "Regn, hvor skal jeg lede efter vilde bregnblade?",
    ["Services"] = "Tjenester",
    ["Show me your wares, Wilhelm."] = "Vis mig dine varer, Vilhelm.",
    ["The Argent Dawn placed the call for aid, and you, among others, have answered. There is no time for us to provide you with training. Our faith is placed in your abilities, and that you will join us in throwing back this Scourge threat."] = "Sølvdæmringen har sendt opfordringen om hjælp, og du er blandt dem, der har svaret. Der er ingen tid til at give dig træning. Vores tro er sat på dine evner, og at du vil slutte dig til os i at slå denne Svøben-trussel tilbage.",
    ["The Scourge have returned in greater numbers than we have seen before. The Argent Dawn is recruiting all willing and capable men and women to defend our lands.\n\nIf we share common cause, take this document to the Keeper of the Rolls at Light's Hope Chapel in the Eastern Plaguelands."] = "Svøben er vendt tilbage i større antal, end vi nogensinde har set. Sølvdæmringen hverver alle villige og dygtige mænd og kvinder til at forsvare vores lande.\n\nHvis vi deler en fælles sag, så tag dette dokument med til Protokolvogteren ved Lysets Håb-kapellet i Østlige Pestlande.",
    ["Vapenkjortel"] = "Våbenkjortel",
    ["Venture to Alterac Valley, located in the Alterac Mountains. Find and speak with Warmaster Laggrond - who stands outside the tunnel entrance - to begin your career as a soldier of Frostwolf. You will find Alterac Valley north of Tarren Mill at the base of the Alterac Mountains."] = "Begiv dig til Alterac-dalen, beliggende i Alterac-bjergene. Find og tal med Krigsmester Laggrønd - som står uden for tunnelindgangen - for at begynde din karriere som soldat i Frostulv. Du finder Alterac-dalen nord for Tarrenmølle ved foden af Alterac-bjergene.",
    ["Very well - your deeds have been entered into the records, and you are duly recognized for your efforts.  Keep up the good work, druid.\n\nIf you have any more signets to hand in, then I am able to assist you further in that regard."] = "Meget godt - dine bedrifter er blevet indført i protokollen, og du er behørigt anerkendt for din indsats.  Bliv ved med det gode arbejde, druide.\n\nHvis du har flere seglringe at aflevere, kan jeg hjælpe dig yderligere i den sag.",
    ["You earned this, scrub. Now, don't cry about your orders. Fill 'em or destroy 'em.\r\n"] = "Du fortjente det her, din lille nisse. Nu skal du ikke hyle over dine ordrer. Fyld dem ud eller ødelæg dem.\r\n",
    ["You know the drill, kid. One valor token gets you a craftsman's writ."] = "Du kender proceduren, unge. Ét modmærke giver dig Håndværkerens Brev.",
    ["You've come to join our order, have you not?"] = "Du er kommet for at slutte dig til vores orden, ikke sandt?",
    ["startrink"] = "stjernedrik",
}
local list = {
    {"^Engrave your belt with the Nourish rune%:\r\n\r\n%|T236162%:24%|t\r\nHeals a friendly target for ([%d%.,]+) to ([%d%.,]+)%. Heals for an additional ([%d%.,]+)%% if you have a Rejuvenation%, Regrowth%, Lifebloom%, or Wild Growth effect active on the target%. This spell benefits from and triggers all effects associated with Healing Touch or Regrowth%.$", "Gravér dit bælte med Nærende-runen:\r\n\r\n|T236162:24|t\r\nHeler et venligt mål for {1} til {2}. Heler for yderligere {3}%, hvis du har en Foryngelse-, Genvækst-, Livsblomst- eller Vild Vækst-effekt aktiv på målet. Denne besværgelse drager fordel af og udløser alle effekter knyttet til Helbredende Berøring eller Genvækst.", "% if you have a Rejuvenation, Regrowth, Lifebloom, or Wild Growth effect active on the target. This spell benefits from and triggers all effects associated with Healing Touch or Regrowth."},
    {"^Engrave your chest or robe with the Wild Strikes rune%:\r\n\r\n%|T132143%:24%|t\r\nWhile you are in Cat Form%, Bear Form%, or Dire Bear Form%, party or raid members within ([%d%.,]+) yards gain increased combat ferocity%.  Each melee hit has a ([%d%.,]+)%% chance of granting the attacker an extra attack with ([%d%.,]+)%% additional Attack Power%. No effect if the target is already benefitting from Windfury Totem%.\r\n$", "Gravér dit bryst eller din kåbe med Vilde Stødder-runen:\r\n\r\n|T132143:24|t\r\nMens du er i Katteform, Bjørneform eller Frygtindgydende Bjørneform, får gruppe- eller razzia-medlemmer inden for {1} meter øget kampvildskab.  Hvert nærkamp-angreb har en {2}% sjans for at give angriberen et ekstra angreb med {3}% ekstra Angrebskraft. Ingen effekt, hvis målet allerede drager fordel af Vindraseri-totem.\r\n", "Engrave your chest or robe with the Wild Strikes rune:\r\n\r\n|T132143:24|t\r\nWhile you are in Cat Form, Bear Form, or Dire Bear Form, party or raid members within "},
    {"^Craftsman Wilhelm at Light%'s Hope Chapel in the Eastern Plaguelands wants you to bring him ([%d%.,]+) Frozen Runes%, ([%d%.,]+) Essence of Water%, ([%d%.,]+) Blue Sapphires and ([%d%.,]+) gold pieces%.$", "Håndværker Vilhelm ved Lysets Håb-kapellet i de Østlige Pestlande vil have dig til at bringe ham {1} Frosne Runer, {2} Vandets Essens, {3} Blå Safirer og {4} guldstykker.", "Craftsman Wilhelm at Light's Hope Chapel in the Eastern Plaguelands wants you to bring him "},
    {"^Smokey LaRue wants you to get ([%d%.,]+) Thorium Bars%, ([%d%.,]+) Golden Rod%, ([%d%.,]+) Hi%-Explosive Bombs%, and ([%d%.,]+) Unstable Triggers%.\n\nYou will have to find a blacksmith and an engineer for these items%.$", "Smøg LaRue vil have dig til at skaffe {1} Thoriumstænger, {2} Gylden Stang, {3} Højeksplosive Bomber og {4} Ustabile Udløsere.\n\nDu bliver nødt til at finde en smed og en ingeniør til disse ting.", " Unstable Triggers.\n\nYou will have to find a blacksmith and an engineer for these items."},
    {"^Rayne at Light%'s Hope Chapel in the Eastern Plaguelands wants ([%d%.,]+) Savage Fronds%.$", "Regn ved Lysets Håb-kapellet i de Østlige Pestlande vil have {1} Vilde Bregnblade.", "Rayne at Light's Hope Chapel in the Eastern Plaguelands wants "},
    {"^Points spent in Balance Talents%: %|cffffffff([%d%.,]+)%|r$", "Point brugt i Balance-begavelser: |cffffffff{1}|r", "Points spent in Balance Talents: |cffffffff"},
    {"^Talent Points%: %|cffffffff([%d%.,]+)%|r$", "Talentpoint: |cffffffff{1}|r", "Talent Points: |cffffffff"},
    {"^Towers Controlled%: ([%d%.,]+)$", "Kontrollerede tårne: {1}", "Towers Controlled: "},
    {"^Arcane Resistance ([%d%.,]+)$", "Arkanmodstand {1}", "Arcane Resistance "},
    {"^Nature Resistance ([%d%.,]+)$", "Naturmodstand {1}", "Nature Resistance "},
    {"^Quests%: %|cffffffff([%d%.,]+)%/([%d%.,]+)%|r$", "Quests: |cffffffff{1}/{2}|r", "Quests: |cffffffff"},
    {"^Shadow Resistance ([%d%.,]+)$", "Skyggemodstand {1}", "Shadow Resistance "},
    {"^Frost Resistance ([%d%.,]+)$", "Frostmodstand {1}", "Frost Resistance "},
    {"^Fire Resistance ([%d%.,]+)$", "Ildmodstand {1}", "Fire Resistance "},
    {"^Arcane Damage %+([%d%.,]+)$", "Arkanskade +{1}", "Arcane Damage +"},
    {"^Level ([%d%.,]+) Tauren Druid$", "Niveau {1} Taurer Druide", " Tauren Druid"},
    {"^%+([%d%.,]+) Spell Power$", "+{1} Besværgelseskraft", " Spell Power"},
    {"^Latency%: ([%d%.,]+)ms$", "Svartid: {1}ms", "Latency: "},
    {"^([%d%.,]+) Silver\n([%d%.,]+) Silver$", "{1} Sølv\n{2} Sølv", " Silver\n"},
    {"^%(Rang ([%d%.,]+)%)$", "(Rang {1})", "(Rang "},
    {"^%(Rank ([%d%.,]+)%)$", "(Rang {1})", "(Rank "},
    {"^([%d%.,]+) Mana$", "{1} Mana", " Mana"},
    {"^Mana ([%d%.,]+) %/ ([%d%.,]+)$", "Mana {1} / {2}", "Mana "},
    {"^Page ([%d%.,]+)$", "Side {1}", "Page "},
}

local cache, cached = {}, 0

function ns.translateCaptured(text)
    local v = exact[text]
    if v then return v end
    local hit = cache[text]
    if hit ~= nil then return hit or nil end
    local result = false
    for i = 1, #list do
        local p = list[i]
        if text:find(p[3], 1, true) then
            local caps = { text:match(p[1]) }
            if caps[1] then
                result = (p[2]:gsub("{(%d+)}", function(k) return caps[tonumber(k)] or "" end))
                break
            end
        end
    end
    cached = cached + 1
    if cached > 3000 then cache, cached = {}, 1 end
    cache[text] = result
    return result or nil
end
