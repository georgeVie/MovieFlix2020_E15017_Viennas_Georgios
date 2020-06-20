FROM mongo
COPY users.json /users.json
COPY movies.json /movies.json
RUN sleep 3
CMD ["sh", "-c", "mongoimport --host=mongodb --db=movieFlixDB --collection=Users --file=users.json --jsonArray && mongoimport --host=mongodb --db=movieFlixDB --collection=Movies --file=movies.json --jsonArray"]