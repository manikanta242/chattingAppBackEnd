from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost/chatapplication"


engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)