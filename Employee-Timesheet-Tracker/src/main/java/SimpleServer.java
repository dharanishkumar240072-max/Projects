import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.*;
import java.net.InetSocketAddress;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SimpleServer {
    private static final Map<String, List<TimesheetEntry>> timesheets = new ConcurrentHashMap<>();

    static class TimesheetEntry {
        String id;
        String employee;
        String date;
        String startTime;
        String endTime;
        String description;
        double hours;

        TimesheetEntry(String employee, String date, String startTime, String endTime, String description) {
            this.id = UUID.randomUUID().toString();
            this.employee = employee;
            this.date = date;
            this.startTime = startTime;
            this.endTime = endTime;
            this.description = description;
            this.hours = calculateHours(startTime, endTime);
        }

        private double calculateHours(String start, String end) {
            try {
                String[] startParts = start.split(":");
                String[] endParts = end.split(":");
                int startMinutes = Integer.parseInt(startParts[0]) * 60 + Integer.parseInt(startParts[1]);
                int endMinutes = Integer.parseInt(endParts[0]) * 60 + Integer.parseInt(endParts[1]);
                return (endMinutes - startMinutes) / 60.0;
            } catch (Exception e) {
                return 0.0;
            }
        }

        String toJson() {
            return String.format("{\"id\":\"%s\",\"employee\":\"%s\",\"date\":\"%s\",\"startTime\":\"%s\",\"endTime\":\"%s\",\"description\":\"%s\",\"hours\":%.2f}",
                    id, employee, date, startTime, endTime, description, hours);
        }
    }

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        
        server.createContext("/", new HomeHandler());
        server.createContext("/api/timesheets", new TimesheetHandler());
        
        server.setExecutor(null);
        server.start();
        System.out.println("Server started on http://localhost:8080");
    }

    static class HomeHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String html = "<!DOCTYPE html><html><head><title>Employee Timesheet Tracker</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f5f5f5;padding:20px}.container{max-width:1200px;margin:0 auto}h1{text-align:center;color:#333;margin-bottom:30px}.form-section{background:white;padding:20px;border-radius:8px;margin-bottom:20px}.form-group{margin-bottom:15px}label{display:block;margin-bottom:5px;font-weight:bold}input,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:4px}button{background:#007bff;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer}button:hover{background:#0056b3}table{width:100%;border-collapse:collapse;background:white}th,td{padding:10px;text-align:left;border-bottom:1px solid #ddd}th{background:#f8f9fa}.delete-btn{background:#dc3545;padding:5px 10px;font-size:12px}.delete-btn:hover{background:#c82333}</style></head><body><div class='container'><h1>Employee Timesheet Tracker</h1><div class='form-section'><form id='form'><div class='form-group'><label>Employee:</label><input type='text' id='employee' required></div><div class='form-group'><label>Date:</label><input type='date' id='date' required></div><div class='form-group'><label>Start Time:</label><input type='time' id='startTime' required></div><div class='form-group'><label>End Time:</label><input type='time' id='endTime' required></div><div class='form-group'><label>Description:</label><textarea id='description' required></textarea></div><button type='submit'>Add Entry</button></form></div><table><thead><tr><th>Employee</th><th>Date</th><th>Start</th><th>End</th><th>Hours</th><th>Description</th><th>Action</th></tr></thead><tbody id='tbody'></tbody></table></div><script>const form=document.getElementById('form');const tbody=document.getElementById('tbody');form.addEventListener('submit',e=>{e.preventDefault();const data=new URLSearchParams({employee:document.getElementById('employee').value,date:document.getElementById('date').value,startTime:document.getElementById('startTime').value,endTime:document.getElementById('endTime').value,description:document.getElementById('description').value});fetch('/api/timesheets',{method:'POST',body:data}).then(()=>{form.reset();loadData()})});function loadData(){fetch('/api/timesheets').then(r=>r.json()).then(data=>{tbody.innerHTML='';data.forEach(entry=>{tbody.innerHTML+=`<tr><td>${entry.employee}</td><td>${entry.date}</td><td>${entry.startTime}</td><td>${entry.endTime}</td><td>${entry.hours.toFixed(2)}</td><td>${entry.description}</td><td><button class='delete-btn' onclick='deleteEntry(\"${entry.id}\")'>Delete</button></td></tr>`})})}function deleteEntry(id){if(confirm('Delete?')){fetch(`/api/timesheets?id=${id}`,{method:'DELETE'}).then(()=>loadData())}}loadData();</script></body></html>";
            
            exchange.getResponseHeaders().set("Content-Type", "text/html");
            exchange.sendResponseHeaders(200, html.length());
            exchange.getResponseBody().write(html.getBytes());
            exchange.getResponseBody().close();
        }
    }

    static class TimesheetHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String method = exchange.getRequestMethod();
            exchange.getResponseHeaders().set("Content-Type", "application/json");

            switch (method) {
                case "GET":
                    StringBuilder response = new StringBuilder("[");
                    boolean first = true;
                    for (List<TimesheetEntry> entries : timesheets.values()) {
                        for (TimesheetEntry entry : entries) {
                            if (!first) response.append(",");
                            response.append(entry.toJson());
                            first = false;
                        }
                    }
                    response.append("]");
                    
                    exchange.sendResponseHeaders(200, response.length());
                    exchange.getResponseBody().write(response.toString().getBytes());
                    break;
                    
                case "POST":
                    String body = new String(exchange.getRequestBody().readAllBytes());
                    String[] params = body.split("&");
                    Map<String, String> data = new HashMap<>();
                    
                    for (String param : params) {
                        String[] kv = param.split("=");
                        if (kv.length == 2) {
                            data.put(kv[0], java.net.URLDecoder.decode(kv[1], "UTF-8"));
                        }
                    }

                    String employee = data.get("employee");
                    TimesheetEntry entry = new TimesheetEntry(
                        employee,
                        data.get("date"),
                        data.get("startTime"),
                        data.get("endTime"),
                        data.get("description")
                    );

                    timesheets.computeIfAbsent(employee, k -> new ArrayList<>()).add(entry);
                    
                    exchange.sendResponseHeaders(201, 0);
                    break;
                    
                case "DELETE":
                    String query = exchange.getRequestURI().getQuery();
                    if (query != null && query.startsWith("id=")) {
                        String id = query.substring(3);
                        for (List<TimesheetEntry> entries : timesheets.values()) {
                            if (entries.removeIf(e -> e.id.equals(id))) break;
                        }
                    }
                    exchange.sendResponseHeaders(200, 0);
                    break;
            }
            exchange.getResponseBody().close();
        }
    }
}