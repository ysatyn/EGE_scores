from __future__ import annotations
import datetime
from db.database import Base
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Boolean, DateTime, Date, ForeignKey


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scores = relationship("Scores", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class UserSubjectAssociation(Base):
    __tablename__ = "user_subjects"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String, ForeignKey("subjects.id"), primary_key=True)
    desired_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user = relationship("User", backref="user_subject_associations", lazy="selectin")
    subject = relationship("Subject", backref="user_subject_associations", lazy="selectin")


class Subject(Base):
    __tablename__ = "subjects"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    scores = relationship("Scores", back_populates="subject", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Subject(id={self.id}, name={self.name})>"


class Scores(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[str] = mapped_column(String, ForeignKey("subjects.id"), nullable=False)
    subject_name: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    exam_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="scores", lazy="selectin")
    subject = relationship("Subject", back_populates="scores", lazy="selectin")

    def __repr__(self):
        return f"<Scores(id={self.id}, user_id={self.user_id}, subject={self.subject_name}, score={self.score})>"


class Exams(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[str] = mapped_column(String, ForeignKey("subjects.id"), nullable=False)
    subject_name: Mapped[str] = mapped_column(String, nullable=False) 
    exam_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", lazy="selectin")

    def __repr__(self):
        return f"<Exams(subject={self.subject_name}, exam_date={self.exam_date})>"