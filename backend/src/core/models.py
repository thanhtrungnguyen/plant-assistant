# from uuid import uuid4

# from database.base import Base, TimestampMixin  # Use global Base with timestamp mixin
# from sqlalchemy import Column, ForeignKey, Integer, String
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship


# class Item(TimestampMixin, Base):
#     __tablename__ = "items"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
#     name = Column(String, nullable=False)
#     description = Column(String, nullable=True)
#     quantity = Column(Integer, nullable=True)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

#     user = relationship("User", back_populates="items")
