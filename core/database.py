from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
DATABASE_URL = "mysql+pymysql://root:root@localhost/chatapplication"
Base = declarative_base()

engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def create_db():
    import auth.models
    import message.models
    import friends.models

    Base.metadata.create_all(bind=engine)