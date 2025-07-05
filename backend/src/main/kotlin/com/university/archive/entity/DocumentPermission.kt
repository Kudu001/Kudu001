package com.university.archive.entity

import jakarta.persistence.*
import org.springframework.data.annotation.CreatedDate
import org.springframework.data.jpa.domain.support.AuditingEntityListener
import java.time.Instant
import java.util.*

@Entity
@Table(
    name = "document_permissions",
    uniqueConstraints = [
        UniqueConstraint(columnNames = ["document_id", "user_id", "permission_type"])
    ]
)
@EntityListeners(AuditingEntityListener::class)
data class DocumentPermission(
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    val id: UUID = UUID.randomUUID(),
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "document_id", nullable = false)
    val document: Document? = null,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    val user: User? = null,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "permission_type", nullable = false, length = 20)
    val permissionType: PermissionType = PermissionType.READ,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "granted_by", nullable = false)
    val grantedBy: User? = null,
    
    @CreatedDate
    @Column(name = "granted_at", nullable = false, updatable = false)
    val grantedAt: Instant = Instant.now()
)

enum class PermissionType {
    read, write, admin
}