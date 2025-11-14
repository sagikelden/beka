from app.database import Base, engine

def create_tables():
    print("Создаю таблицы в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Готово ✅")

if __name__ == "__main__":
    create_tables()
