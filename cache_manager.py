import os
import json
import hashlib
import shutil

class CacheManager:
    CACHE_DIR = "cache"
    LISTS_DIR = os.path.join(CACHE_DIR, "lists")
    GAMES_DIR = os.path.join(CACHE_DIR, "games")
    IMAGES_DIR = os.path.join(CACHE_DIR, "images")

    @classmethod
    def ensure_dirs(cls):
        """Создает структуру папок, если их нет"""
        for d in [cls.CACHE_DIR, cls.LISTS_DIR, cls.GAMES_DIR, cls.IMAGES_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    @classmethod
    def get_list_path(cls, platform_id: int, source: str = "igdb") -> str:
        """
        Возвращает путь к кэшу списка игр. 
        Теперь включает source, чтобы списки IGDB и MobyGames не пересекались.
        """
        return os.path.join(cls.LISTS_DIR, f"{platform_id}_{source}_games.json")

    @classmethod
    def get_game_path(cls, game_id: int, source: str) -> str:
        return os.path.join(cls.GAMES_DIR, f"{game_id}_{source}.json")

    @classmethod
    def get_image_path(cls, url: str) -> str:
        """Генерирует имя файла на основе хеша URL"""
        if not url: return ""
        hash_name = hashlib.md5(url.encode('utf-8')).hexdigest()
        return os.path.join(cls.IMAGES_DIR, hash_name + ".jpg")

    @classmethod
    def save_json(cls, path: str, data: any):
        cls.ensure_dirs()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения кэша {path}: {e}")

    @classmethod
    def load_json(cls, path: str) -> any:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None

    @classmethod
    def save_image(cls, url: str, data: bytes):
        cls.ensure_dirs()
        path = cls.get_image_path(url)
        try:
            with open(path, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"Ошибка сохранения изображения: {e}")

    @classmethod
    def has_image(cls, url: str) -> bool:
        path = cls.get_image_path(url)
        return os.path.exists(path)