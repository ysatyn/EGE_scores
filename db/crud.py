from typing import Optional
from db.models import User, Subject, Scores, Exams, UserSubjectAssociation
from db.exceptions import *

from utils.validators import validate_user_data_create, validate_user_data_update

from sqlalchemy import func
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

async def create_user(db: AsyncSession, **user_data) -> User:
    user_data = validate_user_data_create(user_data)
    new_user = User(**user_data)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError as e:
        await db.rollback()
        raise UserAlreadyExistsError(id=user_data.get("id")) from e


async def get_user_by_id(db: AsyncSession, id: int) -> User | None:
    query = select(User).where(User.id == id)
    result = await db.execute(query)
    user = result.one_or_none()

    if user is None:
        raise UserNotFoundError(id=id)
    return user


async def update_user(db: AsyncSession, **update_data) -> User:
    """
    Update user data in the database. You could insert Message/CallbackQuery dict here.
    """
    try:
        await get_user_by_id(db, update_data.get("id"))
    except UserNotFoundError as e:
        raise e
    
    id = update_data.get("id")  # ИСПРАВЛЕНО: добавлен .get()
    user_data = validate_user_data_update(update_data)
    query = update(User).where(User.id == id).values(**user_data).returning(User)
    try:
        result = await db.execute(query)
        updated_user = result.scalar_one_or_none()
        if updated_user is None:
            await db.rollback()
            raise UserNotFoundError(id=id)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user
    except SQLAlchemyError as e:
        await db.rollback()
        raise CrudError("Failed to update user") from e



async def create_or_update_user(db: AsyncSession, **user_data) -> User:
    try:
        user = await create_user(db, **user_data)
        return user
    except UserAlreadyExistsError:
        if "id" not in user_data:
            raise ValueError("id is required for update")
        user = await update_user(db, **user_data)
        return user


async def delete_user(db: AsyncSession, id: int) -> None:
    try:
        await get_user_by_id(db, id)
    except UserNotFoundError:
        raise

    query = delete(User).where(User.id == id)
    try:
        await db.execute(query)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise CrudError("Failed to delete user") from e
    


async def get_score_by_id(db: AsyncSession, score_id: int) -> Scores:
    query = select(Scores).where(Scores.id == score_id)
    result = await db.execute(query)
    score = result.scalar_one_or_none()
    if score is None:
        raise ScoreNotFoundError(score_id=score_id)
    return score

async def add_score(db: AsyncSession, id: int, subject_id: str, score: int):
    new_score = Scores(user_id=id, subject_id=subject_id, score=score)
    db.add(new_score)
    try:
        await db.commit()
        await db.refresh(new_score)
        return new_score
    except IntegrityError as e:
        await db.rollback()
        raise CrudError("Failed to add score") from e


async def edit_existing_score(db: AsyncSession, score_id: int, new_score_value: int):
    query = update(Scores).where(Scores.id == score_id).values(score=new_score_value).returning(Scores)
    try:
        result = await db.execute(query)
        updated_score = result.scalar_one_or_none()
        if updated_score is None:
            await db.rollback()
            raise ScoreNotFoundError(score_id=score_id)
        await db.commit()
        await db.refresh(updated_score)
        return updated_score
    except SQLAlchemyError as e:
        await db.rollback()
        raise CrudError("Failed to update score") from e


async def delete_score_by_id(db: AsyncSession, score_id: int) -> None:
    try:
        score = await get_score_by_id(db, score_id)
    except ScoreNotFoundError as e:
        raise e
    try:
        query = delete(Scores).where(Scores.id == score_id)
        await db.execute(query)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise CrudError("Failed to delete score") from e


async def get_all_scores_for_user(db: AsyncSession, id: int, subject_id: Optional[str]) -> list[Scores]:
    """
    Retrieve all scores for a specific user, optionally filtered by subject.
    """
    try:
        user = await get_user_by_id(db, id)
    except UserNotFoundError as e:
        raise e

    query = select(Scores).where(Scores.user_id == id)
    if subject_id:
        query = query.where(Scores.subject_id == subject_id)
    result = await db.execute(query)
    scores = result.scalars().all()
    if not scores:
        raise ScoreNotFoundError()
    return scores

