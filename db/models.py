from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    position: Mapped[str] = mapped_column(String(32), default="user")

    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="user", cascade="all, delete-orphan"
    )


class Todo(Base):
    __tablename__ = "todo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    text: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[str] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), nullable=True
    )
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="todos")
    category: Mapped["Category"] = relationship("Category", back_populates="todos")


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    todos: Mapped[list["Todo"]] = relationship("Todo", back_populates="category")
