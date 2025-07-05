package com.university.archive.repository

import com.university.archive.entity.Document
import com.university.archive.entity.DocumentType
import com.university.archive.entity.User
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.util.*

@Repository
interface DocumentRepository : JpaRepository<Document, UUID> {
    
    fun findByUploadedBy(user: User, pageable: Pageable): Page<Document>
    
    fun findByDocumentType(documentType: DocumentType, pageable: Pageable): Page<Document>
    
    fun findByIsPublic(isPublic: Boolean, pageable: Pageable): Page<Document>
    
    fun findByCourseCode(courseCode: String, pageable: Pageable): Page<Document>
    
    fun findByAcademicYear(academicYear: String, pageable: Pageable): Page<Document>
    
    @Query("SELECT d FROM Document d WHERE d.title LIKE %:title%")
    fun findByTitleContaining(@Param("title") title: String, pageable: Pageable): Page<Document>
    
    @Query("SELECT d FROM Document d WHERE " +
           "LOWER(d.title) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(d.description) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(d.contentExtracted) LIKE LOWER(CONCAT('%', :query, '%'))")
    fun searchDocuments(@Param("query") query: String, pageable: Pageable): Page<Document>
    
    @Query("SELECT d FROM Document d WHERE " +
           "d.category.id = :categoryId AND d.isPublic = true")
    fun findByCategoryAndPublic(@Param("categoryId") categoryId: UUID, pageable: Pageable): Page<Document>
    
    @Query("SELECT d FROM Document d WHERE " +
           "d.documentType = :type AND d.academicYear = :year")
    fun findByTypeAndYear(@Param("type") type: DocumentType, @Param("year") year: String, pageable: Pageable): Page<Document>
    
    @Query("SELECT d FROM Document d JOIN d.tags t WHERE t.name = :tagName")
    fun findByTagName(@Param("tagName") tagName: String, pageable: Pageable): Page<Document>
    
    fun countByUploadedBy(user: User): Long
    
    fun countByDocumentType(documentType: DocumentType): Long
}