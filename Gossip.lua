local _, ns = ...

-- NPC gossip windows, quest greetings and NPC chat lines. The Danish text is found by hashing the English text
-- (player name, race, class and line breaks removed) with the scheme from PolishForever (MIT, hash kept
-- byte-for-byte so the keys match). See CREDITS.txt.

local NBSP = "\194\160"      -- marks text we already replaced

local function hash(text)
    local ok, result = pcall(function()
        if not text or #text == 0 then return 0 end
        local counter, len = 1, #text
        for i = 1, len, 3 do
            counter = math.fmod(counter * 8161, 4294967279)
            counter = counter + string.byte(text, i) * 16776193
            counter = counter + (string.byte(text, i + 1) or (len - i + 256)) * 8372226
            counter = counter + (string.byte(text, i + 2) or (len - i + 256)) * 3932164
        end
        return math.fmod(counter, 4294967291)
    end)
    return ok and result or 0
end

local function escape(s)
    return (s:gsub("(%W)", "%%%1"))
end

local function stripWord(text, word)
    if not word or word == "" then return text end
    for _, variant in ipairs({ word, word:lower(), word:upper() }) do
        text = text:gsub("%f[%w]" .. escape(variant) .. "%f[%W]", "")
    end
    return text
end

local function clean(text)
    text = text:gsub("[\r\n]", "")
    local name = UnitName("player")
    if name and name ~= "" then
        text = text:gsub(escape(name), "")
        text = text:gsub(escape(name:upper()), "")
    end
    text = stripWord(text, UnitRace("player"))
    text = stripWord(text, UnitClass("player"))
    text = text:gsub("%$[BbNnRrCc]%$?", "")
    return text
end

local function isFemale(unit)
    local ok, result = pcall(function()
        local sex = UnitSex(unit)
        if issecretvalue and issecretvalue(sex) then return false end
        return sex == 3
    end)
    return ok and result or false
end

-- Fill in the player-dependent codes the Danish text still carries: $n $r $c $b $g a:b;
local function expand(msg)
    local female = isFemale("player")
    local name  = UnitName("player") or ""
    local race  = UnitRace("player") or ""
    local class = UnitClass("player") or ""
    class = (ns.classDa and ns.classDa[class]) or class
    msg = msg:gsub("%$[gG]%s*([^:;$]-)%s*:%s*([^;$]-)%s*;", function(m, f) return female and f or m end)
    msg = msg:gsub("%$[bB]", "\n")
    msg = msg:gsub("%$[nN]", function() return name end)
    msg = msg:gsub("%$[rR]", function() return race:lower() end)
    msg = msg:gsub("%$[cC]", function() return class:lower() end)
    return msg
end

ns.expandDanish = expand

