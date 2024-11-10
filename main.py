from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from models import Base, User, Petition, Vote
from database import engine, session_local, get_db
from schemas import UserCreate, PetitionCreate, PetitionResponse, VoteCreate, UserResponse, VoteResponse, LoginRequest, \
    TokenRequest
from auth import create_access_token, get_current_user, get_user_from_token
from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)



@app.delete("/votes/", response_model=VoteResponse)
async def delete_vote(
    petition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.petition_id == petition_id
    ).first()

    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found for this user")

    db.delete(vote)
    db.commit()

    petition = db.query(Petition).filter(Petition.id == petition_id).first()
    if petition:
        petition.votes_count -= 1
        db.commit()

    return vote


@app.post("/token")
async def login_for_access_token(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == login_request.username).first()
    if user is None or user.password != login_request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password=user.password)  # Здесь пароль должен быть захэширован
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/petitions/", response_model=PetitionResponse)
async def create_petition(petition: PetitionCreate, db: Session = Depends(get_db)):
    db_petition = Petition(title=petition.title, description=petition.description)
    db.add(db_petition)
    db.commit()
    db.refresh(db_petition)
    return db_petition

@app.post("/votes/", response_model=VoteResponse)
async def create_vote(
        vote: VoteCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        token_request: TokenRequest = Depends()
):
    token = token_request.token
    current_user = get_user_from_token(db, token)

    petition = db.query(Petition).filter(Petition.id == vote.petition_id).first()
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found")

    existing_vote = db.query(Vote).filter(
        (Vote.user_id == current_user.id) & (Vote.petition_id == vote.petition_id)
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted for this petition")

    db_vote = Vote(user_id=current_user.id, petition_id=vote.petition_id)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)

    petition.votes_count += 1  # Обновление количества голосов
    db.commit()

    return db_vote

@app.get("/petitions/", response_model=List[PetitionResponse])
async def get_petitions(
        skip: int = Query(0, alias="page", ge=0),  # Пагинация: страницы начинаются с 0
        limit: int = Query(10, le=100),  # Ограничиваем количество на странице
        search: str = Query(None, max_length=50),  # Фильтрация по названию (поиск)
        sort_by: str = Query("created_at", regex="^(created_at|votes_count)$"),  # Сортировка по полям
        sort_order: str = Query("desc", regex="^(asc|desc)$"),  # Направление сортировки
        db: Session = Depends(get_db)
):
    # Строим базовый запрос для получения петиций
    query = db.query(Petition)

    # Фильтрация по названию
    if search:
        # Если search это числовое значение, фильтруем по id
        try:
            search_id = int(search)  # Преобразуем строку в число для поиска по id
            query = query.filter(Petition.id == search_id)
        except ValueError:
            # Если не удается преобразовать в число, фильтруем по title
            query = query.filter(Petition.title.ilike(f"%{search}%"))

    # Сортировка

    if sort_order == "asc":
        query = query.order_by(asc(getattr(Petition, sort_by)))
    else:
        query = query.order_by(desc(getattr(Petition, sort_by)))

    petitions = query.offset(skip * limit).limit(limit).all()

    return petitions
