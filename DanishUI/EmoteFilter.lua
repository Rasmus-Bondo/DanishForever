local _, ns = ...

-- Emote lines are built by the game and printed in chat ("Bob agrees with you."), so they never pass through
-- SetText. A chat filter matches each line against the translated templates and swaps in the Danish one,
-- keeping the names. Chat text can be a protected "secret" value in some situations; those lines are left alone.

local templates

local function compile()
    templates = {}
    for _, t in ipairs(ns.EmoteTemplates or {}) do
        local en, da = t[1], t[2]
        local pat = en:gsub("[%^%$%(%)%%%.%[%]%*%+%-%?]", "%%%0")   -- escape magic characters ("%s" becomes "%%s")
        pat = pat:gsub("%%%%s", "(.+)")
        local _, names = en:gsub("%%s", "")
        templates[#templates + 1] = { pat = "^" .. pat .. "$", da = da, literal = #en - 2 * names }
    end
    table.sort(templates, function(a, b) return a.literal > b.literal end)   -- most specific template first
end

local function fill(fmt, caps)
    local i = 0
    return (fmt:gsub("%%(%d*)%$?s", function(n)
        if n ~= "" then return caps[tonumber(n)] or "" end
        i = i + 1
        return caps[i] or ""
    end))
end

local function translate(msg)
    if not templates then compile() end
    for i = 1, #templates do
        local t = templates[i]
        local caps = { msg:match(t.pat) }
        if caps[1] then
            return fill(t.da, caps)
        end
    end
end

local function filter(_, _, msg, ...)
    if type(msg) ~= "string" or (issecretvalue and issecretvalue(msg)) then return false end
    local ok, new = pcall(translate, msg)
    if ok and new then
        return false, new, ...
    end
    return false
end

if ChatFrame_AddMessageEventFilter then
    ChatFrame_AddMessageEventFilter("CHAT_MSG_TEXT_EMOTE", filter)
end
