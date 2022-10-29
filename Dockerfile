FROM python:3.9

RUN useradd seattle-data-final

WORKDIR /home/seattle-data-final

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY application.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP application.py
ENV FLASK_ENV development
ENV CONFIG_TYPE config.DevelopmentConfig

RUN chown -R seattle-data-final:seattle-data-final ./
USER seattle-data-final

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]