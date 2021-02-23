# api_service

An example of a **json api service** on `aiohttp`.
The `pydantic` and `valdec` libraries are used for data validation.

You can use the docker container to start:

```bash
docker build -t api_service .
docker run --rm -it -p 5000:5000 --name api_service api_service
```
