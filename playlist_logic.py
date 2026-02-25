from typing import Dict, List, Optional, Tuple

Song = Dict[str, object]
PlaylistMap = Dict[str, List[Song]]

DEFAULT_PROFILE = {
    "name": "Default",
    "hype_min_energy": 7,
    "chill_max_energy": 3,
    "favorite_genre": "rock",
    "include_mixed": True,
}


def normalize_title(title: str) -> str:
    """Normalize a song title for comparisons."""
    if not isinstance(title, str):
        return ""
    return title.strip()


def normalize_artist(artist: str) -> str:
    """Normalize an artist name for comparisons."""
    if not artist:
        return ""
    return artist.strip().lower()


def normalize_genre(genre: str) -> str:
    """Normalize a genre name for comparisons."""
    return genre.lower().strip()


def normalize_song(raw: Song) -> Song:
    """Return a normalized song dict with expected keys."""
    title = normalize_title(str(raw.get("title", "")))
    artist = normalize_artist(str(raw.get("artist", "")))
    genre = normalize_genre(str(raw.get("genre", "")))
    energy = raw.get("energy", 0)

    if isinstance(energy, str):
        try:
            energy = int(energy)
        except ValueError:
            energy = 0

    tags = raw.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    return {
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tags": tags,
    }


def classify_song(song: Song, profile: Dict[str, object]) -> str:
    """Return a mood label given a song and user profile."""
    energy = song.get("energy", 0)
    genre = song.get("genre", "")
    title = song.get("title", "")

    hype_min_energy = profile.get("hype_min_energy", 7)
    chill_max_energy = profile.get("chill_max_energy", 3)
    favorite_genre = profile.get("favorite_genre", "")

    hype_keywords = ["rock", "punk", "party"]
    chill_keywords = ["lofi", "ambient", "sleep"]

    is_hype_keyword = any(k in genre for k in hype_keywords)
    is_chill_keyword = any(k in title for k in chill_keywords)

    if genre == favorite_genre or energy >= hype_min_energy or is_hype_keyword:
        return "Hype"
    if energy <= chill_max_energy or is_chill_keyword:
        return "Chill"
    return "Mixed"


def build_playlists(songs: List[Song], profile: Dict[str, object]) -> PlaylistMap:
    """Group songs into playlists based on mood and profile."""
    playlists: PlaylistMap = {
        "Hype": [],
        "Chill": [],
        "Mixed": [],
    }

    for song in songs:
        normalized = normalize_song(song)
        mood = classify_song(normalized, profile)
        normalized["mood"] = mood
        playlists[mood].append(normalized)

    return playlists


def merge_playlists(a: PlaylistMap, b: PlaylistMap) -> PlaylistMap:
    """Merge two playlist maps into a new map."""
    merged: PlaylistMap = {}
    for key in set(a.keys()) | set(b.keys()):
        merged[key] = a.get(key, []) + b.get(key, [])
    return merged


def compute_playlist_stats(playlists: PlaylistMap) -> Dict[str, object]:
    """Compute statistics across all playlists."""
    all_songs = [song for songs in playlists.values() for song in songs]
    
    hype = playlists.get("Hype", [])
    chill = playlists.get("Chill", [])
    mixed = playlists.get("Mixed", [])

    hype_ratio = len(hype) / len(all_songs) if all_songs else 0.0
    avg_energy = sum(s.get("energy", 0) for s in hype) / len(all_songs) if all_songs else 0.0

    top_artist, top_count = most_common_artist(all_songs)

    return {
        "total_songs": len(all_songs),
        "hype_count": len(hype),
        "chill_count": len(chill),
        "mixed_count": len(mixed),
        "hype_ratio": hype_ratio,
        "avg_energy": avg_energy,
        "top_artist": top_artist,
        "top_artist_count": top_count,
    }


def most_common_artist(songs: List[Song]) -> Tuple[str, int]:
    """Return the most common artist and count."""
    from collections import Counter
    
    artists = [str(song.get("artist", "")) for song in songs if song.get("artist")]
    if not artists:
        return "", 0
    
    return Counter(artists).most_common(1)[0]


def search_songs(songs: List[Song], query: str, field: str = "artist") -> List[Song]:
    """Return songs matching the query on a given field."""
    if not query:
        return songs
    
    q = query.lower().strip()
    return [s for s in songs if q in str(s.get(field, "")).lower()]


def _song_key(song: Song) -> Tuple[str, str]:
    """Return a tuple key (title, artist) normalized for comparison."""
    return (
        normalize_title(str(song.get("title", ""))).lower(),
        normalize_artist(str(song.get("artist", ""))).lower(),
    )


def contains_song(songs: List[Song], target: Song) -> bool:
    """Return True if target song already exists in songs list."""
    key = _song_key(target)
    return any(_song_key(s) == key for s in songs)


def lucky_pick(playlists: PlaylistMap, mode: str = "any") -> Optional[Song]:
    """Pick a song from the playlists according to mode."""
    songs_map = {
        "hype": playlists.get("Hype", []),
        "chill": playlists.get("Chill", []),
        "any": playlists.get("Hype", []) + playlists.get("Chill", []),
    }
    return random_choice_or_none(songs_map.get(mode, []))


def random_choice_or_none(songs: List[Song]) -> Optional[Song]:
    """Return a random song or None."""
    import random
    return random.choice(songs) if songs else None


def history_summary(history: List[Song]) -> Dict[str, int]:
    """Return a summary of moods seen in the history."""
    counts = {"Hype": 0, "Chill": 0, "Mixed": 0}
    for song in history:
        mood = song.get("mood", "Mixed")
        counts[mood] = counts.get(mood, 0) + 1
    return counts
