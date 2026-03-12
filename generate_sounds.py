#!/usr/bin/env python3
"""Generate notification melodies (10 themes x 10) and TTS speech WAVs (Polly or ElevenLabs)."""

import argparse
import json
import math
import os
import shutil
import struct
import subprocess
import tempfile
import urllib.error
import urllib.request
import wave
from pathlib import Path

SAMPLE_RATE = 44100
POLLY_SAMPLE_RATE = 16000
SOUNDS_DIR = Path(__file__).parent / 'sounds'
SPEECH_PHRASES_FILE = Path(__file__).parent / 'speech_phrases.json'
CONFIG_FILE = Path(__file__).parent / 'config.json'

# ---------------------------------------------------------------------------
# Melody definitions: dict[theme_name, dict[melody_name, list[(freq_hz, dur_ms)]]]
# freq=0 means silence.  All melodies ≤2 seconds, shorter preferred.
# ---------------------------------------------------------------------------

THEMES: dict[str, dict[str, list[tuple[float, int]]]] = {
    'videogame': {
        'zelda_secret': [
            (587.33, 80), (622.25, 80), (659.25, 80), (698.46, 80),
            (739.99, 80), (783.99, 80), (830.61, 80), (880.00, 250),
            (0, 30), (880.00, 120),
        ],
        'mario_coin': [
            (987.77, 100), (0, 30), (1318.51, 350),
        ],
        'mgs_alert': [
            (880.00, 80), (0, 40), (880.00, 80), (0, 40),
            (880.00, 80), (0, 80), (659.25, 300),
        ],
        'ff_victory': [
            (523.25, 80), (523.25, 80), (523.25, 80), (523.25, 250),
            (0, 40), (415.30, 200), (466.16, 200), (523.25, 150),
        ],
        'sonic_ring': [
            (1046.50, 60), (1318.51, 60), (1567.98, 60),
            (2093.00, 80), (0, 30), (2093.00, 200),
        ],
        'pacman_intro': [
            (523.25, 80), (1046.50, 80), (783.99, 80), (1046.50, 80),
            (659.25, 120), (0, 30), (659.25, 80), (523.25, 80),
            (659.25, 80), (783.99, 120),
        ],
        'street_fighter': [
            (329.63, 60), (392.00, 60), (493.88, 60),
            (587.33, 80), (698.46, 80), (880.00, 200),
        ],
        'megaman_stage_clear': [
            (523.25, 80), (0, 30), (659.25, 80), (0, 30),
            (783.99, 80), (0, 30), (1046.50, 200),
            (0, 40), (880.00, 100), (1046.50, 300),
        ],
        'pokemon_battle': [
            (392.00, 60), (0, 20), (392.00, 60), (0, 20),
            (523.25, 60), (0, 20), (523.25, 60), (0, 20),
            (659.25, 80), (0, 30), (783.99, 80), (0, 30),
            (880.00, 200),
        ],
        'portal_turret': [
            (880.00, 100), (0, 30), (1108.73, 100), (0, 30),
            (1318.51, 100), (0, 50), (1760.00, 180),
        ],
    },

    'disney': {
        'when_you_wish': [
            (523.25, 300), (783.99, 300), (880.00, 250),
            (783.99, 180), (698.46, 180), (659.25, 350),
        ],
        'whole_new_world': [
            (440.00, 250), (523.25, 180), (659.25, 350),
            (0, 50), (587.33, 180), (523.25, 180), (440.00, 400),
        ],
        'let_it_go': [
            (440.00, 200), (493.88, 200), (523.25, 200),
            (659.25, 300), (0, 50), (587.33, 200), (523.25, 400),
        ],
        'under_the_sea': [
            (523.25, 130), (659.25, 130), (783.99, 130),
            (880.00, 200), (0, 60), (783.99, 130),
            (659.25, 130), (783.99, 300),
        ],
        'circle_of_life': [
            (440.00, 350), (0, 50), (659.25, 250),
            (587.33, 180), (523.25, 180), (440.00, 450),
        ],
        'be_our_guest': [
            (659.25, 130), (698.46, 130), (783.99, 130),
            (880.00, 250), (0, 50), (880.00, 130),
            (783.99, 130), (880.00, 400),
        ],
        'hakuna_matata': [
            (523.25, 180), (587.33, 180), (659.25, 180),
            (783.99, 250), (0, 80),
            (659.25, 180), (587.33, 180), (523.25, 350),
        ],
        'bibbidi_bobbidi': [
            (659.25, 100), (659.25, 100), (783.99, 100),
            (659.25, 100), (880.00, 100), (783.99, 100),
            (659.25, 100), (783.99, 350),
        ],
        'colors_of_wind': [
            (440.00, 250), (523.25, 250), (659.25, 350),
            (587.33, 250), (440.00, 450),
        ],
        'part_of_world': [
            (523.25, 180), (587.33, 180), (659.25, 180),
            (783.99, 300), (880.00, 300), (783.99, 350),
        ],
    },

    'anime': {
        'evangelion_fanfare': [
            (440.00, 140), (523.25, 140), (659.25, 140),
            (880.00, 250), (0, 50), (783.99, 140),
            (659.25, 140), (880.00, 350),
        ],
        'sailor_moon_transform': [
            (523.25, 130), (659.25, 130), (783.99, 130),
            (1046.50, 130), (1318.51, 130), (1567.98, 450),
        ],
        'dragon_ball_powerup': [
            (220.00, 100), (246.94, 100), (261.63, 100),
            (293.66, 100), (329.63, 100), (369.99, 100),
            (415.30, 100), (466.16, 100), (523.25, 400),
        ],
        'one_piece_departure': [
            (587.33, 180), (698.46, 180), (880.00, 250),
            (0, 50), (783.99, 180), (698.46, 180),
            (587.33, 350),
        ],
        'naruto_sadness': [
            (493.88, 350), (440.00, 250), (392.00, 180),
            (329.63, 350), (0, 50), (392.00, 180),
            (440.00, 350),
        ],
        'cowboy_bebop_intro': [
            (440.00, 100), (0, 50), (554.37, 100), (0, 50),
            (659.25, 100), (0, 50), (880.00, 180), (0, 60),
            (880.00, 100), (0, 40), (880.00, 350),
        ],
        'attack_on_titan': [
            (329.63, 180), (392.00, 180), (440.00, 180),
            (523.25, 250), (0, 50), (493.88, 140),
            (440.00, 140), (523.25, 400),
        ],
        'studio_ghibli_chime': [
            (1046.50, 180), (880.00, 180), (783.99, 180),
            (659.25, 250), (0, 60), (783.99, 180),
            (880.00, 350),
        ],
        'death_note_alert': [
            (220.00, 180), (0, 80), (220.00, 180), (0, 80),
            (261.63, 180), (0, 80), (220.00, 450),
        ],
        'my_hero_rising': [
            (392.00, 140), (440.00, 140), (523.25, 140),
            (587.33, 140), (659.25, 180), (783.99, 180),
            (880.00, 400),
        ],
    },

    'movies': {
        'star_wars_force': [
            (293.66, 350), (0, 50), (440.00, 350),
            (392.00, 140), (369.99, 140), (329.63, 140),
            (587.33, 350),
        ],
        'indiana_jones': [
            (329.63, 180), (349.23, 140), (392.00, 350),
            (0, 50), (523.25, 450),
        ],
        'harry_potter': [
            (493.88, 250), (0, 50), (659.25, 180),
            (622.25, 140), (659.25, 180), (493.88, 350),
            (880.00, 350),
        ],
        'jaws': [
            (164.81, 200), (174.61, 200), (164.81, 160), (174.61, 160),
            (164.81, 120), (174.61, 120), (164.81, 80), (174.61, 80),
            (164.81, 60), (174.61, 60),
        ],
        'james_bond': [
            (329.63, 140), (0, 40), (349.23, 140), (392.00, 140),
            (392.00, 300), (0, 50),
            (329.63, 140), (0, 40), (349.23, 140), (329.63, 300),
        ],
        'jurassic_park': [
            (392.00, 250), (440.00, 180), (392.00, 180),
            (329.63, 350), (0, 50), (392.00, 180),
            (587.33, 400),
        ],
        'godfather': [
            (440.00, 350), (493.88, 180), (523.25, 350),
            (493.88, 180), (440.00, 350), (392.00, 250),
        ],
        'back_to_future': [
            (523.25, 140), (659.25, 140), (783.99, 140),
            (1046.50, 300), (0, 50), (783.99, 140),
            (1046.50, 450),
        ],
        'imperial_march': [
            (392.00, 250), (392.00, 250), (392.00, 250),
            (311.13, 180), (466.16, 80),
            (392.00, 250), (311.13, 180), (466.16, 80),
            (392.00, 350),
        ],
        'pink_panther': [
            (329.63, 200), (349.23, 200), (0, 50),
            (329.63, 200), (349.23, 200), (415.30, 200),
            (392.00, 200), (0, 50), (329.63, 200), (349.23, 300),
        ],
    },

    '90s_rock': {
        'smells_like_teen_spirit': [
            (329.63, 150), (329.63, 150), (0, 60),
            (440.00, 150), (440.00, 150), (0, 60),
            (415.30, 150), (415.30, 150), (0, 60),
            (392.00, 250), (329.63, 300),
        ],
        'seven_nation_army': [
            (164.81, 250), (164.81, 180), (196.00, 250),
            (164.81, 250), (146.83, 250), (130.81, 250),
            (123.47, 400),
        ],
        'smoke_on_water': [
            (196.00, 200), (233.08, 200), (261.63, 350), (0, 80),
            (196.00, 200), (233.08, 200), (277.18, 150), (261.63, 400),
        ],
        'enter_sandman': [
            (164.81, 180), (0, 60), (196.00, 140), (185.00, 140),
            (164.81, 180), (0, 60), (196.00, 140), (164.81, 350),
        ],
        'iron_man': [
            (146.83, 350), (0, 80), (174.61, 350),
            (0, 80), (196.00, 200), (174.61, 200), (146.83, 400),
        ],
        'sweet_child': [
            (587.33, 100), (493.88, 100), (440.00, 100), (329.63, 100),
            (587.33, 100), (493.88, 100), (440.00, 100), (329.63, 100),
            (587.33, 100), (493.88, 100), (440.00, 350),
        ],
        'thunderstruck': [
            (493.88, 50), (440.00, 50), (493.88, 50), (440.00, 50),
            (493.88, 50), (440.00, 50), (493.88, 50), (440.00, 50),
            (493.88, 50), (440.00, 50), (493.88, 50), (440.00, 50),
            (659.25, 450),
        ],
        'back_in_black': [
            (329.63, 140), (0, 70), (293.66, 140), (0, 70),
            (261.63, 140), (0, 70), (329.63, 200), (0, 70),
            (329.63, 140), (329.63, 350),
        ],
        'crazy_train': [
            (277.18, 100), (0, 50), (277.18, 100), (329.63, 100),
            (277.18, 100), (261.63, 100), (277.18, 100),
            (0, 50), (329.63, 300), (277.18, 300),
        ],
        'paranoid': [
            (329.63, 130), (329.63, 130), (392.00, 130),
            (329.63, 130), (293.66, 130), (329.63, 130),
            (0, 50), (329.63, 130), (392.00, 130), (329.63, 300),
        ],
    },

    'classical': {
        'beethovens_fifth': [
            (392.00, 150), (392.00, 150), (392.00, 150),
            (311.13, 500), (0, 80),
            (349.23, 150), (349.23, 150), (349.23, 150),
            (293.66, 500),
        ],
        'fur_elise': [
            (659.25, 130), (622.25, 130), (659.25, 130),
            (622.25, 130), (659.25, 130), (493.88, 130),
            (587.33, 130), (523.25, 130), (440.00, 350),
        ],
        'ode_to_joy': [
            (659.25, 200), (659.25, 200), (698.46, 200), (783.99, 200),
            (783.99, 200), (698.46, 200), (659.25, 200), (587.33, 200),
        ],
        'eine_kleine': [
            (392.00, 130), (0, 30), (587.33, 130), (0, 30),
            (587.33, 200), (0, 30),
            (659.25, 130), (0, 30), (783.99, 130), (0, 30),
            (783.99, 300),
        ],
        'winter_vivaldi': [
            (659.25, 60), (659.25, 60), (659.25, 60), (659.25, 60),
            (659.25, 60), (659.25, 60), (0, 40),
            (622.25, 200), (587.33, 200), (523.25, 200),
            (493.88, 400),
        ],
        'ride_of_valkyries': [
            (293.66, 180), (349.23, 350), (293.66, 180),
            (392.00, 450), (349.23, 350),
        ],
        'moonlight_sonata': [
            (277.18, 180), (329.63, 180), (415.30, 180),
            (277.18, 180), (329.63, 180), (415.30, 180),
            (277.18, 180), (329.63, 180), (415.30, 350),
        ],
        'morning_grieg': [
            (659.25, 250), (622.25, 180), (659.25, 180),
            (622.25, 180), (659.25, 250), (783.99, 180),
            (880.00, 400),
        ],
        'william_tell': [
            (523.25, 80), (523.25, 80), (523.25, 80), (0, 40),
            (523.25, 80), (523.25, 80), (523.25, 80), (0, 40),
            (523.25, 80), (659.25, 80), (783.99, 300),
        ],
        'habanera': [
            (587.33, 160), (554.37, 160), (523.25, 160),
            (493.88, 160), (466.16, 160), (440.00, 160),
            (415.30, 160), (392.00, 400),
        ],
    },

    'beeps': {
        'ascending_chime': [
            (523.25, 100), (0, 30), (659.25, 100), (0, 30),
            (783.99, 250),
        ],
        'descending_chime': [
            (783.99, 100), (0, 30), (659.25, 100), (0, 30),
            (523.25, 250),
        ],
        'success_ding': [
            (1046.50, 80), (0, 20), (1318.51, 300),
        ],
        'triple_beep': [
            (880.00, 80), (0, 60), (880.00, 80), (0, 60),
            (880.00, 80),
        ],
        'soft_bell': [
            (440.00, 400), (0, 50), (440.00, 200),
        ],
        'digital_chirp': [
            (440.00, 40), (554.37, 40), (659.25, 40),
            (880.00, 40), (1046.50, 40), (1318.51, 40),
            (1567.98, 200),
        ],
        'notification_pop': [
            (987.77, 60), (0, 20), (1318.51, 200),
        ],
        'gentle_alert': [
            (659.25, 200), (0, 40), (523.25, 300),
        ],
        'radar_ping': [
            (1760.00, 30), (0, 40), (1760.00, 30), (0, 120),
            (1760.00, 60), (0, 200),
        ],
        'sonar_sweep': [
            (220.00, 60), (261.63, 60), (329.63, 60),
            (440.00, 60), (523.25, 60), (659.25, 300),
        ],
    },

    'chirps': {
        'robin_song': [
            (2093.00, 50), (1567.98, 40), (2093.00, 60), (0, 40),
            (2349.32, 50), (1760.00, 40), (2349.32, 80),
        ],
        'sparrow_twitter': [
            (2637.02, 30), (2349.32, 30), (2637.02, 30), (0, 20),
            (2349.32, 30), (2093.00, 30), (2349.32, 30), (0, 20),
            (2637.02, 40), (2793.83, 120),
        ],
        'canary_trill': [
            (2793.83, 30), (2637.02, 30), (2793.83, 30), (2637.02, 30),
            (2793.83, 30), (2637.02, 30), (2793.83, 30), (2637.02, 30),
            (2793.83, 60), (3135.96, 150),
        ],
        'cardinal_whistle': [
            (2637.02, 80), (1975.53, 100), (0, 30),
            (2637.02, 80), (1975.53, 100), (0, 30),
            (2349.32, 120),
        ],
        'chickadee_call': [
            (2093.00, 60), (0, 20), (1567.98, 40), (0, 20),
            (1318.51, 40), (1318.51, 40), (1318.51, 40), (1318.51, 60),
        ],
        'nightingale_phrase': [
            (1760.00, 60), (2093.00, 60), (2349.32, 80),
            (2093.00, 40), (1760.00, 60), (0, 30),
            (2093.00, 80), (2637.02, 150),
        ],
        'warbler_cascade': [
            (3135.96, 40), (2793.83, 40), (2637.02, 40),
            (2349.32, 40), (2093.00, 40), (1760.00, 40),
            (1567.98, 40), (1318.51, 200),
        ],
        'woodpecker_tap': [
            (1046.50, 20), (0, 20), (1046.50, 20), (0, 20),
            (1046.50, 20), (0, 20), (1046.50, 20), (0, 20),
            (1046.50, 20), (0, 20), (1046.50, 20), (0, 40),
            (1318.51, 100),
        ],
        'cuckoo_call': [
            (1318.51, 150), (1046.50, 200), (0, 40),
            (1318.51, 150), (1046.50, 200),
        ],
        'wren_burst': [
            (1567.98, 30), (1760.00, 30), (2093.00, 30),
            (2349.32, 30), (2637.02, 30), (2793.83, 30),
            (3135.96, 30), (3520.00, 200),
        ],
    },

    'cyberpunk': {
        'neon_district': [
            # Low synth bass drone with rising sting
            (110.00, 200), (116.54, 200), (123.47, 200),
            (130.81, 200), (138.59, 300), (0, 50), (277.18, 300),
        ],
        'netrunner_jack': [
            # Rapid ascending digital arpeggio — jacking into the net
            (220.00, 60), (277.18, 60), (329.63, 60), (440.00, 60),
            (554.37, 60), (659.25, 60), (880.00, 60),
            (0, 40), (880.00, 300),
        ],
        'corpo_alert': [
            # Cold, clinical two-tone alarm
            (440.00, 120), (0, 60), (554.37, 120), (0, 60),
            (440.00, 120), (0, 60), (554.37, 120), (0, 60),
            (440.00, 200),
        ],
        'braindance_glitch': [
            # Stuttering glitch pattern — broken playback
            (330.00, 40), (0, 20), (330.00, 40), (0, 20),
            (415.30, 40), (0, 80), (330.00, 40), (0, 20),
            (523.25, 60), (0, 40), (659.25, 300),
        ],
        'arasaka_tower': [
            # Ominous power chord — corporate menace
            (146.83, 300), (0, 50), (146.83, 150), (174.61, 150),
            (146.83, 300), (0, 50), (130.81, 400),
        ],
        'night_city_siren': [
            # Warbling siren sweep — two-tone oscillation
            (440.00, 100), (523.25, 100), (440.00, 100), (523.25, 100),
            (440.00, 100), (523.25, 100), (659.25, 400),
        ],
        'cyberware_boot': [
            # System boot sequence — ascending digital chirps
            (261.63, 50), (0, 30), (329.63, 50), (0, 30),
            (392.00, 50), (0, 30), (523.25, 50), (0, 30),
            (659.25, 50), (0, 30), (783.99, 50), (0, 60),
            (1046.50, 250),
        ],
        'ripperdoc_scan': [
            # Scanning pulse — low sweep with ping
            (130.81, 80), (164.81, 80), (196.00, 80), (246.94, 80),
            (293.66, 80), (0, 100), (1318.51, 60), (0, 40),
            (1318.51, 250),
        ],
        'delamain_chime': [
            # Polite AI assistant tone — clean and precise
            (659.25, 150), (0, 30), (783.99, 150), (0, 30),
            (880.00, 150), (0, 50), (1046.50, 350),
        ],
        'johnny_riff': [
            # Distorted rock riff — Silverhand energy
            (164.81, 120), (0, 40), (196.00, 120), (220.00, 120),
            (196.00, 120), (164.81, 200), (0, 40),
            (146.83, 120), (164.81, 350),
        ],
    },

    'dnd': {
        'tavern_lute': [
            # Lute arpeggio in D Mixolydian — warm and inviting
            (293.66, 100), (369.99, 100), (440.00, 100), (523.25, 100),
            (440.00, 100), (369.99, 100), (293.66, 100),
            (440.00, 350),
        ],
        'quest_fanfare': [
            # Heroic horn call — open fifths, triumphant
            (293.66, 200), (0, 30), (440.00, 200), (0, 30),
            (587.33, 300), (0, 50), (440.00, 150), (587.33, 350),
        ],
        'critical_hit': [
            # Sharp ascending strike — impact!
            (392.00, 60), (523.25, 60), (659.25, 60),
            (783.99, 60), (1046.50, 80), (0, 40),
            (1046.50, 120), (0, 30), (1046.50, 300),
        ],
        'spell_cast': [
            # Mystical ascending shimmer — arcane energy
            (440.00, 80), (493.88, 80), (554.37, 80),
            (659.25, 80), (783.99, 80), (880.00, 80),
            (1046.50, 80), (1318.51, 350),
        ],
        'dragon_roar': [
            # Low rumbling growl ascending to roar
            (110.00, 150), (123.47, 150), (146.83, 150),
            (174.61, 150), (220.00, 200), (0, 50),
            (293.66, 400),
        ],
        'treasure_chest': [
            # Sparkling discovery — music box wonder
            (783.99, 80), (880.00, 80), (1046.50, 80),
            (880.00, 80), (1046.50, 80), (1318.51, 80),
            (0, 40), (1567.98, 350),
        ],
        'long_rest': [
            # Gentle campfire melody — peaceful Dorian
            (293.66, 200), (329.63, 200), (349.23, 200),
            (392.00, 250), (349.23, 200), (329.63, 200),
            (293.66, 400),
        ],
        'initiative_roll': [
            # Drumroll tension — rapid repeated notes then resolution
            (392.00, 50), (392.00, 50), (392.00, 50), (392.00, 50),
            (392.00, 50), (392.00, 50), (0, 40),
            (523.25, 80), (659.25, 80), (783.99, 350),
        ],
        'bard_flourish': [
            # Quick melodic run — showing off
            (523.25, 60), (587.33, 60), (659.25, 60), (698.46, 60),
            (783.99, 60), (880.00, 60), (783.99, 60),
            (659.25, 60), (783.99, 350),
        ],
        'dungeon_door': [
            # Heavy creaking open — low ominous then reveal
            (146.83, 200), (0, 60), (155.56, 200), (0, 60),
            (164.81, 200), (0, 80), (329.63, 150), (440.00, 300),
        ],
    },
}

