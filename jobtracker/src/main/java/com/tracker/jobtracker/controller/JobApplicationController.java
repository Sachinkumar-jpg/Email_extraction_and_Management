package com.tracker.jobtracker.controller;

import com.tracker.jobtracker.model.JobApplication;
import com.tracker.jobtracker.repository.JobApplicationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/applications")
@CrossOrigin(origins = "*")
public class JobApplicationController {

    @Autowired
    private JobApplicationRepository repository;

    @GetMapping
    public List<JobApplication> getAll() {
        return repository.findAll();
    }

    @PostMapping
    public JobApplication create(@RequestBody JobApplication job) {
        return repository.save(job);
    }

    @PutMapping("/{id}")
    public JobApplication update(@PathVariable Long id, @RequestBody JobApplication updated) {
        JobApplication job = repository.findById(id).orElse(null);
        if (job != null) {
            job.setCompanyName(updated.getCompanyName());
            job.setDateApplied(updated.getDateApplied());
            job.setDaysSinceUpdate(updated.getDaysSinceUpdate());
            job.setRoleAppliedFor(updated.getRoleAppliedFor());
            job.setStatus(updated.getStatus());
            System.out.println(job);
            return repository.save(job);
        }
        return null;
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        repository.deleteById(id);
    }
}
