FROM pytorch/pytorch:latest

RUN python --help
RUN pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD [ "pytnon", "app.py" ]
