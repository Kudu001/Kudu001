package com.university.archive

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.data.jpa.repository.config.EnableJpaRepositories
import org.springframework.scheduling.annotation.EnableAsync

@SpringBootApplication
@EnableJpaRepositories
@EnableAsync
class UniversityArchiveApplication

fun main(args: Array<String>) {
    runApplication<UniversityArchiveApplication>(*args)
}