# ---------------------------------------------------------------------------
# Speech phrases
# ---------------------------------------------------------------------------


def load_speech_phrases() -> dict:
    """Load speech phrases from speech_phrases.json."""
    with open(SPEECH_PHRASES_FILE) as f:
        return json.load(f)


def expand_phrases(phrases: dict, theme: str) -> dict[str, str]:
    """Expand a theme's phrases into numbered {name}_{idx} -> text mappings.

    Falls back to 'default' theme if the requested theme has no speech entry.
    Expands {window} templates for window indices 0-9.
    Also generates number_{i} entries for number-only voice style.
    """
    theme_phrases = phrases.get(theme, phrases['default'])
    result: dict[str, str] = {}

    for event_type in ('stop', 'notification'):
        for idx, text in enumerate(theme_phrases.get(event_type, phrases['default'][event_type])):
            result[f'{event_type}_{idx}'] = text

    for event_type in ('stop_window', 'notification_window'):
        templates = theme_phrases.get(event_type, phrases['default'][event_type])
        for win_idx in range(10):
            for idx, template in enumerate(templates):
                text = template.replace('{window}', str(win_idx))
                result[f'{event_type}_{win_idx}_{idx}'] = text

    for i in range(10):
        result[f'number_{i}'] = str(i)

    return result


