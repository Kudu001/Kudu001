package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(name = "document_tags")
@EntityListeners(AuditingEntityListener::class)
data class DocumentTag(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @Column(nullable = false, unique = true, length = 100)
    val name: String = "",
    
    @Column(length = 7)
    val color: String = "#007bff",
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now()
) {
    @ManyToMany(mappedBy = "tags", fetch = FetchType.LAZY)
    val documents: Set<Document> = mutableSetOf()
}