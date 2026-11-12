# Fontsource (fonts)

Sources: [Fontsource API](https://fontsource.org/docs/api) (`api.fontsource.org/v1/fonts` and `/v1/fonts/{id}`), files from `cdn.jsdelivr.net/fontsource/fonts/{id}@{version}/`. Read 2026-11-12.

Keyless catalogue of open-source web fonts. The module reads the font list, keeps only fonts whose licence passes the policy (OFL-1.1, Apache-2.0, MIT, CC0; the Ubuntu Font Licence is skipped), matches the query against id, family and category, and returns at most four fonts. Each record lists weight 400 and 700 files as TTF and WOFF2 (at most eight), with the exact npm version in the URL so the files are pinned.

Polish: a query containing "polish", "polski" or similar requires the `latin-ext` subset and returns both the `latin` and `latin-ext` files, because Polish diacritics are in `latin-ext`. A font without `latin-ext` is not returned for such a query.

OFL fonts may be used and embedded commercially; they may not be sold on their own and a modified font may not keep the reserved name. Fontshare is not used (its terms forbid subsetting and conversion).

Fonts are checked on download: WOFF/WOFF2 by header length and table count, TTF/OTF by loading with FreeType (Pillow). The runtime does not install fonts; installing is a separate user decision.

Live check 2026-11-12: "oxanium polish" returned an OFL-1.1 record with 8 variants; the TTF decoded (family Oxanium), the WOFF2 header validated. ChatGPT Work: NOT_RUN.
