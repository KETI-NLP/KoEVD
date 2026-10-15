FROM python:3.12-slim
RUN useradd --create-home --uid 1000 appuser
WORKDIR /home/appuser/app
COPY apps/spaces/registered.requirements.lock.txt /tmp/koevd-requirements.txt
RUN pip install --no-cache-dir -r /tmp/koevd-requirements.txt
COPY --chown=appuser:appuser pyproject.toml README.md LICENSE DATA_LICENSE.md NOTICE.md ./
COPY --chown=appuser:appuser LICENSES ./LICENSES
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser configs ./configs
COPY --chown=appuser:appuser operator-data ./operator-data
COPY --chown=appuser:appuser apps/spaces/registered_launch.py ./launch.py
COPY --chown=appuser:appuser apps/spaces/public_launch.py ./public_launch.py
RUN pip install --no-cache-dir --no-deps .
USER appuser
ENV PYTHONUNBUFFERED=1 HF_HUB_DISABLE_TELEMETRY=1
EXPOSE 7860
CMD ["python", "launch.py"]
