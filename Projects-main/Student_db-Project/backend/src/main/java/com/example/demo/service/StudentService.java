package com.example.demo.service;

import com.example.demo.entity.Student;
import com.example.demo.repository.StudentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class StudentService {

    @Autowired
    private StudentRepository repo;

    // Save student
    public Student save(Student s) {
        return repo.save(s);
    }

    // Get all students
    public List<Student> getAll() {
        return repo.findAll();
    }
}
