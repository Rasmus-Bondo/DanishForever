local addonName, ns = ...

-- 1. Always on: every GlobalString whose English text has no placeholders becomes a fixed-word entry, so
--    the SetText hook can swap it wherever it is drawn. The English value is read from the client itself.
-- 2. Opt-in (/df globals on, then /reload): replace the game's own string variables with the Danish text.
--    This translates texts that are built with format codes (%s, %d). The risk is taint: other addons or
--    Blizzard code that read the changed variables can get "action blocked" errors, so test out of combat.

function ns.ApplyGlobals()
    local n = 0
    for tag, da in pairs(ns.GlobalStrings or {}) do
        if type(_G[tag]) == "string" then
            _G[tag] = da
            n = n + 1
        end
    end
    return n
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:SetScript("OnEvent", function(self, _, name)
    if name ~= addonName then return end
    self:UnregisterEvent("ADDON_LOADED")
    DanishForeverDB = DanishForeverDB or {}

    local exact = ns.Exact
    for tag, da in pairs(ns.GlobalStrings or {}) do
        local en = _G[tag]
        if type(en) == "string" and en ~= "" and exact[en] == nil
           and not en:find("%", 1, true) and not en:find("|", 1, true) then
            exact[en] = da
        end
    end

    if DanishForeverDB.globals then
        ns.ApplyGlobals()
    end
end)
