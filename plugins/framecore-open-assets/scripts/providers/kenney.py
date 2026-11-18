"""Kenney audio packs (CC0) through pinned GitHub mirrors: six packs, 467 sound effects.

Kenney (kenney.nl) publishes these packs under CC0 1.0. kenney.nl itself disallows AI agents and every crawler under
/assets/ in its robots.txt, so this module never contacts it. It reads byte copies that Godot asset ports published on
GitHub, each pinned to the reviewed commit and each carrying Kenney's CC0 licence file. The file names are embedded
below (read from the pinned trees on 2026-11-18), so a search makes no request; a download reads one file from
raw.githubusercontent.com.
"""
import re
import urllib.parse

from core import asset, variant, CC0

KENNEY = 'Kenney (kenney.nl)'
PACKS = (
    ('ui-audio', 'UI Audio', 'Calinou/kenney-ui-audio',
     '8c3d81b9159d058c444f89d12d518276b0b09345', 'addons/kenney_ui_audio',
     'click1.wav click2.wav click3.wav click4.wav click5.wav mouseclick1.wav mouserelease1.wav '
     'rollover1.wav rollover2.wav rollover3.wav rollover4.wav rollover5.wav rollover6.wav switch1.wav '
     'switch10.wav switch11.wav switch12.wav switch13.wav switch14.wav switch15.wav switch16.wav '
     'switch17.wav switch18.wav switch19.wav switch2.wav switch20.wav switch21.wav switch22.wav '
     'switch23.wav switch24.wav switch25.wav switch26.wav switch27.wav switch28.wav switch29.wav '
     'switch3.wav switch30.wav switch31.wav switch32.wav switch33.wav switch34.wav switch35.wav '
     'switch36.wav switch37.wav switch38.wav switch4.wav switch5.wav switch6.wav switch7.wav switch8.wav '
     'switch9.wav'),
    ('interface-sounds', 'Interface Sounds', 'Calinou/kenney-interface-sounds',
     '4596a49eaf5a533948d49a47467f606bcdea70ff', 'addons/kenney_interface_sounds',
     'back_001.wav back_002.wav back_003.wav back_004.wav bong_001.wav click_001.wav click_002.wav '
     'click_003.wav click_004.wav click_005.wav close_001.wav close_002.wav close_003.wav close_004.wav '
     'confirmation_001.wav confirmation_002.wav confirmation_003.wav confirmation_004.wav drop_001.wav '
     'drop_002.wav drop_003.wav drop_004.wav error_001.wav error_002.wav error_003.wav error_004.wav '
     'error_005.wav error_006.wav error_007.wav error_008.wav glass_001.wav glass_002.wav glass_003.wav '
     'glass_004.wav glass_005.wav glass_006.wav glitch_001.wav glitch_002.wav glitch_003.wav '
     'glitch_004.wav maximize_001.wav maximize_002.wav maximize_003.wav maximize_004.wav maximize_005.wav '
     'maximize_006.wav maximize_007.wav maximize_008.wav maximize_009.wav minimize_001.wav '
     'minimize_002.wav minimize_003.wav minimize_004.wav minimize_005.wav minimize_006.wav '
     'minimize_007.wav minimize_008.wav minimize_009.wav open_001.wav open_002.wav open_003.wav '
     'open_004.wav pluck_001.wav pluck_002.wav question_001.wav question_002.wav question_003.wav '
     'question_004.wav scratch_001.wav scratch_002.wav scratch_003.wav scratch_004.wav scratch_005.wav '
     'scroll_001.wav scroll_002.wav scroll_003.wav scroll_004.wav scroll_005.wav select_001.wav '
     'select_002.wav select_003.wav select_004.wav select_005.wav select_006.wav select_007.wav '
     'select_008.wav switch_001.wav switch_002.wav switch_003.wav switch_004.wav switch_005.wav '
     'switch_006.wav switch_007.wav tick_001.wav tick_002.wav tick_004.wav toggle_001.wav toggle_002.wav '
     'toggle_003.wav toggle_004.wav'),
    ('impact-sounds', 'Impact Sounds', 'Boyquotes/kenney-impact-sounds-for-godot',
     '999dd1684873f8b020a3aa5b26e713da21688924', 'addons/kenney impact sounds',
     'footstep_carpet_000.ogg footstep_carpet_001.ogg footstep_carpet_002.ogg footstep_carpet_003.ogg '
     'footstep_carpet_004.ogg footstep_concrete_000.ogg footstep_concrete_001.ogg '
     'footstep_concrete_002.ogg footstep_concrete_003.ogg footstep_concrete_004.ogg footstep_grass_000.ogg '
     'footstep_grass_001.ogg footstep_grass_002.ogg footstep_grass_003.ogg footstep_grass_004.ogg '
     'footstep_snow_000.ogg footstep_snow_001.ogg footstep_snow_002.ogg footstep_snow_003.ogg '
     'footstep_snow_004.ogg footstep_wood_000.ogg footstep_wood_001.ogg footstep_wood_002.ogg '
     'footstep_wood_003.ogg footstep_wood_004.ogg impact_bell_heavy_000.ogg impact_bell_heavy_001.ogg '
     'impact_bell_heavy_002.ogg impact_bell_heavy_003.ogg impact_bell_heavy_004.ogg '
     'impact_generic_light_000.ogg impact_generic_light_001.ogg impact_generic_light_002.ogg '
     'impact_generic_light_003.ogg impact_generic_light_004.ogg impact_glass_heavy_000.ogg '
     'impact_glass_heavy_001.ogg impact_glass_heavy_002.ogg impact_glass_heavy_003.ogg '
     'impact_glass_heavy_004.ogg impact_glass_light_000.ogg impact_glass_light_001.ogg '
     'impact_glass_light_002.ogg impact_glass_light_003.ogg impact_glass_light_004.ogg '
     'impact_glass_medium_000.ogg impact_glass_medium_001.ogg impact_glass_medium_002.ogg '
     'impact_glass_medium_003.ogg impact_glass_medium_004.ogg impact_metal_heavy_000.ogg '
     'impact_metal_heavy_001.ogg impact_metal_heavy_002.ogg impact_metal_heavy_003.ogg '
     'impact_metal_heavy_004.ogg impact_metal_light_000.ogg impact_metal_light_001.ogg '
     'impact_metal_light_002.ogg impact_metal_light_003.ogg impact_metal_light_004.ogg '
     'impact_metal_medium_000.ogg impact_metal_medium_001.ogg impact_metal_medium_002.ogg '
     'impact_metal_medium_003.ogg impact_metal_medium_004.ogg impact_mining_000.ogg impact_mining_001.ogg '
     'impact_mining_002.ogg impact_mining_003.ogg impact_mining_004.ogg impact_plank_medium_000.ogg '
     'impact_plank_medium_001.ogg impact_plank_medium_002.ogg impact_plank_medium_003.ogg '
     'impact_plank_medium_004.ogg impact_plate_heavy_000.ogg impact_plate_heavy_001.ogg '
     'impact_plate_heavy_002.ogg impact_plate_heavy_003.ogg impact_plate_heavy_004.ogg '
     'impact_plate_light_000.ogg impact_plate_light_001.ogg impact_plate_light_002.ogg '
     'impact_plate_light_003.ogg impact_plate_light_004.ogg impact_plate_medium_000.ogg '
     'impact_plate_medium_001.ogg impact_plate_medium_002.ogg impact_plate_medium_003.ogg '
     'impact_plate_medium_004.ogg impact_punch_heavy_000.ogg impact_punch_heavy_001.ogg '
     'impact_punch_heavy_002.ogg impact_punch_heavy_003.ogg impact_punch_heavy_004.ogg '
     'impact_punch_medium_000.ogg impact_punch_medium_001.ogg impact_punch_medium_002.ogg '
     'impact_punch_medium_003.ogg impact_punch_medium_004.ogg impact_soft_heavy_000.ogg '
     'impact_soft_heavy_001.ogg impact_soft_heavy_002.ogg impact_soft_heavy_003.ogg '
     'impact_soft_heavy_004.ogg impact_soft_medium_000.ogg impact_soft_medium_001.ogg '
     'impact_soft_medium_002.ogg impact_soft_medium_003.ogg impact_soft_medium_004.ogg '
     'impact_tin_medium_000.ogg impact_tin_medium_001.ogg impact_tin_medium_002.ogg '
     'impact_tin_medium_003.ogg impact_tin_medium_004.ogg impact_wood_heavy_000.ogg '
     'impact_wood_heavy_001.ogg impact_wood_heavy_002.ogg impact_wood_heavy_003.ogg '
     'impact_wood_heavy_004.ogg impact_wood_light_000.ogg impact_wood_light_001.ogg '
     'impact_wood_light_002.ogg impact_wood_light_003.ogg impact_wood_light_004.ogg '
     'impact_wood_medium_000.ogg impact_wood_medium_001.ogg impact_wood_medium_002.ogg '
     'impact_wood_medium_003.ogg impact_wood_medium_004.ogg'),
    ('sci-fi-sounds', 'Sci-Fi Sounds', 'Boyquotes/kenney-sci-fi-sounds-for-godot',
     'c094967fe930c57ddb376f67c75f8aa0296690b7', 'addons/kenney sci-fi sounds',
     'computer_noise_000.ogg computer_noise_001.ogg computer_noise_002.ogg computer_noise_003.ogg '
     'door_close_000.ogg door_close_001.ogg door_close_002.ogg door_open_000.ogg door_open_001.ogg '
     'door_open_002.ogg engine_circular_000.ogg engine_circular_001.ogg engine_circular_002.ogg '
     'engine_circular_003.ogg engine_circular_004.ogg explosion_crunch_000.ogg explosion_crunch_001.ogg '
     'explosion_crunch_002.ogg explosion_crunch_003.ogg explosion_crunch_004.ogg force_field_000.ogg '
     'force_field_001.ogg force_field_002.ogg force_field_003.ogg force_field_004.ogg impact_metal_000.ogg '
     'impact_metal_001.ogg impact_metal_002.ogg impact_metal_003.ogg impact_metal_004.ogg '
     'laser_large_000.ogg laser_large_001.ogg laser_large_002.ogg laser_large_003.ogg laser_large_004.ogg '
     'laser_retro_000.ogg laser_retro_001.ogg laser_retro_002.ogg laser_retro_003.ogg laser_retro_004.ogg '
     'laser_small_000.ogg laser_small_001.ogg laser_small_002.ogg laser_small_003.ogg laser_small_004.ogg '
     'low_frequency_explosion_000.ogg low_frequency_explosion_001.ogg slime_000.ogg slime_001.ogg '
     'space_engine_000.ogg space_engine_001.ogg space_engine_002.ogg space_engine_003.ogg '
     'space_engine_large_000.ogg space_engine_large_001.ogg space_engine_large_002.ogg '
     'space_engine_large_003.ogg space_engine_large_004.ogg space_engine_low_000.ogg '
     'space_engine_low_001.ogg space_engine_low_002.ogg space_engine_low_003.ogg space_engine_low_004.ogg '
     'space_engine_small_000.ogg space_engine_small_001.ogg space_engine_small_002.ogg '
     'space_engine_small_003.ogg space_engine_small_004.ogg thruster_fire_000.ogg thruster_fire_001.ogg '
     'thruster_fire_002.ogg thruster_fire_003.ogg thruster_fire_004.ogg'),
    ('digital-audio', 'Digital Audio', 'Boyquotes/kenney-digital-audio-for-godot',
     '185a77e7c675341ad8d0805b3bbe4f20427c2481', 'addons/kenney digital audio',
     'high_down.ogg high_up.ogg laser_1.ogg laser_2.ogg laser_3.ogg laser_4.ogg laser_5.ogg laser_6.ogg '
     'laser_7.ogg laser_8.ogg laser_9.ogg low_down.ogg low_random.ogg low_three_tone.ogg pep_sound_1.ogg '
     'pep_sound_2.ogg pep_sound_3.ogg pep_sound_4.ogg pep_sound_5.ogg phase_jump_1.ogg phase_jump_2.ogg '
     'phase_jump_3.ogg phase_jump_4.ogg phase_jump_5.ogg phaser_down_1.ogg phaser_down_2.ogg '
     'phaser_down_3.ogg phaser_up_1.ogg phaser_up_2.ogg phaser_up_3.ogg phaser_up_4.ogg phaser_up_5.ogg '
     'phaser_up_6.ogg phaser_up_7.ogg power_up_1.ogg power_up_10.ogg power_up_11.ogg power_up_12.ogg '
     'power_up_2.ogg power_up_3.ogg power_up_4.ogg power_up_5.ogg power_up_6.ogg power_up_7.ogg '
     'power_up_8.ogg power_up_9.ogg space_trash_1.ogg space_trash_2.ogg space_trash_3.ogg '
     'space_trash_4.ogg space_trash_5.ogg three_tone_1.ogg three_tone_2.ogg tone_1.ogg two_tone_1.ogg '
     'two_tone_2.ogg zap_1.ogg zap_2.ogg zap_three_tone_down.ogg zap_three_tone_up.ogg zap_two_tone.ogg '
     'zap_two_tone_2.ogg'),
    ('rpg-audio', 'RPG Audio', 'Boyquotes/kenney-rpg-audio-for-godot',
     '22eb79bb843bbcadcaa6ed119353a33265ffad11', 'addons/kenney rpg audio',
     'belt_handle_1.ogg belt_handle_2.ogg book_close.ogg book_flip_1.ogg book_flip_2.ogg book_flip_3.ogg '
     'book_open.ogg book_place_1.ogg book_place_2.ogg book_place_3.ogg chop.ogg cloth_1.ogg cloth_2.ogg '
     'cloth_3.ogg cloth_4.ogg cloth_belt.ogg cloth_belt_2.ogg creak_1.ogg creak_2.ogg creak_3.ogg '
     'door_close_1.ogg door_close_2.ogg door_close_3.ogg door_close_4.ogg door_open_1.ogg door_open_2.ogg '
     'draw_knife_1.ogg draw_knife_2.ogg draw_knife_3.ogg drop_leather.ogg footstep_0.ogg footstep_1.ogg '
     'footstep_2.ogg footstep_3.ogg footstep_4.ogg footstep_5.ogg footstep_6.ogg footstep_7.ogg '
     'footstep_8.ogg footstep_9.ogg handle_coins.ogg handle_coins_2.ogg handle_small_leather.ogg '
     'handle_small_leather_2.ogg knife_slice.ogg knife_slice_2.ogg metal_click.ogg metal_latch.ogg '
     'metal_pot_1.ogg metal_pot_2.ogg metal_pot_3.ogg'),
)

