FROM postgres:9.5
ADD remote_connections.sh /docker-entrypoint-initdb.d/
RUN chmod 755 /docker-entrypoint-initdb.d/remote_connections.sh
ADD init.sql /docker-entrypoint-initdb.d/
