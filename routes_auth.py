from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import SessionLocal
from models import User
from schemas_auth import (
    RegisterRequest, LoginL1Request, LoginL2Request, LoginL3Request, ApiResponse
)
from security import (
    make_hash, verify_hash, canon_level1, canon_level3, quantize_clicks
)

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=ApiResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip().lower()

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail="Username already exists")

    if len(payload.level1_images) != 3 or len(payload.level2_clicks) != 3 or len(payload.level3_sequence) != 3:
        raise HTTPException(status_code=400, detail="Each level must have exactly 3 selections")

    l1_set = set([x.strip() for x in payload.level1_images if x.strip()])
    click_set = set([c.image_id.strip() for c in payload.level2_clicks if c.image_id.strip()])
    if l1_set != click_set:
        raise HTTPException(
            status_code=400,
            detail="Level 2 clicks must be for the same 3 images chosen in Level 1"
        )

    l1_secret = canon_level1(payload.level1_images)

    clicks = [{"image_id": c.image_id, "point": c.point} for c in payload.level2_clicks]
    l2_secret = quantize_clicks(clicks, grid=20)

    l3_secret = canon_level3(payload.level3_sequence)

    user = User(
        username=username,
        l1_hash=make_hash(l1_secret),
        l2_hash=make_hash(l2_secret),
        l3_hash=make_hash(l3_secret),
    )
    db.add(user)
    db.commit()

    return ApiResponse(ok=True, message="Registered successfully")

@router.post("/login/l1", response_model=ApiResponse)
def login_l1(payload: LoginL1Request, db: Session = Depends(get_db)):
    username = payload.username.strip().lower()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    secret = canon_level1(payload.level1_images)
    if not verify_hash(secret, user.l1_hash):
        raise HTTPException(status_code=401, detail="Level 1 failed")

    return ApiResponse(ok=True, message="Level 1 passed")

@router.post("/login/l2", response_model=ApiResponse)
def login_l2(payload: LoginL2Request, db: Session = Depends(get_db)):
    username = payload.username.strip().lower()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if len(payload.level2_clicks) != 3:
        raise HTTPException(status_code=400, detail="Level 2 must have exactly 3 clicks")

    clicks = [{"image_id": c.image_id, "point": c.point} for c in payload.level2_clicks]
    secret = quantize_clicks(clicks, grid=20)

    if not verify_hash(secret, user.l2_hash):
        raise HTTPException(status_code=401, detail="Level 2 failed")

    return ApiResponse(ok=True, message="Level 2 passed")

@router.post("/login/l3", response_model=ApiResponse)
def login_l3(payload: LoginL3Request, db: Session = Depends(get_db)):
    username = payload.username.strip().lower()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    secret = canon_level3(payload.level3_sequence)
    if not verify_hash(secret, user.l3_hash):
        raise HTTPException(status_code=401, detail="Level 3 failed")

    return ApiResponse(ok=True, message="Login successful")
