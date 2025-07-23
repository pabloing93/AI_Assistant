FROM python

WORKDIR /rag

COPY requirements.txt .

RUN python -m venv .venv

RUN .venv/bin/pip install -r requirements.txt

COPY . .

RUN echo 'source /rag/.venv/bin/activate' >> /root/.bashrc

CMD [ "tail", "-f", "/dev/null" ]
