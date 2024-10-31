sudo docker build . -t sgb_advisor:latest -f Dockerfile

sudo docker run --mount type=bind,source="$(pwd)"/.env,target=/sgb-advisor/.env --mount type=bind,source="$(pwd)"/tmp/,target=/tmp/sgb_advisor/ sgb_advisor:latest
