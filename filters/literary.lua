-- Presentation only: the .qmd files remain the authority for all book content.
local function italian(b)
  return b.t == 'Div' and b.classes:includes('italian')
end

local function spacing(b)
  if b.t == 'HorizontalRule' then return true end
  if b.t == 'Div' and b.classes:includes('hidden') then return true end
  if b.t == 'Para' or b.t == 'Plain' then
    if #b.content == 1 and b.content[1].t == 'Span' and b.content[1].classes:includes('quarto-markdown-envelope-contents') then return true end
    return pandoc.utils.stringify(b):match('^%s*$') ~= nil
  end
  return false
end

local function title(b)
  if b.t ~= 'Para' then return false end
  return (#b.content == 1 and b.content[1].t == 'Strong')
    or pandoc.utils.stringify(b):match('^%*%*%*$') ~= nil
end

-- Retain the original LineBreak nodes and inline formatting. Each visual line
-- gets a span so browser wrapping can have a hanging indent of its own.
local function stanza(b)
  if b.t ~= 'Para' and b.t ~= 'Plain' then return b end
  local output, line = pandoc.Inlines({}), pandoc.Inlines({})
  for _, inline in ipairs(b.content) do
    if inline.t == 'LineBreak' then
      output:insert(pandoc.Span(line, pandoc.Attr('', {'verse'})))
      output:insert(inline)
      line = pandoc.Inlines({})
    else
      line:insert(inline)
    end
  end
  if #line > 0 then output:insert(pandoc.Span(line, pandoc.Attr('', {'verse'}))) end
  return pandoc.Div({pandoc.Plain(output)}, pandoc.Attr('', {'stanza'}))
end

local function language(blocks, lang, poem_index)
  local output = pandoc.Blocks({})
  local first = true
  for _, b in ipairs(blocks) do
    if spacing(b) then
      -- Preserve explicit source spacing nodes without doubling layout margins.
      output:insert(pandoc.Div({b}, pandoc.Attr('', {'source-spacing'})))
    elseif first and title(b) then
      output:insert(pandoc.Header(3, b.content, pandoc.Attr('poem-'..poem_index..'-'..lang..'-title')))
      first = false
    else
      output:insert(stanza(b))
      first = false
    end
  end
  return pandoc.Div(output, pandoc.Attr('', {'language', lang == 'it' and 'italian' or 'russian'}, {lang=lang}))
end

local function signature(blocks)
  local tokens = {}
  pandoc.Pandoc(blocks):walk({
    Str = function(x) tokens[#tokens+1] = 'S:'..x.text end,
    Code = function(x) tokens[#tokens+1] = 'C:'..x.text end,
    LineBreak = function() tokens[#tokens+1] = 'BR' end,
    SoftBreak = function() tokens[#tokens+1] = 'SOFT' end,
    RawInline = function(x) tokens[#tokens+1] = 'R:'..x.text end,
    RawBlock = function(x) tokens[#tokens+1] = 'RB:'..x.text end,
  })
  return table.concat(tokens, '\n')
end

function Pandoc(doc)
  -- Poet chapters all begin with their original biographical blockquote.
  if #doc.blocks == 0 or doc.blocks[1].t ~= 'BlockQuote' then
    -- Add navigation after the Home introduction without editing its source text.
    if pandoc.path.filename(quarto.doc.input_file) == 'index.qmd' then
      doc.blocks:insert(pandoc.Div({
        pandoc.Para({pandoc.Link('Читать', 'Говони.html')})
      }, pandoc.Attr('', {'home-reading-action'})))
    end
    return doc
  end
  local before = signature(doc.blocks)
  local intro = pandoc.Div(doc.blocks[1].content, pandoc.Attr('', {'bio'}))
  local output = pandoc.Blocks({pandoc.Div({intro}, pandoc.Attr('', {'chapter-head'}))})
  local poems, pending, index = pandoc.Blocks({}), pandoc.Blocks({}), 0
  local function flush(original)
    local meaningful = false
    for _, b in ipairs(pending) do if not spacing(b) then meaningful = true end end
    if not meaningful and not original then
      for _, b in ipairs(pending) do poems:insert(pandoc.Div({b}, pandoc.Attr('', {'source-spacing'}))) end
      pending = pandoc.Blocks({})
      return
    end
    if not original and pandoc.utils.stringify(pandoc.Div(pending)):match('^%s*Из сборника') then
      poems:insert(pandoc.Div(pending, pandoc.Attr('', {'collection-note'})))
      pending = pandoc.Blocks({})
      return
    end
    index = index + 1
    local versions = pandoc.Blocks({language(pending, 'ru', index)})
    if original then versions:insert(language(original.content, 'it', index)) end
    local attrs = pandoc.Attr('poem-'..index, {'poem'}, {['data-paired']=tostring(original ~= nil)})
    poems:insert(pandoc.Div({pandoc.Div(versions, pandoc.Attr('', {'bilingual'}))}, attrs))
    pending = pandoc.Blocks({})
  end
  for i=2,#doc.blocks do
    local b = doc.blocks[i]
    if italian(b) then
      flush(b)
    elseif b.t == 'HorizontalRule' then
      flush(nil)
      poems:insert(pandoc.Div({b}, pandoc.Attr('', {'source-spacing'})))
    elseif title(b) and #pending > 0 then
      -- A new title after verse, without a source version, starts another poem.
      local verse = false
      for _, p in ipairs(pending) do if not spacing(p) and not title(p) then verse = true end end
      if verse then flush(nil) end
      pending:insert(b)
    else
      pending:insert(b)
    end
  end
  flush(nil)
  output:insert(pandoc.Div(poems, pandoc.Attr('', {'reading'}, {['data-mode']='parallel'})))
  if before ~= signature(output) then error('Literary layout changed source text or line breaks') end
  doc.blocks = output
  return doc
end
