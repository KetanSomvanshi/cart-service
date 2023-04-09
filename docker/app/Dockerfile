FROM python:3.9-alpine

WORKDIR /code

COPY requirements.txt .
RUN apk --no-cache add --virtual .build-deps \
    curl \
		git \
		build-base \
		openssh-client \
	&& \
	apk --update-cache add --virtual .runtime-deps \
		libxslt-dev \
		libxml2-dev \
		postgresql-dev \
		libffi \
		libffi-dev \
		util-linux \
		ffmpeg\
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps


COPY .. .
EXPOSE 9999
RUN ["chmod", "+x", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]