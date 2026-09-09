// PetClinic (TRACE demo excerpt) — spring-petclinic-rest (Apache-2.0), 데모용 축약.
package org.springframework.samples.petclinic.billing;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class BillingServiceTests {

    @Mock
    private BillingRepository invoices;

    @InjectMocks
    private BillingService service;

    private static InvoiceItem item(String description, String amount) {
        InvoiceItem it = new InvoiceItem();
        it.setDescription(description);
        it.setAmount(new BigDecimal(amount));
        return it;
    }

    @Test
    void computeTotalSumsAmounts() {
        List<InvoiceItem> items = List.of(item("consult", "40.00"), item("vaccine", "25.50"));

        BigDecimal total = service.computeTotal(items);

        assertThat(total).isEqualByComparingTo("65.50");
    }

    @Test
    void computeTotalOfEmptyListIsZero() {
        assertThat(service.computeTotal(List.of())).isEqualByComparingTo("0");
    }

    @Test
    void computeTotalOfNullIsZero() {
        assertThat(service.computeTotal(null)).isEqualByComparingTo("0");
    }
}
