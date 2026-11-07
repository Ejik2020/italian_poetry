-- Search metadata only: visible chapter headings and literary blocks stay intact.
function Meta(meta)
  -- Keep descriptions in the document head, never in the visible title block.
  meta['hide-description'] = true
  local filename = pandoc.path.filename(quarto.doc.input_file)
  local title = pandoc.utils.stringify(meta.title or '')
  if filename == 'index.qmd' then
    meta.pagetitle = 'Итальянская поэзия — переводы Александра Фейгина'
    meta.description = 'Современная итальянская поэзия в переводах Александра Фейгина. Alexander (Alex) Feigin: Italian poetry translated into Russian, with Italian originals.'
    meta['canonical-url'] = 'https://www.alexfeigin.com/'
  elseif filename == 'book.qmd' then
    meta.pagetitle = 'Купить книгу — Александр Фейгин'
    meta.description = 'Купить книгу итальянской поэзии в русских переводах Александра Фейгина. Italian poetry in Russian translation by Alexander (Alex) Feigin.'
  else
    meta.pagetitle = title..' — переводы Александра Фейгина'
    meta.description = title..': стихи на итальянском и переводы на русский Александра Фейгина. Italian poetry translated into Russian by Alexander (Alex) Feigin.'
  end
  return meta
end
