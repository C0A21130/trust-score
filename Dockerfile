FROM python:3.12
WORKDIR /app

RUN apt update -qq
RUN pip install --upgrade pip

COPY requirements.txt /app/
COPY lesmis.gml /app/
RUN pip install -r /app/requirements.txt

CMD ["jupyter", "notebook","--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]

