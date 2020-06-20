FROM mongo
COPY users.json /users.json
RUN sleep 3
CMD mongoimport --host=mongodb --db=movieFlixDB --collection=Users --file=users.json --jsonArray

FROM mongo
COPY movies.json /movies.json
CMD mongoimport --host=mongodb --db=movieFlixDB --collection=Movies --file=movies.json --jsonArray