-- Every way of removing some (not necessarily all) occurrences of word from text. clean() strips ALL of them, which
-- is wrong when the word is also genuine text: "I'm a mage trainer, and you're a mage." for a mage (only the last
-- one was a $c in the original). Capped so a long text cannot explode.
local function subsets(text, word)
    if not word or word == "" then return { text } end
    local spans = {}
    for _, variant in ipairs({ word, word:lower(), word:upper() }) do
        local from = 1
        while true do
            local s, e = text:find(variant, from, true)
            if not s then break end
            local before, after = text:sub(s - 1, s - 1), text:sub(e + 1, e + 1)
            if not before:find("%w") and not after:find("%w") then spans[#spans + 1] = { s, e } end
            from = e + 1
        end
    end
    table.sort(spans, function(a, b) return a[1] < b[1] end)
    local n = #spans
    if n == 0 then return { text } end
    if n > 4 then n = 4 end
    local out = {}
    for mask = 0, 2 ^ n - 1 do
        local parts, pos = {}, 1
        for i = 1, n do
            parts[#parts + 1] = text:sub(pos, spans[i][1] - 1)
            if math.floor(mask / 2 ^ (i - 1)) % 2 == 0 then   -- bit clear: this occurrence was a $c/$r, remove it
                -- removed
            else
                parts[#parts + 1] = text:sub(spans[i][1], spans[i][2])
            end
            pos = spans[i][2] + 1
        end
        parts[#parts + 1] = text:sub(pos)
        out[#out + 1] = table.concat(parts)
    end
    return out
end

local function fallbackLookup(english, data)
    local text = english:gsub("[\r\n]", "")
    local name = UnitName("player")
    if name and name ~= "" then
        text = text:gsub(escape(name), "")
        text = text:gsub(escape(name:upper()), "")
    end
    text = text:gsub("%$[BbNnRrCc]%$?", "")
    for _, a in ipairs(subsets(text, UnitClass("player"))) do
        for _, b in ipairs(subsets(a, UnitRace("player"))) do
            local da = data[hash(b)]
            if da then return da end
        end
    end
end

local missCache, missCount = {}, 0

local function lookup(english)
    local ok, result = pcall(function()
        if type(english) ~= "string" or english == "" or english:sub(-2) == NBSP then return end
        if issecretvalue and issecretvalue(english) then return end
        local data = ns.Gossip
        if not data then return end
        local c = clean(english)
        local da = data[hash(c)]
        if not da then
            local trimmed = c:gsub(" %(low level%)", "")
            if trimmed ~= c then da = data[hash(trimmed)] end
        end
        if not da and not missCache[english] then
            da = fallbackLookup(english, data)
            if not da then
                missCount = missCount + 1
                if missCount > 500 then missCache, missCount = {}, 1 end
                missCache[english] = true
            end
        end
        return da
    end)
    return ok and result or nil
end

local function translated(english)
    local da = lookup(english)
    if da then
        local ok, text = pcall(expand, da)
        return (ok and text or da) .. NBSP
    end
end

-- for Core.lua's tr(): gossip/trainer texts shown in frames this file does not know (Classic's old GossipFrame)
function ns.translateGossipText(text)
    if type(text) ~= "string" or #text < 8 or #text > 1500 or not text:find(" ", 1, true) then return nil end
    local da = lookup(text)
    if not da then return nil end
    local ok, out = pcall(expand, da)
    return ok and out or da
end

local function applyText(fs, english)
    local new = translated(english)
    if new and fs and fs.SetText then fs:SetText(new) end
end

-- option buttons hold coloured text like "|cff0000ffTitle|r"
local function applyOption(button)
    local text = button.GetText and button:GetText()
    if issecretvalue and issecretvalue(text) then return end
    if type(text) ~= "string" or text == "" then return end
    local prefix = text:match("^(|c%x%x%x%x%x%x%x%x)") or ""
    local suffix = prefix ~= "" and "|r" or ""
    local plain = text:gsub("^|c%x%x%x%x%x%x%x%x", ""):gsub("|r$", "")
    local new = translated(plain)
    if new and button.GetFontString then
        local fs = button:GetFontString()
        if fs then fs:SetText(prefix .. new .. suffix) end
    end
end

local function applyGossip()
    local panel = GossipFrame and GossipFrame.GreetingPanel
    local scrollBox = panel and panel.ScrollBox
    if not (scrollBox and scrollBox.EnumerateFrames) then return end
    local greeting = C_GossipInfo and C_GossipInfo.GetText and C_GossipInfo.GetText()
    for _, f in scrollBox:EnumerateFrames() do
        if f.GreetingText then
            applyText(f.GreetingText, greeting)
        elseif f.GetText then
            applyOption(f)
        end
    end
end

local function applyQuestGreeting()
    local text = GetGreetingText and GetGreetingText()
    if GreetingText and text and text ~= "" then applyText(GreetingText, text) end
end

local events = CreateFrame("Frame")
events:RegisterEvent("GOSSIP_SHOW")
events:RegisterEvent("QUEST_GREETING")
events:SetScript("OnEvent", function(_, event)
    local fn = (event == "QUEST_GREETING") and applyQuestGreeting or applyGossip
    C_Timer.After(0, fn)
    C_Timer.After(0.15, fn)
end)

-- NPC chat: the speaker's name is turned back into %s, which is how the database stores emotes
local CHAT_EVENTS = {
    "CHAT_MSG_MONSTER_SAY", "CHAT_MSG_MONSTER_YELL", "CHAT_MSG_MONSTER_EMOTE",
    "CHAT_MSG_MONSTER_WHISPER", "CHAT_MSG_MONSTER_PARTY",
    "CHAT_MSG_RAID_BOSS_EMOTE", "CHAT_MSG_RAID_BOSS_WHISPER",
}

local function translateSpeech(msg, sender)
    if type(msg) ~= "string" or msg == "" or msg:sub(-2) == NBSP then return end
    local plain = msg
    local name = type(sender) == "string" and sender ~= "" and sender or nil
    if name then plain = plain:gsub(escape(name), "%%s") end
    local da = lookup(plain)
    if not da then return end
    da = expand(da)
    if name then da = da:gsub("%%s", function() return name end) end
    return da
end

local function filter(_, _, msg, ...)
    if issecretvalue and issecretvalue(msg) then return false end
    local sender = ...
    if issecretvalue and issecretvalue(sender) then sender = nil end
    local ok, da = pcall(translateSpeech, msg, sender)
    if ok and da then return false, da, ... end
    return false
end

if ChatFrame_AddMessageEventFilter then
    for _, e in ipairs(CHAT_EVENTS) do ChatFrame_AddMessageEventFilter(e, filter) end
end

-- speech bubbles are separate frames filled from the original message
local function bubbleText(fs)
    local ok, text = pcall(fs.GetText, fs)
    if not ok or type(text) ~= "string" or (issecretvalue and issecretvalue(text)) then return end
    local ok2, da = pcall(translateSpeech, text, nil)
    if ok2 and da and da ~= text then fs:SetText(da) end
end

local function walkBubble(frame, depth)
    if depth > 4 or not frame then return end
    if frame.GetObjectType and frame:GetObjectType() == "FontString" then bubbleText(frame) return end
    if frame.GetRegions then
        for _, r in ipairs({ frame:GetRegions() }) do
            if r.GetObjectType and r:GetObjectType() == "FontString" then bubbleText(r) end
        end
    end
    if frame.GetChildren then
        for _, c in ipairs({ frame:GetChildren() }) do walkBubble(c, depth + 1) end
    end
end

local function translateBubbles()
    if not (C_ChatBubbles and C_ChatBubbles.GetAllChatBubbles) then return end
    local ok, bubbles = pcall(C_ChatBubbles.GetAllChatBubbles, true)
    if not (ok and bubbles) then return end
    for _, b in ipairs(bubbles) do pcall(walkBubble, b, 0) end
end

local bubbleEvents = CreateFrame("Frame")
for _, e in ipairs({ "CHAT_MSG_MONSTER_SAY", "CHAT_MSG_MONSTER_YELL", "CHAT_MSG_SAY" }) do
    pcall(bubbleEvents.RegisterEvent, bubbleEvents, e)
end
bubbleEvents:SetScript("OnEvent", function()
    for _, t in ipairs({ 0.05, 0.2, 0.5, 1, 2 }) do C_Timer.After(t, translateBubbles) end
end)
