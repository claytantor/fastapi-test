# fastapi-test

simple store example using fastapi, uvicorn and sqlalchemy based on the article: [Building REST APIs using FastAPI, SQLAlchemy & Uvicorn](https://dassum.medium.com/building-rest-apis-using-fastapi-sqlalchemy-uvicorn-8a163ccf3aa1)

* fastapi - https://fastapi.tiangolo.com/
* uvicorn - https://www.uvicorn.org/
* sqlalchemy - https://www.sqlalchemy.org/

## running the service

```bash
$ python -m app
2022-12-04 17:51:30,919 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2022-12-04 17:51:30,919 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("items")
2022-12-04 17:51:30,920 INFO sqlalchemy.engine.Engine [raw sql] ()
2022-12-04 17:51:30,920 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("stores")
2022-12-04 17:51:30,920 INFO sqlalchemy.engine.Engine [raw sql] ()
2022-12-04 17:51:30,920 INFO sqlalchemy.engine.Engine COMMIT
INFO:     Will watch for changes in these directories: ['/home/clay/data/github.com/claytantor/fastapi-test']
INFO:     Uvicorn running on http://127.0.0.1:5003 (Press CTRL+C to quit)
INFO:     Started reloader process [17899] using StatReload
2022-12-04 17:51:31,281 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2022-12-04 17:51:31,282 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("items")
2022-12-04 17:51:31,282 INFO sqlalchemy.engine.Engine [raw sql] ()
2022-12-04 17:51:31,282 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("stores")
2022-12-04 17:51:31,282 INFO sqlalchemy.engine.Engine [raw sql] ()
2022-12-04 17:51:31,282 INFO sqlalchemy.engine.Engine COMMIT
2022-12-04 17:51:31,320 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2022-12-04 17:51:31,320 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("items")
2022-12-04 17:51:31,320 INFO sqlalchemy.engine.Engine [raw sql] ()
2022-12-04 17:51:31,321 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("stores")
2022-12-04 17:51:31,321 INFO sqlalchemy.engine.Engine [raw sql] ()
2022-12-04 17:51:31,321 INFO sqlalchemy.engine.Engine COMMIT
INFO:     Started server process [17937]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

and then the docs:

`http://127.0.0.1:5003/docs`