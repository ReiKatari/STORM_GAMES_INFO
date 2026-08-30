"""
MobyGames API Client for fetching game information
"""
import requests
import time
from typing import Optional, List, Dict, Any
from config import API_CONFIG

class MobyGamesClient:
    """Client for interacting with MobyGames API"""
    
    BASE_URL = "https://api.mobygames.com/v1"
    
    def __init__(self):
        self.api_key = API_CONFIG.get("MOBYGAMES_API_KEY", "")
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to MobyGames API"""
        if not self.api_key:
            raise Exception("API Key not configured")
            
        if params is None:
            params = {}
            
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10
            )
            
            if response.status_code == 429:
                # Rate limit hit
                time.sleep(1)
                return self._make_request(endpoint, params)
                
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"MobyGames API Request Error: {e}")
            raise e

    def search_games(self, query: str, platform_id: int = None) -> List[Dict[str, Any]]:
        """
        Search for games by name.
        Note: Platform ID mapping from IGDB config won't work directly here due to ID mismatch,
        so we search primarily by title.
        """
        try:
            data = self._make_request("games", {"title": query})
            games = data.get("games", [])
            
            results = []
            for game in games:
                # MobyGames logic for platforms is complex, returning raw list for now
                # In stormgamesinfo.py we handle empty platform lists gracefully
                results.append({
                    "id": game.get("game_id"),
                    "name": game.get("title"),
                    "platforms": [] # Placeholder, as mapping is different
                })
            
            return results
        except Exception:
            return []

    def get_game_details(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific game and normalize it to match application structure
        """
        try:
            # Request game details including platforms, genres, description
            data = self._make_request(f"games/{game_id}")
            
            if not data:
                return None
                
            # Normalize data to match IGDB structure expected by main.py
            
            # 1. Genres
            genres_raw = data.get("genres", [])
            genres = [{"name": g.get("category_name")} for g in genres_raw]
            
            # 2. Platforms & Dates
            platforms = data.get("platforms", [])
            earliest_date = None
            developers = []
            publishers = []
            
            # MobyGames doesn't give precise dates in the main endpoint easily without extra calls,
            # but sometimes provides 'first_release_date' per platform in list
            for p in platforms:
                p_date = p.get("first_release_date")
                if p_date:
                    # Format is usually YYYY-MM-DD
                    try:
                        import datetime
                        dt = datetime.datetime.strptime(p_date, "%Y-%m-%d")
                        ts = dt.timestamp()
                        if earliest_date is None or ts < earliest_date:
                            earliest_date = ts
                    except:
                        pass

            # 3. Description
            description = data.get("description", "")
            # Cleanup HTML if present (simple replacement)
            description = description.replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n\n")

            # 4. Images
            # MobyGames provides a 'sample_cover'
            sample_cover = data.get("sample_cover", {})
            cover_url = sample_cover.get("image")
            
            # Screenshots are separate endpoint usually, but we can check sample_screenshots
            sample_screens = data.get("sample_screenshots", [])
            screenshot_urls = []
            for sc in sample_screens:
                img = sc.get("image")
                if img:
                    screenshot_urls.append({
                        "thumb": img,   # Moby often provides just one URL or requires API manipulation for sizes
                        "medium": img,
                        "full": img
                    })

            return {
                "id": data.get("game_id"),
                "name": data.get("title", ""),
                "edition": "", # Not easily available
                "earliest_release_date": earliest_date,
                "genres": genres,
                "all_regions": [], # Hard to parse from summary
                "max_local_players": 1, # Default
                "developers_list": developers, # Often needs credits endpoint, skipping for speed
                "publishers_list": publishers,
                "description": description,
                "cover_url_thumb": cover_url,
                "cover_url_medium": cover_url,
                "cover_url_large": cover_url,
                "cover_url_full": cover_url,
                "screenshot_urls": screenshot_urls,
                
                # --- NEW FIELDS (Matching IGDB Structure for UI) ---
                "status_display": "—",
                "russian_support": "None",
                
                # Relations (Empty lists for MobyGames simple client)
                "dlcs_data": [],
                "parent_game_data": [],
                "franchise_data": [],
                "remakes_remasters_data": [],

                # HTML Link Strings for UI (Defaults)
                "dlc_link_str": "—",
                "parent_link_str": "—",
                "franchise_link_str": "—",
                "remake_link_str": "—",

                # Plain Strings for Table/Excel
                "dlcs_str": "",
                "parent_game_str": "",
                "franchise_str": "",
                "remakes_remasters_str": "",
                
                # Mixed Genres helper
                "mixed_genres": "; ".join([g.get("name", "") for g in genres])
            }

        except Exception as e:
            print(f"Error getting MobyGames details: {e}")
            return None

    def get_all_games_for_platform(self, platform_id: int, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch 'all' games for a platform.
        Note: MobyGames IDs != IGDB IDs.
        Since we don't have a full mapping here, this is a placeholder stub to prevent crashes.
        """
        # In a real implementation, you would need to map IGDB platform_id to MobyGames platform_id
        # and then perform a paginated request to the 'games' endpoint with the platform ID.
        print(f"MobyGames 'All Games' fetch requested for IGDB Platform ID: {platform_id}")
        return []

    # Helper methods for formatting (reusing logic if needed or relying on main.py utils)
    def format_release_date(self, timestamp: Optional[int]) -> str:
        if not timestamp:
            return "Неизвестно"
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d.%m.%Y")
        except Exception:
            return "Неизвестно"

    def format_genres(self, genres: Optional[List[Dict[str, Any]]]) -> str:
        if not genres:
            return "Неизвестно"
        return "; ".join([g.get("name", "") for g in genres if g.get("name")])

    def format_list(self, items: Optional[List[str]]) -> str:
        if not items:
            return "Неизвестно"
        return "; ".join(items)

# Global client instance
moby_client = MobyGamesClient()