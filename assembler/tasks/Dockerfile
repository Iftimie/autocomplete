FROM bde2020/hadoop-base:2.0.0-hadoop3.2.1-java8

# Download zookeeper (to access the remote cli)
RUN curl https://mirrors.up.pt/pub/apache/zookeeper/zookeeper-3.6.1/apache-zookeeper-3.6.1-bin.tar.gz -o /tmp/apache-zookeeper-3.6.1-bin.tar.gz
RUN tar -xf /tmp/apache-zookeeper-3.6.1-bin.tar.gz -C /tmp/
RUN mv /tmp/apache-zookeeper-3.6.1-bin /zookeeper
RUN rm /tmp/apache-zookeeper-3.6.1-bin.tar.gz

COPY do_tasks.sh /app/assembler/tasks/do_tasks.sh
RUN chmod a+x /app/assembler/tasks/do_tasks.sh

CMD ["/app/assembler/tasks/do_tasks.sh"]