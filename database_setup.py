from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy_serializer import SerializerMixin

Base = declarative_base()

class Car(Base, SerializerMixin):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///cars-collection.db')
    Base.metadata.create_all(engine)
