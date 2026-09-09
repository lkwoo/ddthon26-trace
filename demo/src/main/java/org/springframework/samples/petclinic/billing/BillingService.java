// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.billing;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Application service for invoice totals.
 */
@Service
public class BillingService {

    private final BillingRepository invoices;

    public BillingService(BillingRepository invoices) {
        this.invoices = invoices;
    }

    /**
     * Sums the amounts of the supplied line items, treating null amounts as zero.
     */
    public BigDecimal computeTotal(List<InvoiceItem> items) {
        BigDecimal total = BigDecimal.ZERO;
        if (items == null) {
            return total;
        }
        for (InvoiceItem item : items) {
            BigDecimal amount = item.getAmount();
            if (amount != null) {
                total = total.add(amount);
            }
        }
        return total;
    }

    @Transactional(readOnly = true)
    public BigDecimal totalForInvoice(int invoiceId) {
        Invoice invoice = invoices.findById(invoiceId)
                .orElseThrow(() -> new IllegalArgumentException("Invoice not found: " + invoiceId));
        return computeTotal(invoice.getItems());
    }
}
