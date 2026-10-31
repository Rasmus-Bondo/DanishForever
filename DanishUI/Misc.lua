local _, ns = ...

-- Small hand-made sets (creature types, currencies). Entries already in ns.Exact are kept.
local misc = {
    -- creature types (the line under an NPC's name)
    ["Beast"] = "Udyr", ["Dragonkin"] = "Drageslægtning", ["Demon"] = "Dæmon", ["Elemental"] = "Elementar",
    ["Giant"] = "Kæmpe", ["Undead"] = "Udøde", ["Humanoid"] = "Humanoid", ["Critter"] = "Skabning",
    ["Mechanical"] = "Mekanisk", ["Not specified"] = "Uspecificeret", ["Totem"] = "Totem",
    ["Non-combat Pet"] = "Kampløst Kæledyr", ["Wild Pet"] = "Vildt Kæledyr",

    -- dungeon and raid difficulties ("10 Player", "40 Player" are handled by a pattern in Patterns.lua)
    ["Normal"] = "Normal", ["Infinite"] = "Uendelig",
    ["Difficulty A"] = "Sværhedsgrad A", ["Difficulty B"] = "Sværhedsgrad B", ["Difficulty C"] = "Sværhedsgrad C",
    ["DNT - Internal only"] = "OVERSÆT-IKKE - Kun intern",

    -- currencies
    ["Darkmoon Prize Ticket"] = "Mørkemåne-præmiebillet",
    ["Honor Points"] = "Ærespoint",
    ["Merchant's Favor"] = "Købmandens Gunst",
    ["Rank Points"] = "Rangpoint",
    ["Tarnished Undermine Real"] = "Plettet Undermine-real",
    ["Renown - PvP Rank"] = "Anseelse - PvP-rang",
    ["Renown - Legacy Rank"] = "Anseelse - Arverang",
    ["[DNT] Class Talent Reset"] = "[OVERSÆT-IKKE] Klassetalent-nulstilling",
    ["[DNT] Legacy Talent Reset"] = "[OVERSÆT-IKKE] Arvetalent-nulstilling",
}
for en, da in pairs(misc) do
    if ns.Exact[en] == nil then ns.Exact[en] = da end
end
