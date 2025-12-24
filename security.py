from passlib.context import CryptContext
from typing import List, Tuple, Dict, Any
import hashlib

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _bcrypt_input(secret: str) -> str:
    """
    bcrypt has a hard limit of 72 bytes input.
    So basically we pre hash with SHA-256 so the input to bcrypt is always fixed length.
    """
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()

def make_hash(secret: str) -> str:
    return pwd.hash(_bcrypt_input(secret))

def verify_hash(secret: str, hashed: str) -> bool:
    return pwd.verify(_bcrypt_input(secret), hashed)

def canon_level1(image_ids: List[str]) -> str:
    cleaned = sorted([s.strip() for s in image_ids if s.strip()])
    return "L1:" + ",".join(cleaned)

def canon_level3(sequence_ids: List[str]) -> str:
    cleaned = [s.strip() for s in sequence_ids if s.strip()]
    return "L3:" + ",".join(cleaned)

def quantize_points(points: List[Tuple[int, int]], grid: int = 20) -> str:
    cells = []
    for x, y in points:
        cells.append((max(0, x // grid), max(0, y // grid)))
    return "L2:" + ";".join([f"{cx}:{cy}" for cx, cy in cells])

def quantize_clicks(clicks: List[Dict[str, Any]], grid: int = 20) -> str:
    """
    clicks: [{"image_id": "img1.jpg", "point": (x, y)}, ...]
    Output becomes stable and tied to image IDs.
    """
    items = []
    for c in clicks:
        image_id = str(c["image_id"]).strip()
        x, y = c["point"]
        cx, cy = max(0, x // grid), max(0, y // grid)
        items.append((image_id, cx, cy))

    items.sort(key=lambda t: t[0])

    return "L2:" + ";".join([f"{img}@{cx}:{cy}" for img, cx, cy in items])
