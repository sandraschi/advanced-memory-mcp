-- Lua filter to insert a native Word TOC field
-- This creates a proper Word TOC that's clickable without the "external files" popup
--
-- Usage: pandoc input.md -o output.docx --lua-filter=word-toc.lua
--
-- The TOC is inserted before the first H1 heading.
-- Word will show "Update Table" prompt (normal) - click Yes to populate.

local defined = false

function Header(el)
  -- Insert TOC before the first H1 heading (after title)
  if el.level == 1 and not defined then
    defined = true
    local toc = pandoc.RawBlock('openxml', [[
<w:sdt>
  <w:sdtPr>
    <w:docPartObj>
      <w:docPartGallery w:val="Table of Contents"/>
      <w:docPartUnique/>
    </w:docPartObj>
  </w:sdtPr>
  <w:sdtContent>
    <w:p>
      <w:pPr>
        <w:pStyle w:val="TOCHeading"/>
      </w:pPr>
      <w:r>
        <w:t>Table of Contents</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:r>
        <w:fldChar w:fldCharType="begin"/>
      </w:r>
      <w:r>
        <w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>
      </w:r>
      <w:r>
        <w:fldChar w:fldCharType="separate"/>
      </w:r>
      <w:r>
        <w:fldChar w:fldCharType="end"/>
      </w:r>
    </w:p>
  </w:sdtContent>
</w:sdt>
]])
    return {toc, el}
  end
  return el
end
