# Iconify (icons)

Sources: [API](https://iconify.design/docs/api/), [search](https://iconify.design/docs/api/search.html) and the `collections` metadata returned by `api.iconify.design`. Read 2026-11-12.

Keyless icon API over about 200 open-source icon sets. Search returns icon ids (`prefix:name`) plus per-set metadata with author and an SPDX licence. The module takes the licence from that metadata, never from the icon name, and delivers one static SVG per icon at `https://api.iconify.design/{prefix}/{icon}.svg`.

Accepted: MIT, ISC, Apache-2.0, BSD, CC0, CC BY 4.0 (credit the set author; the record carries creator and licence). Blocked: GPL and every NC licence (for example `gridicons`, `wordpress`, `dashicons`, `gala`, `icomoon-free`, `et`, `cbi`, `ps`), sets without a named author, and Remix Icon (`ri`, `remixicon`; custom licence since January 2026). Sets in the Logos category (brand marks such as `simple-icons`) get `review_jurisdiction` and a trademark warning: the icon is licensed, the logo it depicts is still a trademark.

Results are diversified by set (one icon per set first, at most five). Every downloaded SVG is decoded by a static-only check: no scripts, event handlers, DOCTYPE or entities, foreignObject, external references or external CSS.

Live check 2026-11-12: "home" and "github" returned MIT, Apache-2.0, CC0 and CC BY records; one SVG downloaded and decoded as vector. ChatGPT Work: NOT_RUN.
