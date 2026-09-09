package org.springframework.samples.petclinic.visit;

import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import org.springframework.samples.petclinic.model.BaseEntity;

/**
 * PetClinic Visit(진료 방문) entity (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0), 데모용으로 축약·개변.
 *
 * 의도적 충돌 맥락:
 *   - description: @Size(max = 8192) -> 명세(visit-scheduling-spec.pdf: 255자)와 불일치 (충돌 C-4, value_mismatch)
 *   - date: 과거일자 예약 금지 검증 없음 -> maintenance-notes VISIT-RULE-1 과 드리프트 (충돌 C-6, stale_knowledge)
 */
@Entity
@Table(name = "visits")
public class Visit extends BaseEntity {

    // 충돌 C-6: 명세/노트는 "과거 일자 예약 금지"를 요구하나, 미래/과거 검증 애너테이션이 없음.
    @NotNull
    @Column(name = "visit_date")
    private LocalDate date = LocalDate.now();

    // 충돌 C-4: 명세는 최대 255자이나 구현은 8192자를 허용.
    @Size(max = 8192)
    private String description;

    @Column(name = "pet_id")
    private Integer petId;

    public LocalDate getDate() {
        return date;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getPetId() {
        return petId;
    }

    public void setPetId(Integer petId) {
        this.petId = petId;
    }
}
