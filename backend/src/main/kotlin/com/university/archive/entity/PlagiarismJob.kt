package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(name = "plagiarism_jobs")
@EntityListeners(AuditingEntityListener::class)
data class PlagiarismJob(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "document_id", nullable = false)
    val document: Document? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "requested_by", nullable = false)
    val requestedBy: User? = null,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    val status: PlagiarismJobStatus = PlagiarismJobStatus.PENDING,
    
    @Column(name = "started_at")
    val startedAt: Instant? = null,
    
    @Column(name = "completed_at")
    val completedAt: Instant? = null,
    
    @Column(name = "error_message", columnDefinition = "TEXT")
    val errorMessage: String? = null,
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now()
) {
    @OneToMany(mappedBy = "job", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val results: List<PlagiarismResult> = mutableListOf()
}

enum class PlagiarismJobStatus {
    PENDING, PROCESSING, COMPLETED, FAILED
}