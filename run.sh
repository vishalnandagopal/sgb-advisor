sudo docker build . -t vishalnandagopal/sgb-advisor:latest -f Dockerfile

sudo docker run --env-file .env vishalnandagopal/sgb-advisor:latest
