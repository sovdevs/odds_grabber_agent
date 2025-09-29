FROM apify/actor-python:3.11

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything (src, configs, etc.)
COPY . ./

CMD ["python3", "-m", "src.main"]