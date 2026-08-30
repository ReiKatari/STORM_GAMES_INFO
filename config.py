# API Configuration - Default empty values, filled from settings
import json
import os

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

# Default API configuration
DEFAULT_API_CONFIG = {
    "IGDB_CLIENT_ID": "",
    "IGDB_CLIENT_SECRET": "",
    "RETROACHIEVEMENTS_USER": "",
    "RETROACHIEVEMENTS_API_KEY": "",
    "MOBYGAMES_API_KEY": "",
    
    # Caching Settings - Search (Single Game)
    "CACHE_SEARCH_INFO": True,
    "CACHE_SEARCH_COVER": True,
    "CACHE_SEARCH_SS": True,
    
    # Caching Settings - All Games List
    "CACHE_ALL_INFO": True,
    "CACHE_ALL_COVER": False, # Default false to save bandwidth/space
    "CACHE_ALL_SS": False,
}


def load_settings() -> dict:
    """Load settings from JSON file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                # Merge with defaults to ensure new keys exist
                data = json.load(f)
                config = DEFAULT_API_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"Error loading settings: {e}")
    return DEFAULT_API_CONFIG.copy()


def save_settings(settings: dict):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}")


# Current API config (loaded from settings)
API_CONFIG = load_settings()


# IGDB Platform IDs mapping
_IGDB_PLATFORMS_RAW = {
    # === СОВРЕМЕННЫЕ ===
    "Sony PlayStation 5": 167,
    "Sony PlayStation 4": 48,
    "Microsoft Xbox Series X|S": 169,
    "Microsoft Xbox One": 49,
    "Nintendo Switch": 130,
    "Nintendo Switch 2": 471,
    "PC (Windows)": 6,
    
    # === SONY ===
    "Sony PlayStation 3": 9,
    "Sony PlayStation 2": 8,
    "Sony PlayStation": 7,
    "Sony PlayStation Vita": 46,
    "Sony PlayStation Portable": 38,
    "Sony PlayStation VR": 165,
    "Sony PlayStation VR2": 390,
    "PocketStation": 118,
    
    # === MICROSOFT ===
    "Microsoft Xbox 360": 12,
    "Microsoft Xbox": 11,
    "Microsoft MS-DOS": 13,
    "Windows Phone": 44,
    
    # === NINTENDO ===
    "Nintendo Wii U": 41,
    "Nintendo Wii": 5,
    "Nintendo GameCube": 21,
    "Nintendo 64": 4,
    "Super Nintendo (SNES)": 19,
    "Nintendo Entertainment System (NES)": 18,
    "Nintendo 3DS": 37,
    "New Nintendo 3DS": 137,
    "Nintendo DS": 20,
    "Nintendo DSi": 159,
    "Game Boy Advance": 24,
    "Game Boy Color": 22,
    "Game Boy": 33,
    "Nintendo Virtual Boy": 87,
    "Nintendo Game & Watch": 406,
    "Famicom Disk System": 51,
    "Super Famicom": 19,
    "Satellaview": 115,
    "Pokemon mini": 236,
    
    # === SEGA ===
    "Sega Dreamcast": 23,
    "Sega Saturn": 32,
    "Sega Genesis / Mega Drive": 29,
    "Sega CD / Mega-CD": 78,
    "Sega 32X": 30,
    "Sega Master System": 64,
    "Sega Game Gear": 35,
    "Sega SG-1000": 70,
    "Sega Mark III": 64,
    "Sega Pico": 238,
    
    # === ATARI ===
    "Atari 2600": 59,
    "Atari 5200": 66,
    "Atari 7800": 60,
    "Atari Jaguar": 62,
    "Atari Jaguar CD": 84,
    "Atari Lynx": 61,
    "Atari ST/STE": 63,
    "Atari 8-bit": 65,
    "Atari Falcon": 240,
    "Atari XEGS": 309,
    
    # === COMMODORE ===
    "Commodore 64": 15,
    "Commodore Amiga": 16,
    "Commodore Amiga CD32": 114,
    "Commodore 128": 94,
    "Commodore VIC-20": 71,
    "Commodore PET": 133,
    "Commodore Plus/4": 99,
    "Commodore CDTV": 129,
    
    # === NEC ===
    "NEC TurboGrafx-16 / PC Engine": 86,
    "NEC PC Engine CD": 150,
    "NEC SuperGrafx": 128,
    "NEC PC-FX": 274,
    "NEC PC-8800 Series": 249,
    "NEC PC-9800 Series": 149,
    
    # === SNK ===
    "SNK Neo Geo AES": 80,
    "SNK Neo Geo MVS": 79,
    "SNK Neo Geo CD": 136,
    "SNK Neo Geo Pocket": 119,
    "SNK Neo Geo Pocket Color": 120,
    "Hyper Neo Geo 64": 308,
    
    # === 3DO ===
    "3DO Interactive Multiplayer": 50,
    
    # === PHILIPS ===
    "Philips CD-i": 117,
    "Philips Videopac G7000": 126,
    "Philips VG 5000": 372,
    
    # === SINCLAIR ===
    "Sinclair ZX Spectrum": 26,
    "Sinclair ZX81": 349,
    
    # === AMSTRAD ===
    "Amstrad CPC": 25,
    "Amstrad GX4000": 389,
    
    # === MSX ===
    "MSX": 27,
    "MSX2": 53,
    "MSX TurboR": 392,
    
    # === BANDAI ===
    "Bandai WonderSwan": 57,
    "Bandai WonderSwan Color": 58,
    "Bandai Playdia": 125,
    "Apple Pippin": 275,
    
    # === COLECO ===
    "ColecoVision": 68,
    
    # === MATTEL ===
    "Mattel Intellivision": 67,
    "Mattel Aquarius": 217,
    
    # === ARCADES ===
    "Arcade": 52,
    
    # === COMPUTERS & OTHERS ===
    "Linux": 3,
    "Apple Macintosh": 14,
    "Apple II": 75,
    "Apple IIgs": 93,
    "Sharp X68000": 100,
    "Sharp X1": 307,
    "FM Towns": 116,
    "Acorn Archimedes": 91,
    "Acorn Electron": 88,
    "BBC Micro": 107,
    "Oric 1/Atmos": 381,
    "Dragon 32/64": 260,
    "Tandy TRS-80": 266,
    "TI-99/4A": 268,
    "Vectrex": 73,
    "Fairchild Channel F": 353,
    "Bally Astrocade": 313,
    "Magnavox Odyssey 2": 126,
    "Watara Supervision": 204,
    "Game.com": 202,
    "Tapwave Zodiac": 164,
    "Nokia N-Gage": 42,
    "Gizmondo": 205,
    "Ouya": 203,
    "Google Stadia": 170,
    "SteamOS": 92,
    "Meta Quest": 384,
    "Oculus Rift": 162,
    "Oculus Go": 384,
    "HTC Vive": 163,
    "Samsung Gear VR": 161,
    "Google Daydream": 206,
    "Valve Index": 385,
    "Android": 34,
    "iOS": 39,
    "Web Browser": 82,
    
    # === RUSSIAN COMPUTERS ===
    "Elektronika BK": 319,
    "Vector-06C": 320,
    "Agat": 321,
    "Microsha": 322,
    "Radio-86RK": 323,
    "Apogey BK-01": 324,
    "Specialist": 325,
    "Partner 01.01": 326,
}


def _sort_platforms(platforms: dict) -> dict:
    """Sort platforms: numbers first, then English, then Russian"""
    def sort_key(name: str):
        first_char = name[0] if name else ''
        if first_char.isdigit():
            return (0, name.lower())
        elif first_char.isascii() and first_char.isalpha():
            return (1, name.lower())
        else:
            return (2, name.lower())
    
    sorted_keys = sorted(platforms.keys(), key=sort_key)
    return {k: platforms[k] for k in sorted_keys}


IGDB_PLATFORMS = _sort_platforms(_IGDB_PLATFORMS_RAW)
IGDB_REGIONS = {} # Not actively used in this file but required for import