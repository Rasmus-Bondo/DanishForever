local _, ns = ...

-- The auction house searches by the ENGLISH item name on the server, but every item is shown in Danish. When the text typed
-- in the AH search box is exactly a Danish item name, it is swapped for the English name so the search finds it.

local reverse                                           -- lower-case Danish name -> English name (built on first use)

local function lowerDa(s)
    s = s:lower()
    s = s:gsub("Æ", "æ"):gsub("Ø", "ø"):gsub("Å", "å")
    return s
end

local function build()
    reverse = {}
    for en, da in pairs(ns.ItemNames or {}) do
        if type(en) == "string" and type(da) == "string" then
            local k = lowerDa(da)
            if reverse[k] == nil then reverse[k] = en end
        end
    end
end

local function toEnglish(text)
    if type(text) ~= "string" or text == "" then return nil end
    if issecretvalue and issecretvalue(text) then return nil end
    if not reverse then build() end
    local en = reverse[lowerDa((text:gsub("^%s+", ""):gsub("%s+$", "")))]
    if en and en ~= text then return en end
end

ns.danishToEnglishItem = toEnglish

local hooked = {}
local function hookBox(box)
    if not box or hooked[box] or not box.HookScript then return end
    hooked[box] = true
    box:HookScript("OnTextChanged", function(self, userInput)
        if not userInput then return end
        local ok, en = pcall(toEnglish, self:GetText())
        if ok and en then self:SetText(en) end
    end)
end

local function tryHook()
    pcall(function()
        local bar = AuctionHouseFrame and AuctionHouseFrame.SearchBar          -- Forever
        hookBox(bar and bar.SearchBox)
        hookBox(BrowseName)                                                    -- Classic Era
    end)
end

local f = CreateFrame("Frame")
f:RegisterEvent("ADDON_LOADED")
f:RegisterEvent("AUCTION_HOUSE_SHOW")
f:SetScript("OnEvent", function()
    tryHook()
    if C_Timer and C_Timer.After then C_Timer.After(0, tryHook) end
end)
tryHook()
