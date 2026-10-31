local _, ns = ...

local function fill(s)
    if not s then return s end
    local name  = (UnitName("player"))
    local class = (UnitClass("player"))
    local race  = (UnitRace("player"))
    s = s:gsub("<Name>",  function() return name  end)
    s = s:gsub("<Class>", function() return class end)
    s = s:gsub("<Race>",  function() return race  end)
    return s
end

-- Every hook is installed and run through pcall, so one wrong frame name or API call cannot stop the rest of the
-- addon. Errors are counted per hook and shown by /dui status.
ns.hookStatus = {}
local function note(name, ok, err)
    local s = ns.hookStatus[name] or { ok = ok, calls = 0, errors = 0 }
    ns.hookStatus[name] = s
    s.ok = ok
    if err then s.errors = s.errors + 1; s.last = tostring(err):sub(1, 160) end
end

-- safeHook(label, "GlobalFunction", fn)  or  safeHook(label, table, "Method", fn)
local function safeHook(label, a, b, c)
    local fn = c or b
    local function wrapped(...)
        local ran, e = pcall(fn, ...)
        if not ran then note(label, true, e) end
    end
    local ok, err
    if c then ok, err = pcall(hooksecurefunc, a, b, wrapped) else ok, err = pcall(hooksecurefunc, a, wrapped) end
    note(label, ok, not ok and err or nil)
    return ok
end

local function safeCall(name, fn, ...)
    local ok, err = pcall(fn, ...)
    note(name, ok, not ok and err or nil)
    return ok
end

local function currentQuestID()
    local id = GetQuestID and GetQuestID() or 0
    if id and id ~= 0 then return id end
    if C_QuestLog and C_QuestLog.GetSelectedQuest then
        id = C_QuestLog.GetSelectedQuest()
        if id and id ~= 0 then return id end
    end
    local d = QuestMapFrame and QuestMapFrame.DetailsFrame
    if d and d.questID and d.questID ~= 0 then return d.questID end
    if GetQuestLogSelection and GetQuestIDFromLogIndex then      -- the old-style quest log (QuestLogFrame)
        local index = GetQuestLogSelection()
        if index and index > 0 then
            id = GetQuestIDFromLogIndex(index)
            if id and id ~= 0 then return id end
        end
    end
    return 0
end

-- /dui 1089 prints the Danish title and text for quest 1089
SLASH_DANISHUI1 = "/dui"
SlashCmdList.DANISHUI = function(msg)
    if (msg or ""):match("^%s*status%s*$") then
        if ns.status then ns.status() end
        return
    end
    local arg = (msg or ""):match("^globals%s*(%a*)$")
    if arg then
        DanishUIDB = DanishUIDB or {}
        if arg == "on" then
            DanishUIDB.globals = true
            print("DanishUI: game strings will be replaced after /reload. Turn off with /dui globals off.")
        elseif arg == "off" then
            DanishUIDB.globals = false
            print("DanishUI: game strings go back to English after /reload.")
        else
            print("DanishUI: replacing game strings is " .. (DanishUIDB.globals and "ON" or "OFF") .. ". Use /dui globals on|off")
        end
        return
    end
    local id = tonumber(msg)
    local q = id and ns.Quests[id]
    if not q then
        print("DanishUI: no translation for quest " .. tostring(msg))
        return
    end
    print("|cff00ff00" .. (q.n or "?") .. "|r")
    print(fill(q.d or q.l or ""))
end

safeHook("QuestInfo_Display", "QuestInfo_Display", function()
    local id = currentQuestID()
    local q = ns.Quests[id]
    if not q then return end
    if q.n and QuestInfoTitleHeader then QuestInfoTitleHeader:SetText(q.n) end
    if q.d and QuestInfoDescriptionText then QuestInfoDescriptionText:SetText(fill(q.d)) end
    if q.l and QuestInfoObjectivesText then QuestInfoObjectivesText:SetText(fill(q.l)) end
    if q.c and QuestInfoRewardText then QuestInfoRewardText:SetText(fill(q.c)) end       -- hand-in text
end)

-- The old-style quest log (QuestLogFrame) fills its detail pane with its own function
safeHook("QuestLog_UpdateQuestDetails", "QuestLog_UpdateQuestDetails", function()
    local q = ns.Quests[currentQuestID()]
    if not q then return end
    if q.n and QuestLogQuestTitle then QuestLogQuestTitle:SetText(q.n) end
    if q.l and QuestLogObjectivesText then QuestLogObjectivesText:SetText(fill(q.l)) end
    if q.d and QuestLogQuestDescription then QuestLogQuestDescription:SetText(fill(q.d)) end
end)

