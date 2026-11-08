local _, ns = ...

-- Danish class names, used where quest/gossip text names the player's own class (<Class>, $c)
ns.classDa = {
    Warrior = "Kriger", Paladin = "Korsridder", Hunter = "Jæger", Rogue = "Snigmorder", Priest = "Præst",
    Shaman = "Shaman", Mage = "Magiker", Warlock = "Heksemester", Druid = "Druide",
}

local function fill(s)
    if not s then return s end
    local name  = (UnitName("player"))
    local class = (UnitClass("player"))
    class = ns.classDa[class] or class
    local race  = (UnitRace("player"))
    s = s:gsub("<Name>",  function() return name  end)
    s = s:gsub("<Class>", function() return class end)
    s = s:gsub("<Race>",  function() return race  end)
    return s
end

-- Every hook is installed and run through pcall, so one wrong frame name or API call cannot stop the rest of the
-- addon. Errors are counted per hook and shown by /df status.
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

-- /df 1089 prints the Danish title and text for quest 1089
SLASH_DANISHFOREVER1 = "/df"
SlashCmdList.DANISHFOREVER = function(msg)
    if (msg or ""):match("^%s*status%s*$") then
        if ns.status then ns.status() end
        return
    end
    local trtext = (msg or ""):match("^tr%s+(.+)$")      -- /df tr Character Info   (type || for a |)
    if trtext then
        trtext = trtext:gsub("||", "|")
        local out = ns.trDebug and ns.trDebug(trtext)
        print("DanishForever tr: " .. ((out or "?"):gsub("|", "||")) .. "   Exact has it: " .. tostring(ns.Exact and ns.Exact[trtext] ~= nil))
        return
    end
    local cap = (msg or ""):match("^capture%s*(%a*)$")
    if cap then
        ns.capture = (cap == "on")
        print("DanishForever: capture is " .. (ns.capture and "ON: UI texts that stay English are saved. Show them with /df missed" or "OFF"))
        return
    end
    local mis = (msg or ""):match("^missed%s*(%a*)$")
    if mis then
        local list = {}
        for t in pairs((DanishForeverDB and DanishForeverDB.missed) or {}) do list[#list + 1] = t end
        table.sort(list)
        if mis == "clear" then
            if DanishForeverDB then DanishForeverDB.missed = {} end
            print("DanishForever: captured list cleared")
            return
        end
        print("DanishForever: " .. #list .. " English UI texts captured (all are saved on /reload). First 40:")
        for i = 1, math.min(40, #list) do print("  " .. (list[i]:gsub("|", "||"))) end
        return
    end
    local tdbg = (msg or ""):match("^tipdebug%s*(%a*)$")
    if tdbg then
        ns.tipdebug = (tdbg == "on")
        print("DanishForever: tooltip debug is " .. (ns.tipdebug and "ON: tooltip lines that stay English are printed in yellow" or "OFF"))
        return
    end
    local arg = (msg or ""):match("^globals%s*(%a*)$")
    if arg then
        DanishForeverDB = DanishForeverDB or {}
        if arg == "on" then
            DanishForeverDB.globals = true
            print("DanishForever: game strings will be replaced after /reload. Turn off with /df globals off.")
        elseif arg == "off" then
            DanishForeverDB.globals = false
            print("DanishForever: game strings go back to English after /reload.")
        else
            print("DanishForever: replacing game strings is " .. (DanishForeverDB.globals and "ON" or "OFF") .. ". Use /df globals on|off")
        end
        return
    end
    local id = tonumber(msg)
    local q = id and ns.Quests[id]
    if not q then
        print("DanishForever: no translation for quest " .. tostring(msg))
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
if type(QuestLog_UpdateQuestDetails) == "function" then
    safeHook("QuestLog_UpdateQuestDetails", "QuestLog_UpdateQuestDetails", function()
        local q = ns.Quests[currentQuestID()]
        if not q then return end
        if q.n and QuestLogQuestTitle then QuestLogQuestTitle:SetText(q.n) end
        if q.l and QuestLogObjectivesText then QuestLogObjectivesText:SetText(fill(q.l)) end
        if q.d and QuestLogQuestDescription then QuestLogQuestDescription:SetText(fill(q.d)) end
    end)
else
    ns.hookStatus["QuestLog_UpdateQuestDetails"] = { ok = true, calls = 0, errors = 0, last = "not present in this client (normal, Forever uses the newer quest log)" }
end

-- "Have you got the items?" panel shown before the reward
local function translateProgress()
    local q = ns.Quests[currentQuestID()]
    if not q then return end
    if q.n and QuestProgressTitleText then QuestProgressTitleText:SetText(q.n) end
    if q.p and QuestProgressText then QuestProgressText:SetText(fill(q.p)) end
end
if QuestFrameProgressPanel then
    local ok, err = pcall(QuestFrameProgressPanel.HookScript, QuestFrameProgressPanel, "OnShow", function() safeCall("progress panel", translateProgress) end)
    note("QuestFrameProgressPanel", ok, not ok and err or nil)
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
-- Unit tooltip info line: "Level 9 Undead", "Level 60 Undead Priest (Player)", "Level ?? Elite". Words are looked up in
-- ns.Exact, longest phrase first (up to 3 words, so "Night Elf" works); unknown words stay.
local function translateWords(rest)
    local ws, n = {}, 0
    for w in rest:gmatch("%S+") do n = n + 1; ws[n] = w end
    local out, i = {}, 1
    while i <= n do
        local done = false
        for len = math.min(3, n - i + 1), 1, -1 do
            local phrase = table.concat(ws, " ", i, i + len - 1)
            local pre, core, post = phrase:match("^(%(?)(.-)(%)?)$")
            local d = ns.Exact and core and ns.Exact[core]
            if d then
                out[#out + 1] = pre .. d .. post
                i = i + len
                done = true
                break
            end
        end
        if not done then out[#out + 1] = ws[i]; i = i + 1 end
    end
    return table.concat(out, " ")
end

local tr                                                     -- cached wrapper, defined after trRaw (trRaw calls it for sub-parts)
local trCache, trCacheN = {}, 0

local function trRaw(text)
    if issecretvalue and issecretvalue(text) then return text end
    if type(text) ~= "string" or text == "" then return text end
    if text:find("\194\160", 1, true) then text = (text:gsub("\194\160", " ")) end     -- no-break spaces break every pattern
    local v = ns.UI[text]
    if v then return v end
    v = ns.Exact and ns.Exact[text]                          -- fixed tooltip words
    if v then return v end
    do                                                       -- tracker/list lines start with a dash or a small icon: "- Rockjaw Trogg slain: 3/6", "|T...|t Name slain: 6/6"
        local pre, rest = text:match("^(%s*%-%s+)(.+)$")
        if not pre then pre, rest = text:match("^(|T[^|]*|t%s*)(.+)$") end
        if not pre then pre, rest = text:match("^(|A[^|]*|a%s*)(.+)$") end
        if pre and rest ~= "" then
            local r = tr(rest)
            if r ~= rest then return pre .. r end
        end
        local body, post = text:match("^(.-)(%s*|T[^|]*|t)$")                 -- icon at the end of the line
        if body and body ~= "" then
            local r = tr(body)
            if r ~= body then return r .. post end
        end
    end
    if text:find("\n- ", 1, true) then                       -- item use text with a list ("Fill the crate with ... list:|cnIQ1:\n- 20 Copper Ore\n- 20 Tin Ore|r"): each line on its own
        local changed = false
        local out = text:gsub("([^\r\n]+)", function(line)
            local pre, rest = line:match("^(Brug: )(.*)$")
            if not pre then pre, rest = line:match("^(Udstyr: )(.*)$") end
            pre = pre or ""; rest = rest or line
            local head, tok, tail = rest:match("^(.-)(|cn[%w_]+:)(.*)$")        -- quality colour marker in the middle of the line
            local function piece(s)
                local body, post = s:match("^(.-)(|r)$")
                if body then local r = tr(body); if r ~= body then changed = true end; return r .. post end
                local r = tr(s); if r ~= s then changed = true end
                return r
            end
            if head then return pre .. piece(head) .. tok .. piece(tail) end
            return pre .. piece(rest)
        end)
        if changed then return out end
    end
    do                                                       -- "\nRequires Rugged Leather (14), Runecloth (10)": keep the line breaks, translate the rest
        local lead, core, trail = text:match("^(%s*)(.-)(%s*)$")
        if core ~= "" and (lead ~= "" or trail ~= "") then
            local r = tr(core)
            if r ~= core then return lead .. r .. trail end
        end
    end
    do                                                       -- crafted items, effect and set bonus lines (independent of the pattern engine)
        local fac, amount = text:match("^Your (.+) reputation has increased by (%d+)%.$")      -- reputation messages (Classic wording)
        if fac then return "Omdømmet hos " .. tr(fac) .. " steg med " .. amount .. "." end
        fac, amount = text:match("^Your (.+) reputation has decreased by (%d+)%.$")
        if fac then return "Omdømmet hos " .. tr(fac) .. " faldt med " .. amount .. "." end
        local standing, fname = text:match("^You are now (%a+) with (.+)%.$")
        local STANDING = { Hated = "Hadet", Hostile = "Fjendtlig", Unfriendly = "Uvenlig", Neutral = "Neutral", Friendly = "Venlig",
                           Honored = "Æret", Revered = "Respekteret", Exalted = "Ophøjet" }
        if standing and STANDING[standing] then return "Du er nu " .. STANDING[standing] .. " hos " .. tr(fname) .. "." end
        local maker = text:match("^<Made by (.+)>$")
        if maker then return "<Lavet af " .. maker .. ">" end
        local n, rest = text:match("^%((%d+)%) Set: (.+)$")                   -- "(3) Set: Increases ..."
        if n then
            local rv = tr(rest)
            return "(" .. n .. ") Sæt: " .. rv
        end
        for pre, da in pairs({ ["Set: "] = "Sæt: ", ["Use: "] = "Brug: ", ["Equip: "] = "Udstyr: ", ["Chance on hit: "] = "Chance ved træf: " }) do
            if text:sub(1, #pre) == pre and #text > #pre then
                return da .. tr(text:sub(#pre + 1))
            end
        end
        -- potion effects: "Absorbs 1300 to 1700 fire damage. Lasts 1 hour." / "Increases your Fire resistance by 90 for 1 hour."
        local SCHOOL = { fire = "ild", frost = "frost", nature = "natur", shadow = "skygge", arcane = "arkan", holy = "hellig", physical = "fysisk" }
        local function dur(s)
            s = s:gsub("(%d+) hours?", "%1 time(r)"):gsub("(%d+) hrs?", "%1 time(r)"):gsub("(%d+) min%a*", "%1 min"):gsub("(%d+) sec%a*", "%1 sek")
            return s
        end
        local a, b, sc, d = text:match("^Absorbs (%d+) to (%d+) (%a+) damage%.%s*Lasts (.+)%.$")
        if a and SCHOOL[sc:lower()] then return "Absorberer " .. a .. " til " .. b .. " " .. SCHOOL[sc:lower()] .. "skade. Varer " .. dur(d) .. "." end
        sc, a, d = text:match("^Increases your (%a+) resistance by (%d+) for (.+)%.$")
        if sc and SCHOOL[sc:lower()] then return "Øger din " .. SCHOOL[sc:lower()] .. "modstand med " .. a .. " i " .. dur(d) .. "." end
    end
    do                                                       -- "Requires Level 20" / "Requires level 20" (any capitalisation)
        local n = text:match("^%s*Requires%s+[Ll]evel%s+(%d+)%s*$")
        if n then return "Kræver niveau " .. n end
        local a, b = text:match("^%s*Durability%s*:?%s*(%d+)%s*/%s*(%d+)%s*$")           -- "Durability 55 / 60"
        if a then return "Holdbarhed " .. a .. " / " .. b end
        local tp = text:match("^Talent Points:%s*(.+)$")                                  -- talent window
        if tp then return "Talentpoint: " .. tp end
        local tree, spent = text:match("^Points spent in (.-) Talents:%s*(.+)$")
        if tree then
            local tv = (ns.UI and ns.UI[tree]) or (ns.Exact and ns.Exact[tree]) or tree
            return "Point brugt i " .. tv .. "-talenter: " .. spent
        end
        local rk = text:match("^%(Rank (%d+)%)$")
        if rk then return "(Rang " .. rk .. ")" end
    end
    do                                                       -- a whole line wrapped in a colour: "|cffff2020Requires Level 20|r"
        local pre, inner, post = text:match("^(|c%x%x%x%x%x%x%x%x)([^|]+)(|r)$")
        if inner then
            local iv = tr(inner)
            if iv ~= inner then return pre .. iv .. post end
        end
    end
    do                                                       -- spell tooltip: "10 sec cooldown", "1.5 min cooldown", "2.5 sec cast"
        local num, unit, what = text:match("^([%d%.,]+) (%a+) (%a+)$")
        if num and (what == "cooldown" or what == "cast") then
            local u = ({ sec = "sek.", min = "min.", hr = "timers", day = "dags", days = "dags" })[unit]
            if u then return num .. " " .. u .. " " .. (what == "cooldown" and "genopladning" or "besværgelse") end
        end
    end
    do
        local lvl, rest = text:match("^Level ([%d%?]+)%s*(.*)$")          -- unit tooltip: "Level 9 Undead"
        if lvl and #text < 60 then
            return "Niveau " .. lvl .. (rest ~= "" and (" " .. translateWords(rest)) or "")
        end
    end
    do                                                       -- bottom bar tooltips: "Character Info |cffffd100(C)|r"
        local b, s = text:match("^(.-)(%s*|c%x%x%x%x%x%x%x%x%([^|]-%)|r)$")
        if b and b ~= "" then
            local bv = (ns.UI and ns.UI[b]) or (ns.Exact and ns.Exact[b])
            if bv then return bv .. s end
        end
    end
    local count, name = text:match("^(%d+/%d+) (.+)$")      -- "0/1 Sleepers' Key"
    if count then
        local o = (ns.Obj and ns.Obj[name]) or (ns.ItemNames and ns.ItemNames[name])
        if o then return count .. " " .. o end
    end
    do                                                       -- "20 Copper Ore" (bundle contents): count, then the item name
        local cnt, iname = text:match("^(%d+) (.+)$")
        if cnt then
            local o = (ns.ItemNames and ns.ItemNames[iname]) or (ns.Obj and ns.Obj[iname]) or (ns.Exact and ns.Exact[iname])
            if o then return cnt .. " " .. o end
        end
    end
    if ns.ItemNames then
        v = ns.ItemNames[text]                               -- item names
        if v then return v end
    end
    if ns.QuestNames then
        v = ns.QuestNames[text]                              -- quest titles in the tracker and quest log list
        if v then return v end
        do                                                   -- tracker with quest levels: "[14] Supplies for the Crossroads", "[60+] Title", "[14D] Title"
            local lvl, qn = text:match("^(%[%d[%d%+%a]*%]%s+)(.+)$")
            if lvl then
                local qv = ns.QuestNames[qn]
                if qv then return lvl .. qv end
            end
        end
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
        local ok, r = pcall(ns.translateSuffix, text)       -- each step is isolated: an error in one must not block the next
        if ok and r then return r end
    end
    if ns.ItemDescs then
        local inner = text:match('^"(.*)"$')                 -- flavor text is shown in quotes
        v = inner and ns.ItemDescs[inner]
        if v then return '"' .. v .. '"' end
        v = ns.ItemDescs[text]
        if v then return v end
    end
    if ns.translateSpellDesc and #text > 11 then             -- spell descriptions with the numbers filled in
        local ok, r = pcall(ns.translateSpellDesc, text)
        if ok and r and r ~= text then return r end
        if not ok then ns.lastStageError = "spelldesc: " .. tostring(r) end
    end
    if ns.translatePattern then                              -- "+4 Spirit", "Requires Level 45", ...
        local ok, r = pcall(ns.translatePattern, text, tr)
        if ok and r then return r end
        if not ok then ns.lastStageError = "pattern: " .. tostring(r) end
    end
    if ns.translateCaptured then                             -- text captured in game and translated afterwards (Captured.lua)
        local ok, r = pcall(ns.translateCaptured, text)
        if ok and r then return r end
    end
    if ns.translateGossipText then                           -- NPC/trainer greetings and options in Classic's own gossip frame
        local ok, r = pcall(ns.translateGossipText, text)
        if ok and r then return r end
    end
    if #text > 30 and ns.Exact then                          -- mail bodies: the game has filled in the player's name
        local pname = UnitName and UnitName("player")
        if pname and pname ~= "" and text:find(pname, 1, true) then
            v = ns.Exact[(text:gsub(pname:gsub("%p", "%%%0"), "<Name>"))]
            if v then return fill(v) end
        end
    end
    -- Button tooltips add the keybinding: "Character Info |cffffd200(C)|r" or "Spellbook (P)". Translate the name only.
    local base, suffix = text:match("^(.-)(%s*|c%x%x%x%x%x%x%x%x%([^|]*%)|r)$")
    if not base or base == "" then
        base, suffix = text:match("^(.-)(%s%([^%(%)|]+%))$")
        if suffix and #suffix > 20 then base = nil end
    end
    if base and base ~= "" and base ~= text then
        v = tr(base)
        if v ~= base then return v .. suffix end
    end
    return text
end

-- The map and other busy frames set the same labels over and over; the result for a given text never changes, so keep it
-- (untranslatable text too, which is the expensive case: it runs through every step before giving up).
tr = function(text)
    if type(text) ~= "string" or #text > 600 or (issecretvalue and issecretvalue(text)) then return trRaw(text) end
    local c = trCache[text]
    if c then return c end
    local r = trRaw(text)
    if type(r) == "string" then
        trCacheN = trCacheN + 1
        if trCacheN > 40000 then trCache, trCacheN = {}, 1 end
        trCache[text] = r
    end
    return r
end

local cacheReset = CreateFrame("Frame")                      -- player name, class and data can change while loading in
cacheReset:RegisterEvent("PLAYER_LOGIN")
cacheReset:RegisterEvent("PLAYER_ENTERING_WORLD")
cacheReset:SetScript("OnEvent", function() trCache, trCacheN = {}, 0 end)

-- /df capture on: remember UI texts that stayed English (saved in DanishForeverDB.missed, shown with /df missed)
local function missed(t)
    if type(t) ~= "string" or #t < 2 or #t > 400 or not t:find("%a") then return end
    if t:find("[\195\133\134\152\166\184]") then return end        -- already Danish (æ ø å): not interesting
    DanishForeverDB = DanishForeverDB or {}
    DanishForeverDB.missed = DanishForeverDB.missed or {}
    DanishForeverDB.missed[t] = true
end
ns.missed = missed

-- Record text only if it is still English a moment later: quest, gossip and book windows replace their text after SetText.
local function missedLater(w, t)
    if not (C_Timer and C_Timer.After) then return missed(t) end
    C_Timer.After(0.5, function()
        local ok, cur = pcall(w.GetText, w)
        if ok and not (issecretvalue and issecretvalue(cur)) and cur == t then missed(t) end
    end)
end

-- /df tr <text>: the result plus what each step says on its own (an ERROR here explains a whole class of English lines)
ns.trDebug = function(t)
    local function stage(label, f, ...)
        if not f then print("  " .. label .. ": (missing)"); return end
        local ok, r = pcall(f, ...)
        print("  " .. label .. ": " .. (ok and (r == nil and "no match" or tostring(r):gsub("|", "||")) or ("ERROR " .. tostring(r))))
    end
    stage("spell description", ns.translateSpellDesc, t)
    stage("patterns", ns.translatePattern, t, tr)
    if ns.lastStageError then print("  last error seen while translating: " .. ns.lastStageError) end
    return tr(t)
end

-- Self-test at login: if the pattern step is broken, say so right away instead of leaving English lines unexplained
local selfTest = CreateFrame("Frame")
selfTest:RegisterEvent("PLAYER_LOGIN")
selfTest:SetScript("OnEvent", function()
    local bad = {}
    for en, da in pairs({ ["Classes: Druid"] = "Klasser: Druide", ["Unique (2)"] = "Unik (2)" }) do
        local ok, r = pcall(tr, en)
        if not ok or r ~= da then bad[#bad + 1] = en .. " -> " .. tostring(r) end
    end
    if #bad > 0 then
        print("|cffff0000DanishForever self-test failed|r (patterns do not work). Run /df tr Classes: Druid and send me the output.")
        for _, b in ipairs(bad) do print("   " .. (b:gsub("|", "||"))) end
    end
end)

local function hookSetText(obj)
    safeHook("SetText " .. obj:GetObjectType(), getmetatable(obj).__index, "SetText", function(self, text)
        if busy then return end
        if issecretvalue and issecretvalue(text) then return end
        local new = tr(text)
        if new ~= text then
            busy = true
            pcall(self.SetText, self, new)      -- busy must always be reset, even if SetText fails
            busy = false
        elseif ns.capture then
            missedLater(self, text)
        end
    end)
    -- SetFormattedText ("|cff000000%s|r" quest titles in NPC windows, many labels) never goes through SetText
    local index = getmetatable(obj).__index
    if type(index.SetFormattedText) == "function" then
        safeHook("SetFormattedText " .. obj:GetObjectType(), index, "SetFormattedText", function(self)
            if busy then return end
            local t = self:GetText()
            if issecretvalue and issecretvalue(t) then return end      -- secret values must be checked before any comparison
            if type(t) ~= "string" or t == "" then return end
            local new = tr(t)
            if new ~= t then
                busy = true
                pcall(self.SetText, self, new)
                busy = false
            elseif ns.capture then
                missedLater(self, t)
            end
        end)
    end
end

note("hookSetText labels", pcall(function() hookSetText(UIParent:CreateFontString()) end))    -- all text labels
note("hookSetText buttons", pcall(function() hookSetText(CreateFrame("Button")) end))        -- all button labels

-- Text set by the frame definition never passes through SetText, so translate it directly
local function retranslate(w)
    if w and w.GetText and w.SetText then
        local t = w:GetText()
        if issecretvalue and issecretvalue(t) then return end
        local new = tr(t)
        if new ~= t then w:SetText(new) elseif ns.capture then missedLater(w, t) end
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
    local ok, err = pcall(QuestMapFrame.HookScript, QuestMapFrame, "OnShow", function() safeCall("quest map", retranslateStatic) end)
    note("QuestMapFrame", ok, not ok and err or nil)
else
    ns.hookStatus["QuestMapFrame"] = { ok = true, calls = 0, errors = 0, last = "not present in this client (normal, the quest log is a separate frame)" }
end

-- Item tooltips: lines the tooltip builds without SetText are translated after it is filled in
local seenLine = setmetatable({}, { __mode = "k" })    -- line FontString -> the text it had when we last handled it (Danish or untranslatable)
local function retranslateTooltip(tip)
    if not tip or not tip.GetName or not tip.NumLines then return end
    local name = tip:GetName()
    if not name then return end
    local changed = false
    for i = 1, tip:NumLines() do
        for _, side in ipairs({ "TextLeft", "TextRight" }) do
            local w = _G[name .. side .. i]
            local t = w and w.GetText and w:GetText()
            if t and not (issecretvalue and issecretvalue(t)) and type(t) == "string" and t ~= "" and seenLine[w] ~= t then
                local trok, new
                if t == "Back" then trok, new = true, "Kappe"      -- the cloak slot; the button "Back" stays "Tilbage"
                else trok, new = pcall(tr, t) end                  -- one bad line must not stop the others
                if not trok then
                    if ns.tipdebug then print("|cffff0000[tip error]|r " .. (t:gsub("|", "||")) .. " : " .. tostring(new)) end
                    new = t
                end
                if new ~= t then
                    pcall(w.SetText, w, new)
                    changed = true
                    if ns.tipdebug then print("|cff00ff00[tip ok]|r " .. (new:gsub("|", "||"))) end
                elseif ns.tipdebug then
                    print("|cffffff00[tip]|r " .. (t:gsub("|", "||")))     -- /df tipdebug on: lines that stayed English
                end
                if new == t and ns.capture then
                    missedLater(w, t)                                      -- /df capture on: also saved for me to read
                end
                seenLine[w] = new                                          -- same text next time (even every frame): nothing to do
            end
        end
    end
    if changed then pcall(tip.Show, tip) end      -- re-measure the tooltip after the text changed
end

if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum and Enum.TooltipDataType then
    for kind, t in pairs(Enum.TooltipDataType) do         -- every tooltip type, including UnitAura (buffs and debuffs)
        if type(kind) == "string" and type(t) == "number" then
            local ok, err = pcall(TooltipDataProcessor.AddTooltipPostCall, t, function(tip) safeCall("tooltip " .. kind, retranslateTooltip, tip) end)
            note("tooltip " .. kind, ok, not ok and err or nil)
        end
    end
elseif GameTooltip and GameTooltip.HookScript then
    local ok, err = pcall(GameTooltip.HookScript, GameTooltip, "OnTooltipSetItem", retranslateTooltip)
    note("tooltip (old API)", ok, not ok and err or nil)
else
    note("tooltip", false, "no tooltip API found")
end

-- Buff/debuff tooltips are rebuilt by the game every update (to refresh the timer) without being shown again, so OnShow
-- is not enough: translate right after every function that fills a tooltip.
for _, tname in ipairs({ "GameTooltip", "ItemRefTooltip" }) do
    local tip = _G[tname]
    if tip then
        for _, m in ipairs({ "SetUnitAura", "SetUnitBuff", "SetUnitDebuff", "SetPlayerBuff", "SetSpellByID", "SetSpellBookItem",
                             "SetAction", "SetHyperlink", "SetTrackingSpell", "SetPetAction", "SetShapeshift", "SetTalent",
                             "SetCurrencyToken", "SetQuestItem", "SetQuestLogItem", "SetInventoryItem", "SetBagItem",
                             "SetMerchantItem", "SetLootItem", "SetUnit", "SetTradeSkillItem", "SetCraftSpell", "SetCraftItem",
                             "SetUnitAuraByAuraInstanceID", "SetUnitBuffByAuraInstanceID", "SetUnitDebuffByAuraInstanceID",
                             "RefreshData", "ProcessInfo" }) do
            if type(tip[m]) == "function" then
                pcall(hooksecurefunc, tip, m, function(self) safeCall("tooltip " .. tname, retranslateTooltip, self) end)
            end
        end
    end
end

-- Every tooltip is translated when it is shown. This catches spell tooltips, unit tooltips and the small menu/button
-- tooltips (GameTooltip:SetText + AddLine), which have no OnTooltipSetItem event. Needed on Classic Era.
for _, tname in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2", "ItemRefShoppingTooltip1",
                         "ItemRefShoppingTooltip2", "EmbeddedItemTooltip", "WorldMapTooltip" }) do
    local tip = _G[tname]
    if tip and tip.HookScript then
        for _, script in ipairs({ "OnShow", "OnTooltipSetSpell", "OnTooltipSetUnit", "OnTooltipSetQuest",
                                  "OnTooltipSetAchievement", "OnTooltipSetEquipmentSet", "OnTooltipSetDefaultAnchor" }) do
            local ok, err = pcall(tip.HookScript, tip, script, function(self) safeCall("tooltip " .. tname, retranslateTooltip, self) end)
            if not ok then ns.hookStatus["tooltip " .. tname .. " " .. script] = { ok = true, calls = 0, errors = 0, last = "no such script here (fine)" } end
        end
    end
end

-- Tooltips for things in the world (herb and ore nodes, chests, signs) are rewritten by the game itself every frame while the
-- mouse is on them, with no script event we could hook. Check the main tooltip once per frame; seenLine makes that cheap
-- (a line is only translated again when the game put different text back).
if GameTooltip and GameTooltip.HookScript then
    pcall(GameTooltip.HookScript, GameTooltip, "OnUpdate", function(self)
        if self:IsShown() then safeCall("tooltip update", retranslateTooltip, self) end
    end)
end

-- Chat: item, spell, quest and achievement links show their name as "[Linen Cloth]" inside |H...|h[...]|h. Chat lines are
-- not FontString text, so translate the names with the official chat filter (safe for secure code, the link data stays the same).
local LINK_TYPES = { item = true, spell = true, enchant = true, quest = true, achievement = true, talent = true, trade = true }
local function translateLinks(msg)
    return (msg:gsub("(|H(%a+):[^|]*|h)%[(.-)%](|h)", function(open, kind, name, close)
        if not LINK_TYPES[kind] then return nil end
        local new = tr(name)
        if new == name then return nil end
        return open .. "[" .. new .. "]" .. close
    end))
end
ns.translateLinks = translateLinks

if ChatFrame_AddMessageEventFilter then
    local function chatFilter(_, _, msg, ...)
        if type(msg) ~= "string" or issecretvalue and issecretvalue(msg) or not msg:find("|H", 1, true) then return false end
        local ok, new = pcall(translateLinks, msg)
        if ok and new ~= msg then return false, new, ... end
        return false
    end
    for _, ev in ipairs({ "CHAT_MSG_LOOT", "CHAT_MSG_SYSTEM", "CHAT_MSG_SKILL", "CHAT_MSG_TRADESKILLS", "CHAT_MSG_SAY", "CHAT_MSG_YELL",
                          "CHAT_MSG_PARTY", "CHAT_MSG_PARTY_LEADER", "CHAT_MSG_RAID", "CHAT_MSG_RAID_LEADER", "CHAT_MSG_GUILD",
                          "CHAT_MSG_OFFICER", "CHAT_MSG_WHISPER", "CHAT_MSG_WHISPER_INFORM", "CHAT_MSG_CHANNEL" }) do
        pcall(ChatFrame_AddMessageEventFilter, ev, chatFilter)
    end
    note("chat links", true)
else
    note("chat links", false, "ChatFrame_AddMessageEventFilter not found")
end

-- Windows and buttons defined by the game's own XML get their text before any SetText hook can see it. Walk every
-- top-level window when it is shown (and once more a moment later, after the game filled in its own text).
local hookedWindows = {}
local function hookWindow(f)
    if hookedWindows[f] or not f.HookScript or f.NumLines then return end     -- tooltips are handled above
    local name = f.GetName and f:GetName() or ""
    if name:find("^ChatFrame") or name == "WorldFrame" then return end
    hookedWindows[f] = true
    pcall(f.HookScript, f, "OnShow", function(self)
        safeCall("window walk", walk, self, 0)
        if C_Timer and C_Timer.After then C_Timer.After(0.1, function() safeCall("window walk", walk, self, 0) end) end
    end)
end
local function hookAllWindows()
    pcall(function() for _, c in ipairs({ UIParent:GetChildren() }) do hookWindow(c) end end)
end
hookAllWindows()
local winEvents = CreateFrame("Frame")
winEvents:RegisterEvent("PLAYER_LOGIN")
winEvents:RegisterEvent("ADDON_LOADED")                -- Blizzard's load-on-demand windows appear later
winEvents:SetScript("OnEvent", function() hookAllWindows() end)
if ShowUIPanel then safeHook("ShowUIPanel walk", "ShowUIPanel", function(f) if f then walk(f, 0) end end) end
if ToggleDropDownMenu then safeHook("DropDown walk", "ToggleDropDownMenu", function() walk(DropDownList1, 0) end) end

-- /df status: which hooks were installed, which data tables loaded, and any errors so far
local function status()
    print("|cff00ff00DanishForever status|r")
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
