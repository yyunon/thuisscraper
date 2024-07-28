# A scraper for thuisbezorgd

In this repository, we have a application to scrape https://www.thuisbezorgd.nl/. Then, we serve several different analytics endpoints to run
example queries on the scraped data.

The project uses poetry as a package manager. There exists a Dockerfile to run the applications

There are several environment variables that are required. You can pass them via docker build args or if you run the application locally, use the following commands

```
export postgres_conn="the connection string to your postgress application"
```

If you use a proxy server, please export the following environment variables. Beware in mind that 
```
export proxy_username="your username"
export proxy_password="your password"
export proxy_host="your host"
export proxy_port="your port"
```

In case you want to run application via docker, please make use of the following command:
```
docker build -t thuis --build-arg postgres_conn=...
docker run --name thuis -p 8000:8000 image_id
```
Make sure that you map the port

You can also run the application via your host machine
```
poetry install
poetry run fastapi run ./app/main.py --port 8000
```