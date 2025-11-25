FROM python:3.11-slim
WORKDIR /workspace
COPY . /workspace
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["bash"]
