package com.tracker.jobtracker.model;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
public class JobApplication {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String companyName;
    private String roleAppliedFor;
    private String dateApplied;
    private String status;
    private int daysSinceUpdate;
}

