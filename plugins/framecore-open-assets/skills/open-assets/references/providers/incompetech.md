# Incompetech (Kevin MacLeod)

Sources: [FAQ with credit format and Content ID notes](https://incompetech.com/music/royalty-free/faq.html), [licence options](https://incompetech.com/music/royalty-free/licenses/), [catalogue JSON](https://incompetech.com/music/royalty-free/pieces.json), [robots.txt](https://incompetech.com/robots.txt). Read 2026-11-06.

All catalogue music is by Kevin MacLeod and offered free under **CC BY 4.0** with the credit "Title Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0 https://creativecommons.org/licenses/by/4.0/". Where attribution is impossible the site sells a separate Standard License; that paid route is outside this module. The licence is stated site-wide, not in each file, so keep the source page and credit with every download. Third parties can still raise platform Content ID claims; the credit and licence are the dispute evidence.

No account or key. `pieces.json` (1,443 pieces on 2026-11-06, about 0.9 MB, `no-store`) gives title, duration, BPM, feel, instruments, ISRC and the MP3 file name; files are served from `/music/royalty-free/mp3-royaltyfree/` as about 320 kbit/s MP3 with `application/octet-stream`. `robots.txt` disallows only `/web-bin/`, `/users/`, `/stats/` and `/home/`. No numeric rate limit or automation clause was found; the module reads the catalogue once per search and downloads only the single file the user picks, two seconds apart. The module matches query words against title, feel, description and instruments, and skips the 30 pieces whose length exceeds the 32 MiB cap at that bitrate (the longest, 58:54, is 141 MB). The source page is the catalogue page for the piece's ISRC.

Live check 2026-11-06 in a Claude Code cloud container (host `claude_code`): search "calm piano" returned eligible CC BY 4.0 records; "Grand Dark Waltz Trio Vivace" downloaded (3,449,364 bytes, SHA-256 `b80e14e0…a38f`) and fully decoded as 172.4 s MP3. ChatGPT Work search/download: NOT_RUN.

Implementation note: the provider register records the current policy gate. Historical HTTP tests do not prove runtime or host readiness.
