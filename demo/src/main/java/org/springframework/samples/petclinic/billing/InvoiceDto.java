// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.billing;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Data transfer object for Invoice.
 */
public class InvoiceDto {

    private Integer id;

    private Integer ownerId;

    private BigDecimal total;

    private List<String> lineDescriptions = new ArrayList<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(Integer ownerId) {
        this.ownerId = ownerId;
    }

    public BigDecimal getTotal() {
        return total;
    }

    public void setTotal(BigDecimal total) {
        this.total = total;
    }

    public List<String> getLineDescriptions() {
        return lineDescriptions;
    }

    public void setLineDescriptions(List<String> lineDescriptions) {
        this.lineDescriptions = lineDescriptions;
    }
}
