FROM python:3.12.1-alpine3.19
ENV PR_REMINDERS_CONFIG_PATH="/app/config/config.json"

RUN addgroup --gid 555 --system pr-reminders && \
    adduser --disabled-password --home /home/pr-reminders --system --ingroup pr-reminders --uid 555 pr-reminders
USER 555:555
WORKDIR /app
RUN mkdir config
COPY --chown=555:555 ./example/config.json ./config/config.json
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir -r /tmp/requirements.txt
COPY --chown=555:555 ./pr-reminders ./pr-reminders


ENTRYPOINT ["python", "/app/pr-reminders/main.py"]
