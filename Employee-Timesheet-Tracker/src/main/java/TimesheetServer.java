import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.*;
import java.net.InetSocketAddress;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.nio.file.Files;
import java.nio.file.Paths;

public class TimesheetServer {
    private static final Map<String, List<TimesheetEntry>> timesheets = new ConcurrentHashMap<>();
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

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
        
        server.createContext("/", new StaticFileHandler());
        server.createContext("/api/timesheets", new TimesheetHandler());
        
        server.setExecutor(null);
        server.start();
        System.out.println("Server started on http://localhost:8080");
    }

    static class StaticFileHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String path = exchange.getRequestURI().getPath();
            if (path.equals("/")) path = "/index.html";
            
            String resourcePath = "resources/static" + path;
            File file = new File(resourcePath);
            
            if (file.exists() && file.isFile()) {
                String contentType = getContentType(path);
                exchange.getResponseHeaders().set("Content-Type", contentType);
                exchange.sendResponseHeaders(200, file.length());
                Files.copy(file.toPath(), exchange.getResponseBody());
            } else {
                String response = "404 Not Found";
                exchange.sendResponseHeaders(404, response.length());
                exchange.getResponseBody().write(response.getBytes());
            }
            exchange.getResponseBody().close();
        }

        private String getContentType(String path) {
            if (path.endsWith(".html")) return "text/html";
            if (path.endsWith(".css")) return "text/css";
            if (path.endsWith(".js")) return "application/javascript";
            return "text/plain";
        }
    }

    static class TimesheetHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String method = exchange.getRequestMethod();
            exchange.getResponseHeaders().set("Content-Type", "application/json");
            exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
            exchange.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
            exchange.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");

            if ("OPTIONS".equals(method)) {
                exchange.sendResponseHeaders(200, 0);
                exchange.getResponseBody().close();
                return;
            }

            switch (method) {
                case "GET":
                    handleGet(exchange);
                    break;
                case "POST":
                    handlePost(exchange);
                    break;
                case "DELETE":
                    handleDelete(exchange);
                    break;
                default:
                    exchange.sendResponseHeaders(405, 0);
                    exchange.getResponseBody().close();
            }
        }

        private void handleGet(HttpExchange exchange) throws IOException {
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
            exchange.getResponseBody().close();
        }

        private void handlePost(HttpExchange exchange) throws IOException {
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
            
            exchange.sendResponseHeaders(201, entry.toJson().length());
            exchange.getResponseBody().write(entry.toJson().getBytes());
            exchange.getResponseBody().close();
        }

        private void handleDelete(HttpExchange exchange) throws IOException {
            String query = exchange.getRequestURI().getQuery();
            if (query != null && query.startsWith("id=")) {
                String id = query.substring(3);
                boolean removed = false;
                
                for (List<TimesheetEntry> entries : timesheets.values()) {
                    removed = entries.removeIf(entry -> entry.id.equals(id));
                    if (removed) break;
                }
                
                if (removed) {
                    exchange.sendResponseHeaders(200, 0);
                } else {
                    exchange.sendResponseHeaders(404, 0);
                }
            } else {
                exchange.sendResponseHeaders(400, 0);
            }
            exchange.getResponseBody().close();
        }
    }
}