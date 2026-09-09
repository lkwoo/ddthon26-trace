// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.billing;

import java.math.BigDecimal;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing invoice totals.
 */
@RestController
@RequestMapping("/api/invoices")
public class BillingRestController {

    private final BillingRepository invoices;
    private final BillingService billing;
    private final BillingMapper mapper;

    public BillingRestController(BillingRepository invoices, BillingService billing, BillingMapper mapper) {
        this.invoices = invoices;
        this.billing = billing;
        this.mapper = mapper;
    }

    @GetMapping("/{invoiceId}")
    public ResponseEntity<InvoiceDto> getInvoice(@PathVariable int invoiceId) {
        return invoices.findById(invoiceId)
                .map(mapper::toDto)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @GetMapping("/{invoiceId}/total")
    public ResponseEntity<BigDecimal> getInvoiceTotal(@PathVariable int invoiceId) {
        try {
            return ResponseEntity.ok(billing.totalForInvoice(invoiceId));
        } catch (IllegalArgumentException ex) {
            return ResponseEntity.notFound().build();
        }
    }
}
