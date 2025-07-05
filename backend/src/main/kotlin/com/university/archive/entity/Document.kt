package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.annotation.LastModifiedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(name = "documents")
@EntityListeners(AuditingEntityListener::class)
data class Document(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @Column(nullable = false, length = 500)
    val title: String = "",
    
    @Column(columnDefinition = "TEXT")
    val description: String? = null,
    
    @Column(name = "original_filename", nullable = false)
    val originalFilename: String = "",
    
    @Column(name = "file_type", nullable = false, length = 10)
    val fileType: String = "",
    
    @Column(name = "file_size_bytes", nullable = false)
    val fileSizeBytes: Long = 0,
    
    @Column(name = "s3_bucket", nullable = false, length = 100)
    val s3Bucket: String = "",
    
    @Column(name = "s3_key", nullable = false, length = 500)
    val s3Key: String = "",
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "uploaded_by", nullable = false)
    val uploadedBy: User? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    val category: DocumentCategory? = null,
    
    @Column(name = "course_code", length = 20)
    val courseCode: String? = null,
    
    @Column(name = "academic_year", length = 20)
    val academicYear: String? = null,
    
    @Column(length = 20)
    val semester: String? = null,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "document_type", length = 50)
    val documentType: DocumentType? = null,
    
    @Column(name = "is_public")
    val isPublic: Boolean = false,
    
    @Column(name = "content_extracted", columnDefinition = "TEXT")
    val contentExtracted: String? = null,
    
    @Column(length = 10)
    val language: String = "en",
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now(),
    
    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: Instant = Instant.now()
) {
    // One-to-many relationships
    @OneToMany(mappedBy = "document", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val plagiarismJobs: List<PlagiarismJob> = mutableListOf()
    
    @OneToMany(mappedBy = "document", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val permissions: List<DocumentPermission> = mutableListOf()
    
    @OneToMany(mappedBy = "document", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val reviews: List<DocumentReview> = mutableListOf()
    
    // Many-to-many relationships
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "document_tag_mappings",
        joinColumns = [JoinColumn(name = "document_id")],
        inverseJoinColumns = [JoinColumn(name = "tag_id")]
    )
    val tags: Set<DocumentTag> = mutableSetOf()
}

enum class DocumentType {
    THESIS, DISSERTATION, RESEARCH_PAPER, ASSIGNMENT, PROJECT_REPORT, OTHER
}