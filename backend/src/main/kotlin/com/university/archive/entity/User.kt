package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.annotation.LastModifiedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(name = "users")
@EntityListeners(AuditingEntityListener::class)
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @Column(nullable = false, unique = true)
    val email: String = "",
    
    @Column(name = "password_hash", nullable = false)
    val passwordHash: String = "",
    
    @Column(name = "first_name", nullable = false)
    val firstName: String = "",
    
    @Column(name = "last_name", nullable = false)
    val lastName: String = "",
    
    @Enumerated(EnumType.STRING)
    val role: UserRole = UserRole.STUDENT,
    
    @Column(name = "university_id")
    val universityId: String? = null,
    
    val department: String? = null,
    
    @Column(name = "is_active")
    val isActive: Boolean = true,
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: Instant = Instant.now(),
    
    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    val updatedAt: Instant = Instant.now()
) {
    // One-to-many relationships
    @OneToMany(mappedBy = "uploadedBy", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val uploadedDocuments: List<Document> = mutableListOf()
    
    @OneToMany(mappedBy = "requestedBy", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val plagiarismJobs: List<PlagiarismJob> = mutableListOf()
    
    @OneToMany(mappedBy = "reviewer", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val documentReviews: List<DocumentReview> = mutableListOf()
}

enum class UserRole {
    STUDENT, FACULTY, ADMIN
}