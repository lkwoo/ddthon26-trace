// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.billing;

import org.springframework.stereotype.Component;

/**
 * Maps the Invoice entity to its DTO.
 */
@Component
public class BillingMapper {

    public InvoiceDto toDto(Invoice invoice) {
        if (invoice == null) {
            return null;
        }
        InvoiceDto dto = new InvoiceDto();
        dto.setId(invoice.getId());
        dto.setTotal(invoice.getAmount());
        for (InvoiceItem item : invoice.getItems()) {
            dto.getLineDescriptions().add(item.getDescription());
        }
        return dto;
    }
}
