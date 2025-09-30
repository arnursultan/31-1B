import os
from typing import List, Optional, Tuple
from sqlalchemy import (
    Column, Integer, String, ForeignKey, create_engine, event, Index, func, and_, or_
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session as SASession
from sqlalchemy.exc import IntegrityError
import argparse

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
    name = Column(String, nullable=False, unique=True)
    country = Column(String)

    recipes = relationship(
        "Recipe",
        back_populates="chef",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        Index("ix_chefs_name", func.lower(name)),
        Index("ix_chefs_country", func.lower(country)),
    )

    def __repr__(self):
        return f"<Chef id={self.id} name={self.name}>"


class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    chef_id = Column(Integer, ForeignKey('chefs.id', ondelete="CASCADE"), nullable=False)
    cooking_time_minutes = Column(Integer)

    chef = relationship("Chef", back_populates="recipes")
    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        Index("ix_recipes_title", func.lower(title)),
        Index("ix_recipes_chef_id", chef_id),
        Index("ix_recipes_cooktime", cooking_time_minutes),
    )

    def __repr__(self):
        return f"<Recipe id={self.id} title={self.title}>"


class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(String)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete="CASCADE"), nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")

    __table_args__ = (
        Index("ix_ingredients_name", func.lower(name)),
        Index("ix_ingredients_recipe_id", recipe_id),
    )

    def __repr__(self):
        return f"<Ingredient id={self.id} name={self.name} qty={self.quantity}>"


def init_db():
    Base.metadata.create_all(engine)
    print("Таблицы созданы / проверены.")

def create_chef(session: SASession, name: str, country: Optional[str] = None) -> Chef:
    name = name.strip()
    existing = session.query(Chef).filter(func.lower(Chef.name) == func.lower(name)).first()
    if existing:
        return existing
    chef = Chef(name=name, country=country)
    session.add(chef)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        chef = session.query(Chef).filter(func.lower(Chef.name) == func.lower(name)).one()
    session.refresh(chef)
    return chef


def create_recipe(session: SASession, title: str, chef: Chef, cooking_time_minutes: Optional[int] = None) -> Recipe:
    recipe = Recipe(title=title.strip(), chef_id=chef.id, cooking_time_minutes=cooking_time_minutes)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


def add_ingredient(session: SASession, recipe: Recipe, name: str, quantity: Optional[str] = None) -> Ingredient:
    ing = Ingredient(name=name.strip(), quantity=(quantity.strip() if quantity else None), recipe_id=recipe.id)
    session.add(ing)
    session.commit()
    session.refresh(ing)
    return ing


def get_all_recipes(session: SASession, limit: int = 100, offset: int = 0, order_by: str = "title") -> List[Recipe]:
    q = session.query(Recipe)
    if order_by == "title":
        q = q.order_by(func.lower(Recipe.title))
    elif order_by == "time":
        q = q.order_by(Recipe.cooking_time_minutes.is_(None), Recipe.cooking_time_minutes)
    elif order_by == "chef":
        q = q.join(Recipe.chef).order_by(func.lower(Chef.name))
    return q.offset(offset).limit(limit).all()


def get_recipes_by_chef_name(session: SASession, chef_name: str, limit: int = 100) -> List[Recipe]:
    return (
        session.query(Recipe)
        .join(Chef)
        .filter(func.lower(Chef.name).like(f"%{chef_name.lower()}%"))
        .limit(limit)
        .all()
    )


def get_ingredients_for_recipe(session: SASession, recipe_title: str) -> Optional[List[Ingredient]]:
    recipe = session.query(Recipe).filter(func.lower(Recipe.title) == recipe_title.lower()).first()
    if not recipe:
        return None
    return recipe.ingredients


def search_recipes(
    session: SASession,
    title_substring: Optional[str] = None,
    chef_name: Optional[str] = None,
    ingredient_substring: Optional[str] = None,
    cook_time_range: Optional[Tuple[Optional[int], Optional[int]]] = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = "title",
) -> List[Recipe]:

    q = session.query(Recipe)

    if chef_name:
        q = q.join(Recipe.chef).filter(func.lower(Chef.name).like(f"%{chef_name.lower()}%"))

    if title_substring:
        q = q.filter(func.lower(Recipe.title).like(f"%{title_substring.lower()}%"))

    if ingredient_substring:
        q = q.join(Recipe.ingredients).filter(func.lower(Ingredient.name).like(f"%{ingredient_substring.lower()}%"))

    if cook_time_range:
        tmin, tmax = cook_time_range
        if tmin is not None:
            q = q.filter(Recipe.cooking_time_minutes >= tmin)
        if tmax is not None:
            q = q.filter(Recipe.cooking_time_minutes <= tmax)

    q = q.distinct()

    if order_by == "title":
        q = q.order_by(func.lower(Recipe.title))
    elif order_by == "time":
        q = q.order_by(Recipe.cooking_time_minutes.is_(None), Recipe.cooking_time_minutes)
    elif order_by == "chef":
        q = q.join(Recipe.chef).order_by(func.lower(Chef.name))

    return q.offset(offset).limit(limit).all()


def list_chefs(session: SASession, limit: int = 100, offset: int = 0, q: Optional[str] = None) -> List[Chef]:
    query = session.query(Chef)
    if q:
        query = query.filter(
            or_(func.lower(Chef.name).like(f"%{q.lower()}%"), func.lower(Chef.country).like(f"%{q.lower()}%"))
        )
    return query.order_by(func.lower(Chef.name)).offset(offset).limit(limit).all()

def update_chef(session: SASession, chef_id: int, *, name: Optional[str] = None, country: Optional[str] = None) -> Optional[Chef]:
    chef = session.get(Chef, chef_id)
    if not chef:
        return None
    if name:
        chef.name = name.strip()
    if country is not None:
        chef.country = country.strip() if country else None
    session.commit()
    session.refresh(chef)
    return chef


def update_recipe(
    session: SASession,
    recipe_id: int,
    *,
    title: Optional[str] = None,
    cooking_time_minutes: Optional[int] = None,
    chef_id: Optional[int] = None,

) -> Optional[Recipe]:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return None
    if title:
        recipe.title = title.strip()
    if cooking_time_minutes is not None:
        recipe.cooking_time_minutes = cooking_time_minutes
    if chef_id is not None:
        if not session.get(Chef, chef_id):
            raise ValueError(f"Chef with id={chef_id} does not exist")
        recipe.chef_id = chef_id
    session.commit()
    session.refresh(recipe)
    return recipe


def update_ingredients(
    session: SASession,
    ingredient_id: int,
    *,
    name: Optional[str] = None,
    quantity: Optional[int] = None,
) -> Optional[Ingredient]:
    ing = session.get(Ingredient, ingredient_id)
    if not ing:
        return None
    if name:
        ing.name = name.strip()
    if quantity is not None:
        ing.quantity = quantity.strip() if quantity else None
    session.commit()
    session.refresh(ing)
    return ing

def delete_chef(session: SASession, chef_id: int) -> bool:
    chef = session.get(Chef, chef_id)
    if not chef:
        return False
    session.delete(chef)
    session.commit()
    return True

def delete_recipe(session: SASession, recipe_id: int) -> bool:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return False
    session.delete(recipe)
    session.commit()
    return True

def delete_ingredients(session: SASession, ingredient_id: int) -> bool:
    ing = session.get(Ingredient, ingredient_id)
    if not ing:
        return False
    session.delete(ing)
    session.commit()
    return True

def demo():