-- "Have you got the items?" panel shown before the reward
local function translateProgress()
    local q = ns.Quests[currentQuestID()]
    if not q then return end
    if q.n and QuestProgressTitleText then QuestProgressTitleText:SetText(q.n) end
    if q.p and QuestProgressText then QuestProgressText:SetText(fill(q.p)) end
end
if QuestFrameProgressPanel then
    note("QuestFrameProgressPanel", pcall(QuestFrameProgressPanel.HookScript, QuestFrameProgressPanel, "OnShow", function() safeCall("progress panel", translateProgress) end))
else
    note("QuestFrameProgressPanel", false, "frame not found")
end

ns.UI = {
    ["Description"] = "Beskrivelse",
    ["Rewards"] = "Belønninger",
    ["You will receive:"] = "Du vil modtage:",
    ["Abandon"] = "Opgiv",
    ["Share"] = "Del",
    ["Track"] = "Spor",
    ["Back"] = "Tilbage",
    ["REWARDS"] = "BELØNNINGER",
    ["BACK"] = "TILBAGE",
    ["DESCRIPTION"] = "BESKRIVELSE",
}

local busy = false
local function tr(text)
    if issecretvalue and issecretvalue(text) then return text end
    if type(text) ~= "string" or text == "" then return text end
    local v = ns.UI[text]
    if v then return v end
    v = ns.Exact and ns.Exact[text]                          -- fixed tooltip words
    if v then return v end
    local count, name = text:match("^(%d+/%d+) (.+)$")      -- "0/1 Sleepers' Key"
    if count then
        local o = (ns.Obj and ns.Obj[name]) or (ns.ItemNames and ns.ItemNames[name])
        if o then return count .. " " .. o end
    end
    if ns.ItemNames then
        v = ns.ItemNames[text]                               -- item names
        if v then return v end
    end
    if ns.QuestNames then
        v = ns.QuestNames[text]                              -- quest titles in the tracker and quest log list
        if v then return v end
    end
    if ns.QuestTexts and #text > 40 then
        v = ns.QuestTexts[text]                              -- class/race variants of a quest text
        if v then return fill(v) end
    end
    local sname, scount = text:match("^(.+) %((%d+/%d+)%)$")   -- item set header: "Battlegear of Might (3/8)"
    if sname and ns.Exact and ns.Exact[sname] then
        return ns.Exact[sname] .. " (" .. scount .. ")"
    end
    local oname, ocount = text:match("^(.+): (%d+/%d+)$")    -- tracker form: "Sleepers' Key: 0/1"
    if oname then
        local o = (ns.Obj and ns.Obj[oname]) or (ns.ItemNames and ns.ItemNames[oname])
        if o then return o .. ": " .. ocount end
    end
    if ns.translateSuffix then                               -- "Bent Staff of the Whale"
        v = ns.translateSuffix(text)
        if v then return v end
    end
    if ns.ItemDescs then
        local inner = text:match('^"(.*)"$')                 -- flavor text is shown in quotes
        v = inner and ns.ItemDescs[inner]
        if v then return '"' .. v .. '"' end
        v = ns.ItemDescs[text]
        if v then return v end
    end
    if ns.translateSpellDesc and #text > 11 then             -- spell descriptions with the numbers filled in
        v = ns.translateSpellDesc(text)
        if v then return v end
    end
    if ns.translatePattern then                              -- "+4 Spirit", "Requires Level 45", ...
        v = ns.translatePattern(text, tr)
        if v then return v end
    end
    if #text > 30 and ns.Exact then                          -- mail bodies: the game has filled in the player's name
        local pname = UnitName and UnitName("player")
        if pname and pname ~= "" and text:find(pname, 1, true) then
            v = ns.Exact[(text:gsub(pname:gsub("%p", "%%%0"), "<Name>"))]
            if v then return fill(v) end
        end
    end
    return text
end

local function hookSetText(obj)
    safeHook("SetText " .. obj:GetObjectType(), getmetatable(obj).__index, "SetText", function(self, text)
        if busy then return end
        if issecretvalue and issecretvalue(text) then return end
        local new = tr(text)
        if new ~= text then
            busy = true
            pcall(self.SetText, self, new)      -- busy must always be reset, even if SetText fails
            busy = false
        end
    end)
