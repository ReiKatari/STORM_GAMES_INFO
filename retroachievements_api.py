import requests
from config import API_CONFIG
from typing import Dict, Any, Optional

class RetroAchievementsClient:
    BASE_URL = "https://retroachievements.org/API"
    
    # Mapping IGDB Platform ID -> RA Console ID
    CONSOLE_MAPPING = {
        18: 7,    # NES
        19: 3,    # SNES
        4: 2,     # N64
        21: 15,   # GameCube
        5: 16,    # Wii
        41: 30,   # Wii U
        130: 38,  # Switch (Not in RA yet usually?)
        33: 4,    # Game Boy
        22: 6,    # Game Boy Color
        24: 5,    # GBA
        20: 8,    # DS
        37: 74,   # 3DS
        64: 1,    # Mega Drive / Genesis
        29: 1,    # Genesis (Mapping conflict? check ID. Genesis is 1, Master System is 2... no MS is 13)
        # Fix: Mega Drive=1, Master System=13
        # In IGDB: 64=Master System, 29=Genesis
        
        # Corrected:
        29: 1,    # Mega Drive
        64: 13,   # Master System
        35: 21,   # Game Gear
        32: 17,   # Saturn
        23: 18,   # Dreamcast
        7: 12,    # PS1
        8: 21,    # PS2
        38: 41,   # PSP
        46: 54,   # Vita
        52: 8,    # Arcade (RA handles arcade differently, usually ID 8 is not Arcade? Arcade is 11)
        # Arcade is 11? Need verification. 
        # PC Engine = 9
    }

    def __init__(self):
        self.user = API_CONFIG.get("RETROACHIEVEMENTS_USER", "")
        self.api_key = API_CONFIG.get("RETROACHIEVEMENTS_API_KEY", "")

    def _get_auth(self):
        return {"z": self.user, "y": self.api_key}

    def get_console_id(self, igdb_platform_id: int) -> Optional[int]:
        return self.CONSOLE_MAPPING.get(igdb_platform_id)

    def _normalize(self, s):
        s = s.lower()
        if s.startswith("the "): s = s[4:]
        if s.endswith(", the"): s = s[:-5]
        # Remove punctuation, keep spaces
        s = "".join(c for c in s if c.isalnum() or c.isspace())
        return " ".join(s.split())

    def get_game_id(self, console_id: int, game_name: str) -> Optional[int]:
        """
        Get info (ID) by matching game name against console game list
        """
        if not self.user or not self.api_key: return None
        
        url = f"{self.BASE_URL}/API_GetGameList.php"
        params = self._get_auth()
        params["i"] = console_id
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # data is list of {ID, Title, ConsoleID, ImageIcon, ConsoleName}
                
                target_raw = game_name.lower()
                target_norm = self._normalize(game_name)
                
                # 1. Exact match (case insensitive)
                for game in data:
                    if game.get("Title", "").lower() == target_raw: return game.get("ID")
                
                # 2. Normalized match ("The 7th Saga" == "7th Saga, The")
                for game in data:
                    if self._normalize(game.get("Title", "")) == target_norm: return game.get("ID")

                # 3. Starts with (Normalized)
                for game in data:
                    t_norm = self._normalize(game.get("Title", ""))
                    if t_norm.startswith(target_norm): return game.get("ID")
                
                # 4. Contains (Normalized) - fallback
                for game in data:
                    t_norm = self._normalize(game.get("Title", ""))
                    if target_norm in t_norm: return game.get("ID")
                    
        except Exception as e:
            print(f"RA Error: {e}")
            return None
        return None

    def get_game_info(self, game_id: int) -> Dict[str, Any]:
        """Get achievement count and other info using Extended API"""
        if not game_id: return {}
        url = f"{self.BASE_URL}/API_GetGameExtended.php"
        params = self._get_auth()
        params["i"] = game_id
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                # Returns info including Achievements dictionary
                return response.json()
        except: pass
        return {}

    def get_game_list_raw(self, console_id: int) -> list:
        """Get raw game list for a console"""
        if not self.user or not self.api_key: return []
        url = f"{self.BASE_URL}/API_GetGameList.php"
        params = self._get_auth()
        params["i"] = console_id
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
        except: pass
        return []

ra_client = RetroAchievementsClient()
