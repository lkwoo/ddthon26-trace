package org.springframework.samples.petclinic.billing;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

import org.springframework.samples.petclinic.model.BaseEntity;

/**
 * PetClinic Invoice(청구서) entity (TRACE demo excerpt).
 * 원본: spring-petclinic-rest (Apache-2.0) 스타일의 데모용 합성 확장(청구 도메인).
 *
 * 의도적 충돌 맥락 (충돌 C-7, value_mismatch):
 *   billing-spec.pdf 는 통화 금액을 DECIMAL(10,2)로 규정하나, 아래 매핑과 db/schema.sql 은
 *   DECIMAL(8,2)로 정의되어 있다. 고액 청구 시 반올림/오버플로 위험 => 명세-구현 값 불일치.
 */
@Entity
@Table(name = "invoices")
public class Invoice extends BaseEntity {

    @Column(name = "owner_id")
    private Integer ownerId;

    @Column(name = "issued_on")
    private LocalDate issuedOn = LocalDate.now();

    // 충돌 C-7: 명세는 precision=10 이나 구현은 precision=8 (scale=2 동일).
    @Column(name = "amount", precision = 8, scale = 2)
    private BigDecimal amount = BigDecimal.ZERO;

    private final List<InvoiceItem> items = new ArrayList<>();

    public Integer getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(Integer ownerId) {
        this.ownerId = ownerId;
    }

    public LocalDate getIssuedOn() {
        return issuedOn;
    }

    public void setIssuedOn(LocalDate issuedOn) {
        this.issuedOn = issuedOn;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public List<InvoiceItem> getItems() {
        return items;
    }
}
