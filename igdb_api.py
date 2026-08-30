"""
IGDB API Client for fetching game information
"""
import requests
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import API_CONFIG, IGDB_PLATFORMS, IGDB_REGIONS


class IGDBClient:
    """Client for interacting with IGDB API"""
    
    BASE_URL = "https://api.igdb.com/v4"
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    
    # Mapping Region ID to full names for display
    REGION_NAMES = {
        1: "Europe (EU)",
        2: "North America (NA)",
        3: "Australia (AU)",
        4: "New Zealand (NZ)",
        5: "Japan (JP)",
        6: "China (CN)",
        7: "Asia (AS)",
        8: "Worldwide (WW)",
        9: "Korea (KR)",
        10: "Brazil (BR)",
    }
    
    # Status Enum Mapping
    STATUS_NAMES = {
        0: "Released (Вышла)",
        2: "Alpha",
        3: "Beta",
        4: "Early Access (Ранний доступ)",
        5: "Offline",
        6: "Cancelled (Отменена)",
        7: "Rumored (Слухи)"
    }
    
    def __init__(self):
        self.client_id = API_CONFIG["IGDB_CLIENT_ID"]
        self.client_secret = API_CONFIG["IGDB_CLIENT_SECRET"]
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
        
        # Reverse mapping for ID -> Name lookup
        self.ID_TO_PLATFORM = {v: k for k, v in IGDB_PLATFORMS.items()}
        
    def _get_access_token(self) -> str:
        """Get or refresh OAuth access token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
            
        response = requests.post(
            self.AUTH_URL,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        self.access_token = data["access_token"]
        self.token_expires_at = time.time() + data["expires_in"] - 60
        
        return self.access_token
    
    def _make_request(self, endpoint: str, query: str) -> List[Dict[str, Any]]:
        """Make a request to IGDB API"""
        token = self._get_access_token()
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/{endpoint}",
            headers=headers,
            data=query.encode('utf-8')
        )
        response.raise_for_status()
        return response.json()
    
    def search_games(self, query: str, platform_id: int, region_id: Optional[int] = None, limit: int = 25) -> List[Dict[str, Any]]:
        safe_query = query.replace('"', '\\"').replace("*", "\\*")
        where_clause = f'name ~ *"{safe_query}"* & platforms = ({platform_id})'
        if region_id:
            where_clause += f' & release_dates.region = {region_id}'
        
        igdb_query = f'''
            fields name, id, platforms;
            where {where_clause};
            sort name asc;
            limit {limit};
        '''
        try:
            return self._make_request("games", igdb_query)
        except Exception as e:
            print(f"Error searching games: {e}")
            return []

    def search_franchises(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Search for franchises by name"""
        safe_query = query.replace('"', '\\"').replace("*", "\\*")
        igdb_query = f'''
            fields name, id;
            where name ~ *"{safe_query}"*;
            sort name asc;
            limit {limit};
        '''
        try:
            return self._make_request("franchises", igdb_query)
        except Exception as e:
            print(f"Error searching franchises: {e}")
            return []

    def get_franchise_games(self, franchise_id: int) -> List[Dict[str, Any]]:
        """Fetch all games belonging to a specific franchise"""
        igdb_query = f'''
            fields games.name, games.id, games.platforms, games.first_release_date;
            where id = {franchise_id};
        '''
        try:
            results = self._make_request("franchises", igdb_query)
            if results and "games" in results[0]:
                games = results[0]["games"]
                # Sort by date
                games.sort(key=lambda x: x.get("first_release_date", float('inf')))
                return games
            return []
        except Exception as e:
            print(f"Error fetching franchise games: {e}")
            return []
    
    def get_all_games_for_platform(self, platform_id: int, offset: int = 0, limit: int = 50) -> list:
        # Added expansions and standalone_expansions to query
        igdb_query = f'''
            fields name, first_release_date, genres.name, themes.name, player_perspectives.name, platforms.name,
                   summary, version_title, status,
                   cover.url, cover.image_id, 
                   screenshots.url, screenshots.image_id,
                   involved_companies.company.name,
                   involved_companies.developer, involved_companies.publisher,
                   release_dates.*,
                   game_localizations.name, game_localizations.region,
                   game_modes.name, multiplayer_modes.*,
                   language_supports.language.name, language_supports.language_support_type.name,
                   dlcs.name, expansions.name, standalone_expansions.name, 
                   parent_game.name, franchises.name, remakes.name, remasters.name;
            where platforms = ({platform_id});
            sort name asc;
            offset {offset};
            limit {limit};
        '''
        try:
            results = self._make_request("games", igdb_query)
            processed = []
            for game in results:
                game_entry = self._process_game_data(game, None, platform_id)
                processed.append(game_entry)
            return processed
        except Exception as e:
            print(f"Error getting all games: {e}")
            return []
    
    def get_game_details(self, game_id: int, region_id: Optional[int] = None, platform_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        # Added expansions and standalone_expansions to query
        igdb_query = f'''
            fields name, first_release_date, genres.name, themes.name, player_perspectives.name, platforms.name,
                   summary, storyline, rating, aggregated_rating, status,
                   version_title,
                   cover.url, cover.image_id, cover.width, cover.height,
                   screenshots.url, screenshots.image_id, screenshots.width, screenshots.height,
                   involved_companies.company.name,
                   involved_companies.developer, involved_companies.publisher,
                   release_dates.*,
                   game_modes.name, multiplayer_modes.*,
                   game_localizations.name, game_localizations.region,
                   language_supports.language.name, language_supports.language_support_type.name,
                   dlcs.name, expansions.name, standalone_expansions.name,
                   parent_game.name, franchises.name, remakes.name, remasters.name;
            where id = {game_id};
        '''
        try:
            results = self._make_request("games", igdb_query)
            if results:
                game = results[0]
                return self._process_game_data(game, region_id, platform_id)
            return None
        except Exception as e:
            print(f"Error getting game details: {e}")
            return None
    
    def _process_game_data(self, game: Dict[str, Any], region_id: Optional[int], platform_id: Optional[int] = None) -> Dict[str, Any]:
        """Process game data"""
        release_dates = game.get("release_dates", [])
        involved_companies = game.get("involved_companies", [])
        
        # Earliest Date
        earliest_date = None
        if release_dates:
            valid_dates = [rd for rd in release_dates if rd.get("date")]
            sorted_dates = sorted(valid_dates, key=lambda x: x.get("date", float('inf')))
            if sorted_dates:
                earliest_date = sorted_dates[0].get("date")
        game["earliest_release_date"] = earliest_date
        
        # Regions
        regions_set = set()
        for rd in release_dates:
            r_id = rd.get("region")
            if r_id is not None and r_id in self.REGION_NAMES:
                regions_set.add(self.REGION_NAMES[r_id])
        
        locs = game.get("game_localizations", [])
        for loc in locs:
            r_id = loc.get("region")
            if r_id is not None and r_id in self.REGION_NAMES:
                regions_set.add(self.REGION_NAMES[r_id])

        game["all_regions"] = sorted(list(regions_set)) if regions_set else []
        
        # Status
        status_id = game.get("status", 0) 
        game["status_display"] = self.STATUS_NAMES.get(status_id, "Unknown")

        # Localization (Russian)
        lang_supports = game.get("language_supports", [])
        ru_support = []
        for lang in lang_supports:
            l_name = lang.get("language", {}).get("name", "")
            if l_name == "Russian":
                t_name = lang.get("language_support_type", {}).get("name", "")
                if t_name: ru_support.append(t_name)
        
        if ru_support:
            ru_support = sorted(list(set(ru_support)))
            game["russian_support"] = ", ".join(ru_support)
        else:
            game["russian_support"] = "None"

        # Relations (Improved DLC gathering)
        def extract_relations(key):
            items = game.get(key, [])
            if isinstance(items, dict): items = [items]
            res_list = []
            for i in items:
                if i.get("name"):
                    res_list.append({"name": i.get("name"), "id": i.get("id")})
            return res_list

        # Combine all DLC types
        dlc_combined = []
        dlc_combined.extend(extract_relations("dlcs"))
        dlc_combined.extend(extract_relations("expansions"))
        dlc_combined.extend(extract_relations("standalone_expansions"))
        
        # Remove duplicates by ID
        unique_dlcs = {d['id']: d for d in dlc_combined}.values()
        game["dlcs_data"] = sorted(list(unique_dlcs), key=lambda x: x['name'])

        game["parent_game_data"] = extract_relations("parent_game") 
        game["franchise_data"] = extract_relations("franchises")
        
        remakes_remasters = []
        remakes_remasters.extend(extract_relations("remakes"))
        remakes_remasters.extend(extract_relations("remasters"))
        game["remakes_remasters_data"] = remakes_remasters

        # Helper to create smart links: href='type:id|Name'
        def make_smart_links(data_list, type_prefix="game"):
            if not data_list: return "—"
            links = []
            for item in data_list:
                safe_name = item['name'].replace("'", "&#39;")
                href = f"{type_prefix}:{item['id']}|{safe_name}"
                links.append(f"<a href='{href}' style='color: #00d4ff; text-decoration: none;'>{item['name']}</a>")
            return "; ".join(links)

        # Generate HTML strings for UI
        game["dlc_link_str"] = make_smart_links(game["dlcs_data"], "game") # Changed key from dlcs_link_str to dlc_link_str to match UI
        game["parent_link_str"] = make_smart_links(game["parent_game_data"], "game")
        game["franchise_link_str"] = make_smart_links(game["franchise_data"], "franchise")
        game["remake_link_str"] = make_smart_links(game["remakes_remasters_data"], "game")

        # Plain text for table
        game["dlcs_str"] = "; ".join([d["name"] for d in game["dlcs_data"]])
        game["parent_game_str"] = "; ".join([d["name"] for d in game["parent_game_data"]])
        game["franchise_str"] = "; ".join([d["name"] for d in game["franchise_data"]])
        game["remakes_remasters_str"] = "; ".join([d["name"] for d in game["remakes_remasters_data"]])

        # Mixed Genres
        mixed_list = []
        if "genres" in game:
            mixed_list.extend([g.get("name") for g in game.get("genres", []) if g.get("name")])
        if "themes" in game:
            mixed_list.extend([t.get("name") for t in game.get("themes", []) if t.get("name")])
        if "player_perspectives" in game:
            mixed_list.extend([p.get("name") for p in game.get("player_perspectives", []) if p.get("name")])
        
        seen = set()
        unique_mixed = []
        for item in mixed_list:
            if item not in seen:
                seen.add(item)
                unique_mixed.append(item)
        game["mixed_genres"] = "; ".join(unique_mixed)
        
        # Companies
        developers = []
        publishers = []
        for company in involved_companies:
            company_name = company.get("company", {}).get("name", "")
            if company_name:
                if company.get("developer") and company_name not in developers:
                    developers.append(company_name)
                if company.get("publisher") and company_name not in publishers:
                    publishers.append(company_name)
        game["developers_list"] = developers
        game["publishers_list"] = publishers
        
        # Players
        multiplayer_modes = game.get("multiplayer_modes", [])
        max_local_players = 1
        for mode in multiplayer_modes:
            couch = mode.get("offlinecoopplayersmax", 0) or 0
            local_max = mode.get("offlinemax", 0) or 0
            splitscreen = mode.get("splitscreencoopmax", 0) or 0
            max_local_players = max(max_local_players, couch, local_max, splitscreen)
        
        if max_local_players == 1:
            game_modes = game.get("game_modes", [])
            mode_names = [m.get("name", "") for m in game_modes]
            if "Multiplayer" in mode_names or "Co-operative" in mode_names or "Split-screen" in mode_names:
                max_local_players = 2
        game["max_local_players"] = max_local_players
        
        game["description"] = game.get("summary", "")
        game["edition"] = game.get("version_title") or ""
        
        # Media
        cover = game.get("cover", {})
        if cover and cover.get("image_id"):
            image_id = cover["image_id"]
            game["cover_url_thumb"] = f"https://images.igdb.com/igdb/image/upload/t_cover_small/{image_id}.jpg"
            game["cover_url_medium"] = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
            game["cover_url_large"] = f"https://images.igdb.com/igdb/image/upload/t_cover_big_2x/{image_id}.jpg"
            game["cover_url_full"] = f"https://images.igdb.com/igdb/image/upload/t_original/{image_id}.jpg"
        else:
            game["cover_url_thumb"] = None; game["cover_url_medium"] = None; game["cover_url_large"] = None; game["cover_url_full"] = None
        
        screenshots = game.get("screenshots", [])
        screenshot_urls = []
        for ss in screenshots:
            if ss.get("image_id"):
                image_id = ss["image_id"]
                screenshot_urls.append({
                    "thumb": f"https://images.igdb.com/igdb/image/upload/t_screenshot_med/{image_id}.jpg",
                    "medium": f"https://images.igdb.com/igdb/image/upload/t_screenshot_big/{image_id}.jpg",
                    "full": f"https://images.igdb.com/igdb/image/upload/t_original/{image_id}.jpg",
                })
        game["screenshot_urls"] = screenshot_urls
        
        return game
    
    # Utils
    def format_release_date(self, timestamp: Optional[int]) -> str:
        if not timestamp: return "Неизвестно"
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d.%m.%Y")
        except Exception: return "Неизвестно"
    
    def format_genres(self, genres: Optional[List[Dict[str, Any]]]) -> str:
        if not genres: return "Неизвестно"
        return "; ".join([g.get("name", "") for g in genres if g.get("name")])
    
    def format_list(self, items: Optional[List[str]]) -> str:
        if not items: return "Неизвестно"
        return "; ".join(items)
    
    def get_platforms_list(self) -> List[str]:
        return list(IGDB_PLATFORMS.keys())
    
    def get_platform_id(self, platform_name: str) -> Optional[int]:
        return IGDB_PLATFORMS.get(platform_name)
    
    def get_platform_name_by_id(self, platform_id: int) -> Optional[str]:
        """Reverse lookup ID -> Name"""
        return self.ID_TO_PLATFORM.get(platform_id)

igdb_client = IGDBClient()