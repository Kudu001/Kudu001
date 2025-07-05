package com.university.archive.repository

import com.university.archive.entity.User
import com.university.archive.entity.UserRole
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.util.*

@Repository
interface UserRepository : JpaRepository<User, UUID> {
    
    fun findByEmail(email: String): User?
    
    fun findByEmailAndIsActive(email: String, isActive: Boolean): User?
    
    fun findByUniversityId(universityId: String): User?
    
    fun findByRole(role: UserRole): List<User>
    
    fun findByDepartment(department: String): List<User>
    
    fun findByIsActive(isActive: Boolean, pageable: Pageable): Page<User>
    
    @Query("SELECT u FROM User u WHERE u.firstName LIKE %:name% OR u.lastName LIKE %:name%")
    fun findByNameContaining(@Param("name") name: String, pageable: Pageable): Page<User>
    
    @Query("SELECT u FROM User u WHERE u.role = :role AND u.department = :department")
    fun findByRoleAndDepartment(@Param("role") role: UserRole, @Param("department") department: String): List<User>
    
    fun existsByEmail(email: String): Boolean
    
    fun existsByUniversityId(universityId: String): Boolean
}