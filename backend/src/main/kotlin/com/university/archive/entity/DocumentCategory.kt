package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(name = "document_categories")
@EntityListeners(AuditingEntityListener::class)
data class DocumentCategory(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @Column(nullable = false, unique = true, length = 100)
    val name: String = "",
    
    @Column(columnDefinition = "TEXT")
    val description: String? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_category_id")
    val parentCategory: DocumentCategory? = null,
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now()
) {
    @OneToMany(mappedBy = "parentCategory", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val subCategories: List<DocumentCategory> = mutableListOf()
    
    @OneToMany(mappedBy = "category", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val documents: List<Document> = mutableListOf()
}