# Separate opt-in candidate. Requires operator-data/managed.json and backup roles.
# This image is not the currently running private development Space.
FROM python:3.12-slim
RUN useradd --create-home --uid 1000 appuser
WORKDIR /home/appuser/app
COPY apps/spaces/managed.requirements.lock.txt /tmp/koevd-managed-requirements.txt
RUN pip install --no-cache-dir -r /tmp/koevd-managed-requirements.txt
COPY --chown=appuser:appuser pyproject.toml README.md LICENSE DATA_LICENSE.md NOTICE.md ./
COPY --chown=appuser:appuser LICENSES ./LICENSES
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser configs ./configs
COPY --chown=appuser:appuser operator-data ./operator-data
COPY --chown=appuser:appuser apps/spaces/managed_launch.py ./managed_launch.py
RUN pip install --no-cache-dir --no-deps .
USER appuser
ENV PYTHONUNBUFFERED=1
EXPOSE 7860
CMD ["python", "managed_launch.py", "--config", "operator-data/managed.json"]
