package com.university.archive.repository

import com.university.archive.entity.Document
import com.university.archive.entity.PlagiarismJob
import com.university.archive.entity.PlagiarismJobStatus
import com.university.archive.entity.User
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.time.Instant
import java.util.*

@Repository
interface PlagiarismJobRepository : JpaRepository<PlagiarismJob, UUID> {
    
    fun findByDocument(document: Document): List<PlagiarismJob>
    
    fun findByRequestedBy(user: User, pageable: Pageable): Page<PlagiarismJob>
    
    fun findByStatus(status: PlagiarismJobStatus): List<PlagiarismJob>
    
    fun findByStatusOrderByCreatedAtAsc(status: PlagiarismJobStatus): List<PlagiarismJob>
    
    @Query("SELECT pj FROM PlagiarismJob pj WHERE pj.document.id = :documentId ORDER BY pj.createdAt DESC")
    fun findByDocumentIdOrderByCreatedAtDesc(@Param("documentId") documentId: UUID): List<PlagiarismJob>
    
    @Query("SELECT pj FROM PlagiarismJob pj WHERE " +
           "pj.status = :status AND pj.createdAt <= :before")
    fun findOldJobsWithStatus(@Param("status") status: PlagiarismJobStatus, @Param("before") before: Instant): List<PlagiarismJob>
    
    fun existsByDocumentAndStatus(document: Document, status: PlagiarismJobStatus): Boolean
    
    fun countByStatus(status: PlagiarismJobStatus): Long
    
    fun countByRequestedBy(user: User): Long
}