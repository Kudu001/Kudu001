package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.math.BigDecimal
import java.time.Instant
import java.util.*

@Entity
@Table(name = "plagiarism_results")
@EntityListeners(AuditingEntityListener::class)
data class PlagiarismResult(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_id", nullable = false)
    val job: PlagiarismJob? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "source_document_id", nullable = false)
    val sourceDocument: Document? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "matched_document_id", nullable = false)
    val matchedDocument: Document? = null,
    
    @Column(name = "similarity_score", nullable = false, precision = 5, scale = 4)
    val similarityScore: BigDecimal = BigDecimal.ZERO,
    
    @Column(name = "matched_text_segments", columnDefinition = "jsonb")
    val matchedTextSegments: String? = null,
    
    @Column(name = "detection_method", nullable = false, length = 50)
    val detectionMethod: String = "",
    
    @Column(name = "confidence_score", precision = 5, scale = 4)
    val confidenceScore: BigDecimal? = null,
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now()
)