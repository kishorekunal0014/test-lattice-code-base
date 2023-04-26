FROM python:3.10.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y python3-pip

# Build folder for our app, only stuff that matters copied.
RUN mkdir build
WORKDIR /build

# Update, install requirements and then cleanup.
COPY ./requirements.txt .

RUN pip3 install -r requirements.txt                                          \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

EXPOSE 8080
