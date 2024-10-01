# The builder image to build virtual environment
FROM python:3.11-slim-bullseye as builder

RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN --mount=type=bind,source=requirments.txt,target=requirements.txt \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# The runtime image, run app using virtual env created
FROM python:3.11-slim-buster as runtime
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["chainlit", "run", "demo_app/main.py"]