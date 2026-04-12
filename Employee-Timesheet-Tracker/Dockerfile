FROM amazoncorretto:11

WORKDIR /app

COPY src/main/java/*.java ./
COPY src/main/resources/ ./resources/

RUN javac *.java

EXPOSE 8080

CMD ["java", "TimesheetServer"]