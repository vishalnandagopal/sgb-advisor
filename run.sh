sudo docker build . -t vishalnandagopal/sgb_advisor:latest -f Dockerfile

sudo docker run --mount type=bind,source="$(pwd)"/.env,target=/sgb-advisor/.env --mount type=bind,source="$(pwd)"/tmp/,target=/tmp/sgb_advisor/ vishalnandagopal/sgb_advisor:latest
