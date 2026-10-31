local _, ns = ...

-- Books, letters and signs. The reading window fills its text without SetText on a label, so it is replaced
-- here when the game says the text is ready. Lookup is by the English text with all whitespace removed.

local function translatePage()
    local getText = ItemTextGetText
    local page = ItemTextPageText
    if not (getText and page and page.SetText) then return end
    local en = getText()
    if type(en) ~= "string" or en == "" or (issecretvalue and issecretvalue(en)) then return end
    local da = ns.Books and ns.Books[(en:gsub("%s+", ""))]
    if not da then return end
    if ns.expandDanish then
        local ok, out = pcall(ns.expandDanish, da)
        if ok then da = out end
    end
    page:SetText(da)
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("ITEM_TEXT_READY")
frame:SetScript("OnEvent", function()
    C_Timer.After(0, translatePage)
    C_Timer.After(0.15, translatePage)
end)
