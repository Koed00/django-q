FROM sphinxdoc/sphinx

RUN mkdir -p /docs
WORKDIR /docs
COPY . .
RUN pip3 install -r requirements.txt
RUN make html
