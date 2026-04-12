# Employee Timesheet Tracker

A simple web application for tracking employee timesheets with Java backend and HTML/CSS/JS frontend.

## Features

- Add timesheet entries with employee name, date, start/end times, and description
- Automatic calculation of work hours
- View all timesheet entries in a table
- Delete timesheet entries
- Responsive design for mobile and desktop

## Project Structure

```
employee-timesheet-tracker/
├── src/
│   └── main/
│       ├── java/
│       │   └── TimesheetServer.java
│       └── resources/
│           └── static/
│               ├── index.html
│               ├── style.css
│               └── script.js
├── Dockerfile
└── README.md
```

## Running Locally

### Prerequisites
- Java 11 or higher

### Steps
1. Navigate to the project directory
2. Compile and run the Java server:
   ```bash
   cd src/main/java
   javac TimesheetServer.java
   java TimesheetServer
   ```
3. Open your browser and go to `http://localhost:8080`

## Running with Docker

### Build the Docker image:
```bash
docker build -t timesheet-tracker .
```

### Run the container:
```bash
docker run -p 8080:8080 timesheet-tracker
```

### Access the application:
Open your browser and go to `http://localhost:8080`

## API Endpoints

- `GET /api/timesheets` - Get all timesheet entries
- `POST /api/timesheets` - Add a new timesheet entry
- `DELETE /api/timesheets?id={id}` - Delete a timesheet entry

## Usage

1. Fill in the form with employee details:
   - Employee Name
   - Date
   - Start Time
   - End Time
   - Description of work

2. Click "Add Entry" to save the timesheet

3. View all entries in the table below

4. Click "Delete" to remove an entry

The application automatically calculates work hours based on start and end times.