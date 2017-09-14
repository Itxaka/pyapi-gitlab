FROM python:3

ADD . /code
WORKDIR /code

RUN pip install --no-cache-dir -r test-requirements.txt
CMD ["/bin/bash", "integration_cov"]
