# api_service

An example of a json api service on `aiohttp`.

Build image:

```bash
docker build -t api_service . 
```

- The simple service:

```bash
docker run -e RS="run_simple.py" --rm -it -p 5000:5000 --name api_service api_service
```

- The service whose handlers can have different arguments:

```bash
docker run -e RS="run_kwargs.py" --rm -it -p 5000:5000 --name api_service api_service
```

- The service where requests and responses have a wrap and the data is validated:

```bash
docker run -e RS="run_wraps.py" --rm -it -p 5000:5000 --name api_service api_service
```

*[Article with examples on the site harb.ru](https://habr.com/ru/post/544638/)*