end

note("hookSetText labels", pcall(function() hookSetText(UIParent:CreateFontString()) end))    -- all text labels
note("hookSetText buttons", pcall(function() hookSetText(CreateFrame("Button")) end))        -- all button labels

-- Text set by the frame definition never passes through SetText, so translate it directly
local function retranslate(w)
    if w and w.GetText and w.SetText then
        local t = w:GetText()
        if issecretvalue and issecretvalue(t) then return end
        local new = tr(t)
        if new ~= t then w:SetText(new) end
    end
end

-- Walk every text region and button under a frame, so no frame names are needed
local function walk(f, depth)
    if not f or depth > 8 then return end
    pcall(function()
        for _, r in ipairs({ f:GetRegions() }) do retranslate(r) end
        for _, c in ipairs({ f:GetChildren() }) do
            retranslate(c)
            if c.GetFontString then retranslate(c:GetFontString()) end
            walk(c, depth + 1)
        end
    end)
end

local function retranslateStatic()
    walk(QuestMapFrame, 0)
    walk(QuestInfoFrame, 0)
    local d = QuestMapFrame and QuestMapFrame.DetailsFrame
    if d then
        retranslate(d.BackButton)
        retranslate(d.AbandonButton)
        retranslate(d.ShareButton)
        retranslate(d.TrackButton)
    end
    retranslate(QuestInfoDescriptionHeader)
    retranslate(QuestInfoRewardsFrame and QuestInfoRewardsFrame.Header)
    retranslate(QuestInfoRewardsFrame and QuestInfoRewardsFrame.ItemReceiveText)
end

safeHook("QuestInfo_Display static", "QuestInfo_Display", retranslateStatic)
if QuestMapFrame then
    note("QuestMapFrame", pcall(QuestMapFrame.HookScript, QuestMapFrame, "OnShow", function() safeCall("quest map", retranslateStatic) end))
else
    note("QuestMapFrame", false, "frame not found (normal in Classic if the quest log is a separate frame)")
end

-- Item tooltips: lines the tooltip builds without SetText are translated after it is filled in
local function retranslateTooltip(tip)
    if not tip or not tip.GetName or not tip.NumLines then return end
    local name = tip:GetName()
    if not name then return end
    pcall(function()
        for i = 1, tip:NumLines() do
            retranslate(_G[name .. "TextLeft" .. i])
            retranslate(_G[name .. "TextRight" .. i])
        end
        tip:Show()      -- re-measure the tooltip after the text changed
    end)
end

if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum and Enum.TooltipDataType then
    for _, kind in ipairs({ "Item", "Spell", "Unit", "Object", "Currency", "Toy", "Mount", "Achievement", "Quest" }) do
        local t = Enum.TooltipDataType[kind]
        if t then
            note("tooltip " .. kind, pcall(TooltipDataProcessor.AddTooltipPostCall, t, function(tip) safeCall("tooltip " .. kind, retranslateTooltip, tip) end))
        end
    end
elseif GameTooltip and GameTooltip.HookScript then
    note("tooltip (old API)", pcall(GameTooltip.HookScript, GameTooltip, "OnTooltipSetItem", retranslateTooltip))
else
    note("tooltip", false, "no tooltip API found")
end

-- /dui status: which hooks were installed, which data tables loaded, and any errors so far
local function status()
    print("|cff00ff00DanishUI status|r")
    local names = {}
    for k in pairs(ns.hookStatus) do names[#names + 1] = k end
    table.sort(names)
    for _, k in ipairs(names) do
        local s = ns.hookStatus[k]
        print(("  %s %s%s"):format(s.ok and "|cff00ff00ok|r" or "|cffff0000FAIL|r", k,
            s.errors > 0 and (" - " .. s.errors .. " errors, last: " .. (s.last or "?")) or (s.last and (" - " .. s.last) or "")))
    end
    local function count(t) local n = 0 for _ in pairs(t or {}) do n = n + 1 end return n end
    for _, k in ipairs({ "Quests", "QuestNames", "ItemNames", "ItemDescs", "Exact", "Gossip", "Books", "GlobalStrings",
                         "SpellDescExact", "SpellDescTemplates", "EmoteTemplates", "Obj" }) do
        print(("  %s: %d entries"):format(k, count(ns[k])))
    end
end
ns.status = status