async def create_subjects(db: AsyncSession) -> list[Subject]:
    from utils.subjects import EGE_SUBJECTS_DICT
    subjects = []
    for subject_id, name in EGE_SUBJECTS_DICT.items():
        new_subject = Subject(id=subject_id, name=name)
        db.add(new_subject)
        subjects.append(new_subject)
    
    try:
        await db.commit()
        for subject in subjects:
            await db.refresh(subject)
        return subjects
    except IntegrityError as e:
        await db.rollback()
        raise CrudError("Failed to create subjects") from e


async def get_subject_by_id(db: AsyncSession, subject_id: str) -> Subject:
    query = select(Subject).where(Subject.id == subject_id)
    result = await db.execute(query)
    subject = result.scalar_one_or_none()
    if subject is None:
        raise SubjectNotFoundError(subject_id=subject_id)
    return subject


async def add_subject_to_user(db: AsyncSession, user_id: int, subject_id: str) -> UserSubjectAssociation:
    try:
        user = await get_user_by_id(db, user_id)
    except UserNotFoundError as e:
        raise e

    try:
        subject = await get_subject_by_id(db, subject_id)
    except SubjectNotFoundError as e:
        raise e
    
    association = UserSubjectAssociation(user_id=user_id, subject_id=subject_id)
    db.add(association)
    try:
        await db.commit()
        await db.refresh(association)
        return association
    except IntegrityError as e:
        await db.rollback()
        raise CrudError("Failed to add subject to user") from e


async def get_user_subjects(db: AsyncSession, user_id: int) -> list[Subject]:
    try:
        user = await get_user_by_id(db, user_id)
    except UserNotFoundError as e:
        raise e
    
    # Use explicit join between Subject and association table
    query = select(Subject).join(UserSubjectAssociation, Subject.id == UserSubjectAssociation.subject_id).where(UserSubjectAssociation.user_id == user_id)
    result = await db.execute(query)
    subjects = result.scalars().all()
    return subjects
    

async def get_user_subjects_ids(db: AsyncSession, user_id: int) -> list[str]:
    subjects = await get_user_subjects(db, user_id)
    subject_ids = [subject.id for subject in subjects]
    return subject_ids

async def remove_subject_from_user(db: AsyncSession, user_id: int, subject_id: str) -> None:
    try:
        user = await get_user_by_id(db, user_id)
    except UserNotFoundError as e:
        raise e

    try:
        subject = await get_subject_by_id(db, subject_id)
    except SubjectNotFoundError as e:
        raise e

    query = delete(UserSubjectAssociation).where(
        UserSubjectAssociation.user_id == user_id,
        UserSubjectAssociation.subject_id == subject_id
    )
    try:
        await db.execute(query)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise CrudError("Failed to remove subject from user") from e


async def switch_subject_for_user(db: AsyncSession, user_id: int, subject_id: str) -> None:
    user_subjects_ids = await get_user_subjects_ids(db, user_id)
    if subject_id in user_subjects_ids:
        await remove_subject_from_user(db, user_id, subject_id)
    else:
        await add_subject_to_user(db, user_id, subject_id)


async def set_desired_score(db: AsyncSession, user_id: int, subject_id: str, desired_score: int) -> UserSubjectAssociation:
    try:
        await get_user_by_id(db, user_id)
    except UserNotFoundError as e:
        raise e

    try:
        await get_subject_by_id(db, subject_id)
    except SubjectNotFoundError as e:
        raise e
    
    query = select(UserSubjectAssociation).where(
        UserSubjectAssociation.user_id == user_id,
        UserSubjectAssociation.subject_id == subject_id
    )
    result = await db.execute(query)
    association = result.scalar_one_or_none()
    
    if not association:
        association = UserSubjectAssociation(
            user_id=user_id, 
            subject_id=subject_id, 
            desired_score=desired_score
        )
        db.add(association)
    else:
        association.desired_score = desired_score
    
    try:
        await db.commit()
        await db.refresh(association)
        return association
    except IntegrityError as e:
        await db.rollback()
        raise CrudError("Failed to set desired score") from e
    except SQLAlchemyError as e:
        await db.rollback()
        raise CrudError("Failed to set desired score") from e