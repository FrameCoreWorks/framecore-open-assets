"""Regression cases from the 2026-10-28 Work validation; no network."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import core
import runtime

class Policies(unittest.TestCase):
    def test_proof_cannot_move_to_another_provider_or_category(self):
        with tempfile.TemporaryDirectory() as root:
            data={'utc':core.utc(),'fingerprint':runtime.fingerprint(),'host':'chatgpt_work',
                  'provider':'commons','category':'photos','status':'PASS'}
            signed=json.dumps(runtime.seal(data,root))
            for provider,category,expected in [('commons','photos',True),('met','graphics',False),('commons','video',False)]:
                runtime.proof_path(root,'chatgpt_work',provider,category).write_text(signed)
                self.assertEqual(runtime.proof_valid(root,'chatgpt_work',provider,category),expected)

    def test_provider_interval_above_five_seconds_is_honoured(self):
        with tempfile.TemporaryDirectory() as root:
            c=core.Client('loc',root,'chatgpt_work','test')
            (Path(root)/'loc.last').write_text('100')
            with patch('time.time',return_value=100),patch('time.sleep') as sleep,c.serial():pass
            sleep.assert_called_once_with(6.1)

    def test_finna_locale_suffix_does_not_change_rights(self):
        self.assertEqual(core.license_policy(core.CC0+'deed.fi'),('CC0','eligible'))
        self.assertEqual(core.license_policy('https://creativecommons.org/licenses/by-nc/4.0/deed.fi')[1],'blocked')

    def test_loc_rejects_negated_dedication_and_clippings(self):
        module=importlib.import_module('providers.loc')
        row={'id':'https://www.loc.gov/item/123/','original_format':['photo, print, drawing'],
             'image_url':['https://tile.loc.gov/test.jpg'],'title':'Portrait','contributor':['Gottlieb']}
        for text,count in [('This is not in the public domain; permission is required.',0),
                           ('Mr. Gottlieb has dedicated these works to the public domain, but rights of privacy and publicity may apply.',1)]:
            c=Mock();c.json.side_effect=[{'results':[row]},{'item':{'rights_advisory':[text]}}]
            self.assertEqual(len(module.search(c,'portrait','photos',1)),count)
        c=Mock();c.json.return_value={'results':[{**row,'original_format':['manuscript']}]}
        self.assertEqual(module.search(c,'jazz','photos',1),[])
        self.assertEqual(c.json.call_count,1)

    def test_rijks_does_not_apply_metadata_cc0_to_image_or_invent_by_credit(self):
        module=importlib.import_module('providers.rijks')
        for licence,expected in [(core.PDM,'eligible'),('https://creativecommons.org/licenses/by/4.0/','blocked'),('', 'blocked')]:
            c=Mock();c.json.side_effect=[{'orderedItems':[{'id':'https://id.rijksmuseum.nl/1'}]},
                {'id':'https://id.rijksmuseum.nl/1','referred_to_by':[{'content':core.CC0}],
                 'subject_of':[{'digitally_carried_by':[{'access_point':[{'id':'https://iiif.micr.io/1/full/max/0/default.jpg'}],
                                                        'referred_to_by':[{'content':licence}]}]}]}]
            self.assertEqual(module.search(c,'work','graphics',1)[0]['rights_status'],expected)

    def test_nasa_audio_lists_small_renditions_first_and_keeps_review(self):
        # Owner decision 2026-11-11 (research DR-04): NASA audio in the existing adapter, review_nasa kept.
        self.assertEqual(core.REGISTRY['nasa']['categories'], ['photos', 'video', 'audio'])
        fixtures=Path(__file__).parent/'fixtures'
        c=Mock();c.policy=core.REGISTRY['nasa']
        c.json.side_effect=[json.loads((fixtures/'nasa-audio-search.json').read_text()),json.loads((fixtures/'nasa-audio-manifest.json').read_text())]
        items=runtime.search_one(c,'apollo','audio',5)
        self.assertEqual(len(items),1)
        self.assertIn('media_type=audio',c.json.call_args_list[0].args[0])
        self.assertIn('page_size=3',c.json.call_args_list[0].args[0])
        names=[v['label'] for v in items[0]['variants']]
        self.assertEqual(names[0],'Ep433_Callsign White Flight~64k.m4a')
        self.assertEqual(len(names),len(set(names)),'duplicate manifest rows are listed once')
        self.assertNotIn('metadata.json',names)
        self.assertEqual(items[0]['rights_status'],'review_nasa')

    def test_audio_cannot_be_delivered_as_a_photo(self):
        with tempfile.TemporaryDirectory() as root:
            c=core.Client('met',Path(root)/'state','chatgpt_work','test')
            c.get=Mock(return_value=(b'fake',{'content-type':'audio/wav'}))
            item=core.asset('met','1','work','artist','https://metmuseum.org/',[core.variant('https://images.metmuseum.org/a.jpg')],core.CC0,'photos')
            with patch('core.decode',return_value={'kind':'audio'}),self.assertRaises(core.Refused) as error:
                core.download(c,item,Path(root)/'photo.jpg')
            self.assertEqual(error.exception.kind,'wrong_media_type')
            self.assertFalse((Path(root)/'photo.jpg').exists())

    def test_incompetech_matches_terms_skips_oversized_tracks_and_credits_kevin_macleod(self):
        # 2026-11-06: 30 catalogue tracks run over 13 minutes (up to 141 MB) and exceed the 32 MiB cap.
        fixture=json.loads((Path(__file__).parent/'fixtures'/'incompetech-search.json').read_text())
        c=Mock();c.policy=core.REGISTRY['incompetech'];c.json.return_value=fixture
        items=runtime.search_one(c,'calm piano','music',5)
        self.assertEqual([i['title'] for i in items],['Grand Dark Waltz Trio Vivace'])
        item=items[0]
        self.assertEqual((item['license'],item['rights_status']),('CC BY 4.0','eligible'))
        self.assertEqual(item['creator'],'Kevin MacLeod (incompetech.com)')
        self.assertTrue(item['source_page'].endswith('isrc=USUAN2100027'))
        self.assertEqual(item['variants'][0]['url'],
                         'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Grand%20Dark%20Waltz%20Trio%20Vivace.mp3')
        self.assertEqual(item['variants'][0]['bpm'],'140')
        self.assertTrue(any('Credit required' in w for w in item['warnings']))
        self.assertEqual(runtime.search_one(c,'relaxation','music',5),[])
        self.assertEqual(len(runtime.search_one(c,'','music',5)),2)
        with self.assertRaises(core.Refused):
            runtime.search_one(c,'piano','sfx',1)

    # 0.7.0 providers (research 2026-11-12). Fixtures are trimmed live responses; no network.
    @staticmethod
    def fixture(name):
        return json.loads((Path(__file__).parent/'fixtures'/name).read_text())

    def test_archive_returns_only_open_licence_whitelisted_items_and_small_mp3s(self):
        c=Mock();c.policy=core.REGISTRY['archive']
        c.json.side_effect=[self.fixture('archive-search.json'),self.fixture('archive-metadata.json'),
                            self.fixture('archive-metadata-nc.json')]
        items=runtime.search_one(c,'goldberg','music',5)
        self.assertEqual([i['id'] for i in items],['OpenGoldbergVariations'],'a BY-NC item is dropped even if the search returned it')
        item=items[0]
        self.assertEqual((item['license'],item['rights_status']),('CC0','eligible'))
        self.assertTrue(all(v['url'].startswith('https://archive.org/download/OpenGoldbergVariations/') for v in item['variants']))
        self.assertTrue(all(v['label'].endswith('.mp3') and v['bytes']<=core.MAX_FILE for v in item['variants']))
        query=c.json.call_args_list[0].args[0]
        self.assertIn('collection%3A%28musopen+OR+netlabels%29',query,'music is bound to reviewed collections')
        self.assertIn('licenseurl',query)
        self.assertTrue(any('declared by the uploader' in w for w in item['warnings']))
        c.json.side_effect=[{'response':{'docs':[]}}]
        runtime.search_one(c,'rain','sfx',2)
        self.assertIn('radio-aporee-maps',c.json.call_args.args[0])
        c.json.side_effect=[{'response':{'docs':[]}}]
        runtime.search_one(c,'x','video',2)
        self.assertIn('mediatype%3Amovies',c.json.call_args.args[0])
        with self.assertRaises(core.Refused):
            runtime.search_one(c,'x','photos',1)

    def test_jukebox_keeps_only_recordings_before_1923_behind_the_review_gate(self):
        c=Mock();c.policy=core.REGISTRY['jukebox'];c.json.return_value=self.fixture('jukebox-search.json')
        items=runtime.search_one(c,'waltz','music',5)
        self.assertEqual(len(items),2,'the 1931 row is skipped')
        self.assertTrue(all(i['rights_status']=='review_jurisdiction' for i in items))
        self.assertTrue(all(i['variants'][0]['url'].startswith('https://tile.loc.gov/') for i in items))
        self.assertTrue(any('composition' in w for w in items[0]['warnings']))
        with tempfile.TemporaryDirectory() as root:
            client=core.Client('jukebox',Path(root)/'state','claude_code','test')
            with self.assertRaises(core.Refused) as error:
                core.download(client,items[0],Path(root)/'a.mp3')
            self.assertEqual(error.exception.kind,'rights_blocked','a review note is required before download')

    def test_nasasvs_uses_description_sizes_and_skips_oversized_movies(self):
        c=Mock();c.policy=core.REGISTRY['nasasvs']
        c.json.side_effect=[self.fixture('nasasvs-search.json'),self.fixture('nasasvs-page.json')]
        items=runtime.search_one(c,'hurricane','photos',3)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]['rights_status'],'review_nasa')
        self.assertTrue(items[0]['variants'][0]['url'].startswith('https://svs.gsfc.nasa.gov/'))
        self.assertNotIn('bytes',items[0]['variants'][0],'sizes in the description are approximate')
        c.json.side_effect=[self.fixture('nasasvs-search.json'),self.fixture('nasasvs-page.json')]
        self.assertEqual(runtime.search_one(c,'hurricane','video',3),[],'the 185 MB and 77 MB movies exceed the 32 MiB cap')

    def test_metasound_matches_ucs_names_and_carries_the_required_credit(self):
        c=Mock();c.policy=core.REGISTRY['metasound'];c.json.return_value=self.fixture('metasound-manifest.json')
        items=runtime.search_one(c,'ui error','sfx',5)
        self.assertTrue(items and all(i['id'].startswith('UIAlert') for i in items))
        self.assertEqual((items[0]['license'],items[0]['rights_status']),('CC BY 4.0','eligible'))
        self.assertEqual(items[0]['creator'],'Oculus VR, LLC')
        self.assertTrue(items[0]['variants'][0]['url'].endswith('.ogg'))
        self.assertIn('251c0be57d5d1b3242b91f53e0cde62ab1cb42d9',items[0]['variants'][0]['url'],'URLs are pinned to the reviewed commit')
        self.assertTrue(any('Credit required' in w and 'CC BY 4.0' in w for w in items[0]['warnings']))
        self.assertEqual(runtime.search_one(c,'dragon','sfx',5),[])

    def test_uisfx_reads_cues_from_the_taxonomy_and_orders_packs_by_the_query(self):
        c=Mock();c.policy=core.REGISTRY['uisfx']
        c.get.return_value=((Path(__file__).parent/'fixtures'/'uisfx-taxonomy.md').read_bytes(),{})
        items=runtime.search_one(c,'glass toggle','sfx',5)
        self.assertEqual({i['id'] for i in items}>={'toggle-on','toggle-off'},True)
        item=items[0]
        self.assertEqual((item['license'],item['rights_status']),('CC0','eligible'))
        self.assertTrue(item['variants'][0]['label'].startswith('glass/'))
        self.assertEqual(len(item['variants']),12)
        self.assertIn('9950fe66f993a6660dab9c2651dcbcd899ffd83b',item['variants'][0]['url'])

    # 0.8.0: icons and fonts (owner decision 2026-11-12). Fixtures are trimmed live responses; no network.
    def test_software_licences_are_accepted_only_with_an_author_and_gpl_nc_stay_blocked(self):
        self.assertEqual(core.license_policy('MIT'),('MIT','eligible'))
        self.assertEqual(core.license_policy('Apache-2.0'),('Apache-2.0','eligible'))
        self.assertEqual(core.license_policy('OFL-1.1'),('OFL-1.1','eligible'))
        self.assertEqual(core.license_policy('CC-BY-4.0'),('CC BY 4.0','eligible'))
        self.assertEqual(core.license_policy('CC0-1.0'),('CC0','eligible'))
        for bad in ('GPL-2.0-only','CC-BY-NC-SA-4.0','UFL-1.0','Unlicense',''):
            self.assertEqual(core.license_policy(bad)[1],'blocked',bad)
        ok=core.asset('x','1','t','Author','https://x/',[core.variant('https://x/a')],'','icons',license_id='MIT')
        self.assertEqual(ok['rights_status'],'eligible')
        self.assertEqual(core.asset('x','1','t','','https://x/',[],'','icons',license_id='MIT')['rights_status'],'blocked')

    def test_iconify_drops_gpl_nc_and_remix_sets_and_gates_logos(self):
        c=Mock();c.policy=core.REGISTRY['iconify'];c.json.return_value=self.fixture('iconify-search.json')
        items=runtime.search_one(c,'home','icons',5)
        ids=[i['id'] for i in items]
        for dropped in ('gridicons:home','cbi:home','ri:home-line'):
            self.assertNotIn(dropped,ids)
        self.assertEqual(len(set(i['id'].split(':')[0] for i in items)),len(items),'one icon per set first')
        self.assertTrue(all(i['rights_status'] in ('eligible','review_jurisdiction') for i in items))
        c.json.return_value={**self.fixture('iconify-search.json'),'icons':['simple-icons:github']}
        logo=runtime.search_one(c,'github','icons',5)[0]
        self.assertEqual(logo['rights_status'],'review_jurisdiction')
        self.assertTrue(any('trademark' in w for w in logo['warnings']))
        c.json.return_value={**self.fixture('iconify-search.json'),'icons':['twemoji:house']}
        emoji=runtime.search_one(c,'house','icons',5)[0]
        self.assertEqual((emoji['license'],emoji['creator']),('CC BY 4.0','Twitter'))
        self.assertTrue(any('Credit the author' in w for w in emoji['warnings']))
        self.assertEqual(items[0]['variants'][0]['url'].rsplit('/',2)[-2:],[items[0]['id'].split(':')[0],items[0]['id'].split(':')[1]+'.svg'])

    def test_fontsource_skips_non_open_licences_and_polish_needs_latin_and_latin_ext(self):
        c=Mock();c.policy=core.REGISTRY['fontsource']
        c.json.side_effect=[self.fixture('fontsource-list.json'),self.fixture('fontsource-oxanium.json')]
        items=runtime.search_one(c,'oxanium polish','fonts',3)
        self.assertEqual([i['id'] for i in items],['oxanium'])
        labels=[v['label'] for v in items[0]['variants']]
        self.assertTrue(any(' latin ttf' in l for l in labels) and any(' latin-ext ttf' in l for l in labels))
        self.assertTrue(all('@5.3.0' in v['url'] for v in items[0]['variants']),'URLs carry the exact npm version')
        self.assertEqual((items[0]['license'],items[0]['rights_status']),('OFL-1.1','eligible'))
        c.json.side_effect=[self.fixture('fontsource-list.json')]
        self.assertEqual(runtime.search_one(c,'ubuntu','fonts',3),[],'Ubuntu Font Licence is not accepted')
        c.json.side_effect=[self.fixture('fontsource-list.json')]
        self.assertEqual(runtime.search_one(c,'no latin polish','fonts',3),[],'a font without latin-ext cannot serve Polish')

    def test_svg_decoder_refuses_active_content_and_font_decoder_checks_headers(self):
        good=b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'
        bad={'script':b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
             'handler':b'<svg xmlns="http://www.w3.org/2000/svg" onload="x()"></svg>',
             'external':b'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><use xlink:href="https://evil/x.svg#a"/></svg>',
             'entity':b'<!DOCTYPE svg [<!ENTITY a "b">]><svg xmlns="http://www.w3.org/2000/svg"/>',
             'css':b'<svg xmlns="http://www.w3.org/2000/svg"><style>@import url(https://evil/x.css);</style></svg>',
             'foreign':b'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject><p/></foreignObject></svg>'}
        with tempfile.TemporaryDirectory() as root:
            f=Path(root)/'a.svg';f.write_bytes(good)
            self.assertEqual(core.decode(f)['kind'],'vector')
            for name,body in bad.items():
                f.write_bytes(body)
                with self.assertRaises(core.Refused,msg=name):core.decode(f)
            f.write_bytes(b'wOF2'+b'\x00\x01\x00\x00'+(99).to_bytes(4,'big')+(3).to_bytes(2,'big')+b'\x00'*20)
            with self.assertRaises(core.Refused):core.decode(f)
            f.write_bytes(b'wOF2'+b'\x00\x01\x00\x00'+(24).to_bytes(4,'big')+(3).to_bytes(2,'big')+b'\x00'*10)
            self.assertEqual(core.decode(f)['kind'],'font')

    def test_icons_and_fonts_cannot_be_delivered_as_other_media(self):
        with tempfile.TemporaryDirectory() as root:
            c=core.Client('iconify',Path(root)/'state','claude_code','test')
            c.get=Mock(return_value=(b'x',{'content-type':'image/svg+xml'}))
            item=core.asset('iconify','mdi:home','t','Author','https://x/',[core.variant('https://api.iconify.design/mdi/home.svg')],'','icons',license_id='MIT')
            with patch('core.decode',return_value={'kind':'font'}),self.assertRaises(core.Refused) as error:
                core.download(c,item,Path(root)/'home.svg')
            self.assertEqual(error.exception.kind,'wrong_media_type')

if __name__=='__main__':unittest.main()
