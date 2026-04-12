@echo off
echo Compiling Java server...
cd src\main\java
javac TimesheetServer.java
echo Starting server...
java TimesheetServer
pause