# Build context: materialized development Space root with pinned operator-data.
FROM python:3.12-slim
RUN useradd --create-home --uid 1000 appuser
WORKDIR /home/appuser/app
COPY apps/spaces/requirements.lock.txt /tmp/koevd-web-requirements.txt
RUN pip install --no-cache-dir -r /tmp/koevd-web-requirements.txt
COPY --chown=appuser:appuser pyproject.toml README.md LICENSE DATA_LICENSE.md NOTICE.md ./
COPY --chown=appuser:appuser LICENSES ./LICENSES
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser configs ./configs
COPY --chown=appuser:appuser operator-data ./operator-data
COPY --chown=appuser:appuser apps/spaces/launch.py ./launch.py
RUN pip install --no-cache-dir --no-deps .
USER appuser
ENV PYTHONUNBUFFERED=1
EXPOSE 7860
# Native HF OAuth + SPACE_HOST; development submissions use temporary disk only.
CMD ["python", "launch.py"]
