package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.annotation.LastModifiedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(
    name = "document_reviews",
    uniqueConstraints = [
        UniqueConstraint(columnNames = ["document_id", "reviewer_id"])
    ]
)
@EntityListeners(AuditingEntityListener::class)
data class DocumentReview(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "document_id", nullable = false)
    val document: Document? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reviewer_id", nullable = false)
    val reviewer: User? = null,
    
    @Column
    val rating: Int? = null,
    
    @Column(name = "review_text", columnDefinition = "TEXT")
    val reviewText: String? = null,
    
    @Column(name = "is_public")
    val isPublic: Boolean = true,
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now(),
    
    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: Instant = Instant.now()
)