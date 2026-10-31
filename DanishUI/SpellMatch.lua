local _, ns = ...

-- Spell and aura descriptions. The tooltip shows them with the numbers already filled in ("Lasts 30 sec."), so
-- each English template from SpellDescs.lua is a Lua pattern; the captured values go into the Danish text.

local DURATION = { { " seconds", " sek" }, { " second", " sek" }, { " sec", " sek" }, { " minutes", " min" }, { " minute", " min" },
                   { " min", " min" }, { " hours", " timer" }, { " hour", " time" }, { " days", " dage" }, { " day", " dag" } }

local function duration(v)
    for _, w in ipairs(DURATION) do v = v:gsub(w[1] .. "%f[%A]", w[2]) end
    return v
end

local function apply(entry, text)
    local caps = { text:match(entry[1]) }
    if #caps == 0 then return nil end
    for i = 1, #caps do if caps[i] == "" or #caps[i] > 40 then return nil end end
    for _, i in ipairs(entry[2]) do if caps[i] then caps[i] = duration(caps[i]) end end
    local out = {}
    for i = 3, #entry do
        local p = entry[i]
        if type(p) == "number" then
            out[#out + 1] = caps[p] or ""
        elseif type(p) == "table" then
            local n = tonumber((caps[p[3]] or ""):match("[%d%.]+"))
            out[#out + 1] = (n == 1) and p[1] or p[2]
        else
            out[#out + 1] = p
        end
    end
    return table.concat(out)
end

function ns.translateSpellDesc(text)
    local plain = text:gsub("\r\n", "\n"):gsub("\r", "\n")
    local v = ns.SpellDescExact and ns.SpellDescExact[plain]
    if v then return v end
    local t = ns.SpellDescTemplates
    if not t or #plain < 12 then return nil end
    for len = 8, 0, -1 do
        local bucket = t[plain:sub(1, len)]
        if bucket then
            for _, entry in ipairs(bucket) do
                v = apply(entry, plain)
                if v then return v end
            end
        end
    end
end