# Query words that reel editors use, mapped to the words in Kenney's file names. Approximations are labelled.
SYNONYMS = {
    'hit': {'impact', 'punch'}, 'punch': {'impact', 'punch'}, 'thud': {'impact', 'soft', 'heavy'},
    'boom': {'explosion'}, 'explode': {'explosion'}, 'glitch': {'glitch', 'computer', 'noise', 'zap'},
    'typing': {'click', 'switch', 'tick', 'mouseclick'}, 'keyboard': {'click', 'switch', 'tick'},
    'type': {'click', 'switch', 'tick'}, 'tap': {'click', 'tick', 'select'}, 'button': {'click', 'select', 'switch'},
    'ui': {'click', 'select', 'confirmation', 'back', 'open', 'close'}, 'hover': {'rollover'},
    'notification': {'confirmation', 'bong', 'pluck'}, 'success': {'confirmation', 'power', 'up'},
    'pop': {'pluck', 'drop', 'select'}, 'riser': {'up', 'power', 'phaser'}, 'rise': {'up', 'power', 'phaser'},
    'fall': {'down'}, 'drop': {'drop', 'down'}, 'scifi': {'laser', 'force', 'field', 'engine', 'thruster', 'zap'},
    'tech': {'computer', 'noise', 'zap', 'phaser'}, 'foley': {'footstep', 'cloth', 'book', 'door', 'leather', 'coins'},
    'steps': {'footstep'}, 'footsteps': {'footstep'}, 'paper': {'book', 'flip'}, 'page': {'book', 'flip'},
    'money': {'coins'}, 'coin': {'coins'}, 'cash': {'coins'},
    'transition': {'scratch', 'scroll', 'maximize', 'minimize'}, 'magic': {'power', 'up', 'force', 'field'},
}
APPROXIMATE = {'riser', 'rise', 'transition', 'glitch', 'typing', 'keyboard', 'type'}


