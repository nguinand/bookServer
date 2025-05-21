from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db_models.base import Base


class Publisher(Base):
    __tablename__ = "publishers"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # A publisher can publish multiple books.
    # A book belongs to one publisher.
    # 1:N
    books = relationship("Book", back_populates="publisher")
