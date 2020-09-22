FROM rappdw/docker-java-python:openjdk1.8.0_171-python3.6.6
RUN java -version
RUN python --version
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