def words(text):
    return {w for w in re.split(r'[^a-z]+', text.lower()) if w}


def groups():
    for key, title, repo, pin, folder, names in PACKS:
        found = {}
        for name in names.split():
            found.setdefault(re.sub(r'[_-]?\d+$', '', name.rsplit('.', 1)[0]), []).append(name)
        for stem, files in found.items():
            yield key, title, repo, pin, folder, stem, files


def search(client, query, category, limit):
    terms = words(str(query))
    expanded = set(terms)
    for t in terms:
        expanded |= SYNONYMS.get(t, set())
    packs = {key for key, *_ in PACKS if words(key) <= terms - {'sounds', 'audio'} or key.replace('-', '') in terms}
    ranked = []
    for key, title, repo, pin, folder, stem, files in groups():
        name = words(stem)
        hit = 2 * len(terms & name) + len(expanded & name) + (3 if key in packs else 0)
        if terms and not hit:
            continue
        ranked.append((-hit, key, stem, title, repo, pin, folder, files))
    out = []
    for _, key, stem, title, repo, pin, folder, files in sorted(ranked)[:limit]:
        base = f'https://raw.githubusercontent.com/{repo}/{pin}/{urllib.parse.quote(folder)}/'
        variants = [variant(base + urllib.parse.quote(f), f) for f in sorted(files, key=lambda f: (len(f), f))][:8]
        notes = [f'Kenney "{title}" pack, CC0 1.0: commercial use, no credit required (credit "Kenney" appreciated).',
                 f'Served from the GitHub mirror {repo} at the reviewed commit; kenney.nl is not contacted.',
                 'Short game sounds (mostly under 2 s); layer or stretch them for reels.']
        if terms & APPROXIMATE and not terms & words(stem):
            notes.append('Approximate match for "' + ' '.join(sorted(terms & APPROXIMATE)) + '": listen before using.')
        out.append(asset('kenney', f'{key}/{stem}', f'{title}: {stem.replace("_", " ")}', KENNEY,
                         f'https://github.com/{repo}/tree/{pin}', variants, CC0, category, notes))
    return out