POLLY_VOICES: dict[str, dict[str, str]] = {
    'us': {'male': 'Stephen', 'female': 'Tiffany'},
    'uk': {'male': 'Brian', 'female': 'Amy'},
}

# ---------------------------------------------------------------------------
# Audio generation
# ---------------------------------------------------------------------------


def generate_tone(freq: float, duration_ms: int, volume: float = 0.6) -> list[int]:
    """Generate sine wave samples for a single tone with fade envelope."""
    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    if n_samples == 0:
        return []

    fade_samples = min(int(SAMPLE_RATE * 0.005), n_samples // 2)  # 5ms fade
    samples: list[int] = []

    for i in range(n_samples):
        if freq > 0:
            val = math.sin(2.0 * math.pi * freq * i / SAMPLE_RATE)
        else:
            val = 0.0

        if i < fade_samples:
            val *= i / fade_samples
        elif i >= n_samples - fade_samples:
            val *= (n_samples - 1 - i) / fade_samples

        samples.append(int(val * volume * 32767))

    return samples


def write_wav(filepath: Path, samples: list[int]) -> None:
    """Write 16-bit mono WAV file."""
    with wave.open(str(filepath), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        data = struct.pack(f'<{len(samples)}h', *samples)
        wf.writeframes(data)


def wrap_pcm_in_wav(pcm_path: Path, wav_path: Path, sample_rate: int = POLLY_SAMPLE_RATE) -> None:
    """Wrap raw PCM (16-bit signed LE) in a WAV container."""
    raw = pcm_path.read_bytes()
    with wave.open(str(wav_path), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(raw)


# ---------------------------------------------------------------------------
# Melody generation
# ---------------------------------------------------------------------------


def generate_melodies(theme_filter: str | None = None) -> None:
    """Generate melody WAV files for all (or one) theme."""
    if theme_filter and theme_filter not in THEMES:
        print(f'  No melodies for theme "{theme_filter}", skipping.\n')
        return

    themes = {theme_filter: THEMES[theme_filter]} if theme_filter else THEMES

    for theme_name, melodies in themes.items():
        theme_dir = SOUNDS_DIR / theme_name
        theme_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for name, notes in melodies.items():
            samples: list[int] = []
            for freq, dur in notes:
                samples.extend(generate_tone(freq, dur))

            filepath = theme_dir / f'{name}.wav'
            write_wav(filepath, samples)
            duration_s = len(samples) / SAMPLE_RATE
            print(f'  {theme_name}/{name}.wav ({duration_s:.2f}s)')
            count += 1

        print(f'  -> {count} melodies in {theme_name}/\n')


# ---------------------------------------------------------------------------
# Speech generation (AWS Polly)
# ---------------------------------------------------------------------------


def _generate_polly_phrases(phrases: dict[str, str], speech_dir: Path, voice_id: str) -> int:
    """Generate WAV files for a set of phrases using AWS Polly. Returns count."""
    count = 0
    for name, text in phrases.items():
        wav_path = speech_dir / f'{name}.wav'

        with tempfile.NamedTemporaryFile(suffix='.pcm', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            result = subprocess.run(
                [
                    'aws', 'polly', 'synthesize-speech',
                    '--engine', 'generative',
                    '--voice-id', voice_id,
                    '--output-format', 'pcm',
                    '--sample-rate', str(POLLY_SAMPLE_RATE),
                    '--text', text,
                    str(tmp_path),
                ],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f'  ERROR: Polly failed for {name}: {result.stderr.strip()}')
                continue

            wrap_pcm_in_wav(tmp_path, wav_path)
            count += 1
        finally:
            tmp_path.unlink(missing_ok=True)
    return count


def generate_speech_polly(accent_filter: str | None = None, gender_filter: str | None = None,
                          theme_filter: str | None = None) -> None:
    """Generate TTS speech WAV files using AWS Polly."""
    phrases = load_speech_phrases()
    themes_to_gen = [theme_filter] if theme_filter else list(phrases.keys())

    for theme in themes_to_gen:
        expanded = expand_phrases(phrases, theme)

        if theme == 'default':
            # Default phrases: generate for each accent/gender combo
            accents = {accent_filter: POLLY_VOICES[accent_filter]} if accent_filter else POLLY_VOICES
            for accent, genders in accents.items():
                voices = {gender_filter: genders[gender_filter]} if gender_filter else genders
                for gender, voice_id in voices.items():
                    speech_dir = SOUNDS_DIR / 'speech' / accent / gender
                    speech_dir.mkdir(parents=True, exist_ok=True)
                    count = _generate_polly_phrases(expanded, speech_dir, voice_id)
                    print(f'  -> {count} speech files ({voice_id}) in speech/{accent}/{gender}/\n')
        else:
            # Themed phrases: single voice, output to themed/{theme}/
            accent = accent_filter or 'us'
            gender = gender_filter or 'male'
            voice_id = POLLY_VOICES[accent][gender]
            speech_dir = SOUNDS_DIR / 'speech' / 'themed' / theme
            speech_dir.mkdir(parents=True, exist_ok=True)
            count = _generate_polly_phrases(expanded, speech_dir, voice_id)
            print(f'  -> {count} speech files ({voice_id}) in speech/themed/{theme}/\n')


# ---------------------------------------------------------------------------
# Speech generation (ElevenLabs)
# ---------------------------------------------------------------------------


def _resolve_elevenlabs_voice(voice_map: dict | None, accent: str, gender: str) -> str | None:
    """Look up ElevenLabs voice_id from config mapping."""
    if not voice_map:
        return None
    accent_map = voice_map.get(accent, {})
    voice = accent_map.get(gender)
    if not voice:
        print(f'  ERROR: No ElevenLabs voice configured for {accent}/{gender}. '
              f'Use --voice-id or set elevenlabs_voices in config.json.')
    return voice


def _generate_elevenlabs_phrases(phrases: dict[str, str], speech_dir: Path,
                                 api_key: str, voice_id: str) -> int:
    """Generate WAV files for a set of phrases using ElevenLabs API. Returns count."""
    count = 0
    for name, text in phrases.items():
        wav_path = speech_dir / f'{name}.wav'

        try:
            url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
            body = json.dumps({
                'text': text,
                'model_id': 'eleven_multilingual_v2',
            }).encode()
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    'xi-api-key': api_key,
                    'Content-Type': 'application/json',
                    'Accept': 'audio/mpeg',
                },
            )
            with urllib.request.urlopen(req) as resp:
                mp3_data = resp.read()
        except urllib.error.HTTPError as e:
            print(f'  ERROR: ElevenLabs API error for "{name}": {e.code} {e.reason}')
            continue
        except urllib.error.URLError as e:
            print(f'  ERROR: Network error for "{name}": {e.reason}')
            continue

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(mp3_data)

        try:
            result = subprocess.run(
                [
                    'ffmpeg', '-y', '-i', str(tmp_path),
                    '-ar', str(POLLY_SAMPLE_RATE),
                    '-ac', '1',
                    '-sample_fmt', 's16',
                    '-f', 'wav',
                    str(wav_path),
                ],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f'  ERROR: ffmpeg conversion failed for {name}: {result.stderr.strip()}')
                continue
            count += 1
        finally:
            tmp_path.unlink(missing_ok=True)
    return count


def generate_speech_elevenlabs(api_key: str, voice_id: str | None = None,
                               accent_filter: str | None = None, gender_filter: str | None = None,
                               theme_filter: str | None = None) -> None:
    """Generate TTS speech WAV files using ElevenLabs API."""
    if not shutil.which('ffmpeg'):
        print('  ERROR: ffmpeg not found. Install ffmpeg to generate ElevenLabs speech.')
        print('  Skipping speech generation.\n')
        return

    phrases = load_speech_phrases()
    themes_to_gen = [theme_filter] if theme_filter else list(phrases.keys())

    # Load voice mapping from config if no direct voice_id override
    voice_map = None
    if not voice_id:
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                config = json.load(f)
        voice_map = config.get('elevenlabs_voices', {})

    for theme in themes_to_gen:
        expanded = expand_phrases(phrases, theme)

        if theme == 'default':
            # Default phrases: generate for each accent/gender combo
            accents_to_gen = [accent_filter] if accent_filter else ['us', 'uk']
            genders_to_gen = [gender_filter] if gender_filter else ['male', 'female']
            for accent in accents_to_gen:
                for gender in genders_to_gen:
                    resolved_voice = voice_id or _resolve_elevenlabs_voice(voice_map, accent, gender)
                    if not resolved_voice:
                        continue
                    speech_dir = SOUNDS_DIR / 'speech' / accent / gender
                    speech_dir.mkdir(parents=True, exist_ok=True)
                    count = _generate_elevenlabs_phrases(expanded, speech_dir, api_key, resolved_voice)
                    print(f'  -> {count} speech files (ElevenLabs) in speech/{accent}/{gender}/\n')
        else:
            # Themed phrases: single voice
            accent = accent_filter or 'us'
            gender = gender_filter or 'male'
            resolved_voice = voice_id or _resolve_elevenlabs_voice(voice_map, accent, gender)
            if not resolved_voice:
                print(f'  Skipping theme "{theme}" — no voice resolved.\n')
                continue
            speech_dir = SOUNDS_DIR / 'speech' / 'themed' / theme
            speech_dir.mkdir(parents=True, exist_ok=True)
            count = _generate_elevenlabs_phrases(expanded, speech_dir, api_key, resolved_voice)
            print(f'  -> {count} speech files (ElevenLabs) in speech/themed/{theme}/\n')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    speech_themes = list(load_speech_phrases().keys()) if SPEECH_PHRASES_FILE.exists() else ['default']
    all_theme_choices = sorted(set(list(THEMES.keys()) + speech_themes))

    parser = argparse.ArgumentParser(description='Generate bells-and-whistles notification sounds')
    parser.add_argument('--melodies-only', action='store_true', help='Only generate melodies')
    parser.add_argument('--speech-only', action='store_true', help='Only generate speech')
    parser.add_argument('--theme', choices=all_theme_choices, help='Generate only one theme')
    parser.add_argument('--accent', choices=['us', 'uk'], help='Generate only one accent')
    parser.add_argument('--gender', choices=['male', 'female'], help='Generate only one gender')
    parser.add_argument('--tts-provider', choices=['polly', 'elevenlabs'], default='polly',
                        help='TTS provider for speech generation (default: polly)')
    parser.add_argument('--api-key', help='ElevenLabs API key (overrides ELEVENLABS_API_KEY env var)')
    parser.add_argument('--voice-id', help='ElevenLabs voice ID (overrides config mapping)')
    args = parser.parse_args()

    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.speech_only:
        print('=== Generating melodies ===\n')
        generate_melodies(args.theme)

    if not args.melodies_only:
        if args.tts_provider == 'elevenlabs':
            api_key = args.api_key or os.environ.get('ELEVENLABS_API_KEY')
            if not api_key:
                parser.error('ElevenLabs requires --api-key flag or ELEVENLABS_API_KEY env var')
            if not args.voice_id:
                config = {}
                if CONFIG_FILE.exists():
                    with open(CONFIG_FILE) as f:
                        config = json.load(f)
                if not config.get('elevenlabs_voices'):
                    parser.error('ElevenLabs requires --voice-id flag or elevenlabs_voices mapping in config.json')
            print('=== Generating speech (ElevenLabs) ===\n')
            generate_speech_elevenlabs(api_key, args.voice_id, args.accent, args.gender, args.theme)
        else:
            print('=== Generating speech (AWS Polly) ===\n')
            generate_speech_polly(args.accent, args.gender, args.theme)

    print('Done!')


if __name__ == '__main__':
    main()
