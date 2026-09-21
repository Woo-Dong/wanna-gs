# 홍보 이미지 생성 기록

2026-09-21. imagegen 스킬의 built-in image_gen 편집 모드 사용. CLI/API 키 방식은 사용하지 않았다. 이 파일과 이미지는 프로젝트의 디자인 참고이며 앱 구현·기능 검증 증거가 아니다.

- 최초 고객 제공 UX 참고: `wanna-gs-ux-reference.png`.
- 색상 보정 결과: `wanna-gs-promo-cyan.png`.
- 최종 캐릭터 포함 컨셉: `wanna-gs-promo-mascot.png`.
- 캐릭터 정보 근거: [GS리테일 보도자료](https://www.newswire.co.kr/newsRead.php?no=982245). 무무씨를 참고한 생성 일러스트이며 공식 원본과 동일성을 보장하지 않는다.
- 시각 확인: 네 화면·시안/블루·원하지쓰 안내·입력 예시·48시간·모의 표시 유지. 생성 이미지의 작은 글자와 숫자는 구현 시 원장/DB에서 다시 렌더링한다. 앱 접근성/색 대비 검증은 별도다.

## 색상 편집 프롬프트

```text
Edit this existing Korean WANNA GS app promotional concept image. Change ONLY its color palette to closely evoke the official 우리동네GS app's bright cyan and sky blue branding, replacing the dominant mint green/greenish teal cast. Preserve the exact overall composition, all four phone mockups, all Korean text, typography, all product names, data, footer disclaimer and especially the visible pronunciation ‘원하지쓰’라고 읽어요. Preserve photographic product/package colors and the GS25 logo. Use bright cyan approximately #00B9D6 for brand accents, sky blue and deeper blue approximately #008AC4 or #007A9E for primary action buttons, very pale cool blue #E3F7FC backgrounds, dark navy #123344 text, clean white cards. These are creative approximate palette targets, not certified official brand tokens. Replace green-tinted backgrounds and teal interface areas with clean cyan/blue, making the whole poster unmistakably blue/cyan rather than mint. Maintain readable contrast, sharp Korean lettering, and the exact screen content and dimensions. Success check can remain semantic green but do not let green dominate. Do not introduce new elements or change wording.
```

## 캐릭터 추가 최종 프롬프트

```text
Use case: precise-object-edit. Edit the provided cyan/blue WANNA GS promotional poster. Keep all existing phone screen content, all typography, all Korean wording including ‘원하지쓰’라고 읽어요, product photos, four-phone layout, white cards and bright cyan/blue palette unchanged. Add two small tasteful depictions of GS25's Korean mascot 무무씨 (Moomoossi / Serious Fox), the orange Tibetan fox with a broad squared fluffy cream cheek/muzzle area, narrow half-lidded horizontal eyes, deadpan nonchalant expression, pointed orange ears and short rounded body. This is a concept illustration inspired by the mascot, not a licensed asset reproduction. Add a small mascot sitting in unused upper-left space between the handwritten copy and the title, with a small cyan shopping bag; add a tiny head peeking beside the phone-three merchant heading only where no text or button is obscured. Character warmth must not replace the dominant cyan palette. Preserve uncluttered reading and all information. Do not use a yellow rabbit or Kakao Muzi, do not invent a mascot label. Do not add any other copy, logos, UI functions, or characters. Do not hide titles, input examples, counts, dates, buttons, consent or footer. Keep 1536x1024 landscape composition.
```
