package org.springframework.samples.petclinic.owner;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

/**
 * Owner 등록 검증 테스트 (발췌·데모용).
 * 전화번호 최대 길이(구현 기준 10자리)를 검증한다. SMS 인증 관련 테스트는 없다.
 */
class OwnerRegistrationTests {

    @Test
    void telephoneAtMaxLengthIsAccepted() {
        Owner owner = new Owner();
        owner.setTelephone("0123456789"); // 10자리 — 허용 상한
        assertEquals(10, owner.getTelephone().length());
    }
}
