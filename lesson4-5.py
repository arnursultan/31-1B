import os
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

Base = declarative_base()
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
Session = sessionmaker(bind=engine, expire_on_commit=False)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

class Chef(Base):
    __tablename__ = 'chefs'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String)
    recipes = relationship("Recipe", back_populates="chef", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chef id={self.id} name={self.name}>"

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    chef_id = Column(Integer, ForeignKey('chefs.id', ondelete="CASCADE"))
    cooking_time_minutes = Column(Integer)
    chef = relationship("Chef", back_populates="recipes")
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipe id={self.id} title={self.title}>"

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(String)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete="CASCADE"))
    recipe = relationship("Recipe", back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient id={self.id} name={self.name} qty={self.quantity}>"

def init_db():
    Base.metadata.create_all(engine)
    print("Таблицы созданы / проверены.")

def create_chef(session, name: str, country: str = None) -> Chef:
    existing = session.query(Chef).filter(Chef.name == name).first()
    if existing:
        return existing
    chef = Chef(name=name, country=country)
    session.add(chef)
    session.commit()
    session.refresh(chef)
    return chef

def add_ingredient(session, recipe: Recipe, name: str, quantity: str = None) -> Ingredient:
    ing = Ingredient(name=name, quantity=quantity, recipe_id=recipe.id)
    session.add(ing)
    session.commit()
    session.refresh(ing)
    return ing

def get_all_recipes(session):
    return session.query(Recipe).all()

def get_recipes_by_chef_name(session, recipe_title: str):
    recipe = session.query(Recipe).filter(Recipe.title == recipe_title).first()
    if not recipe:
        return None
    return recipe.ingredients

def demo():
    init_db()

    with Session() as session:
        sanzhar = create_chef(session, name="Sanzhar sybau", country="Ohio")
        ular = create_chef(session, name="Ular same", country="Oshio")

        borsch = create_recipe(session, recipe=borsch, name="Beetroot", quantity=2)
        burger