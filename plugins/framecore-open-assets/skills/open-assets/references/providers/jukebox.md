# Library of Congress: National Jukebox (before 1923)

Sources: [rights and access](https://www.loc.gov/collections/national-jukebox/about-this-collection/rights-and-access/), [collection search](https://www.loc.gov/collections/national-jukebox/?fo=json). Read 2026-11-12.

The collection page states that, under the Music Modernization Act, recordings published before 1923 entered the US public domain on 1 January 2022 and are free to use and reuse; later recordings are protected. The module keeps only sound recordings dated 1922 or earlier. That statement covers the recording in the United States. It does not cover the musical composition (a composer who died after 1955 can still be protected in the EU), performers' rights outside the US, privacy or publicity rights, or offensive period content, and the Library says the user must assess the legality of use. Every record therefore carries `review_jurisdiction` and needs a written review note before download. Credit line requested: Library of Congress, National Jukebox.

No account or key. One `?fo=json&q=...&c=8` call per search (larger pages timed out); MP3 files come from `tile.loc.gov`. Records carry no byte count, so the download is bounded by the 32 MiB cap at request time. The National Screening Room was tested too and left out: its MP4 copies run about 1 MB per second, so almost no film fits the cap.

Live check 2026-11-12: "waltz" returned eligible-after-review records; one 181-second recording downloaded (technical test) and fully decoded. ChatGPT Work: NOT_RUN.
