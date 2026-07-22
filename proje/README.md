# STM32 Mesafe Ölçüm Projesi

Bu klasör, STM32 projesinin görsel ve dokümantasyon bölümünü içerir. Asıl STM32CubeIDE proje dosyaları [kod/](kod/) altındadır.

## Proje Özeti

- HC-SR04 sensörüne 10 µs TRIG darbesi gönderir.
- ECHO sinyalinin yükselen ve düşen kenarlarını TIM4 ile yakalar.
- Darbe süresini mikrosaniye cinsinden ölçer.
- Mesafeyi yaklaşık olarak echo süresi / 58 formülüyle cm cinsine çevirir.

## Önemli Dosyalar

| Yol | Açıklama |
| --- | --- |
| [kod/HedefTespitSistemi.ioc](kod/HedefTespitSistemi.ioc) | STM32CubeMX/STM32CubeIDE proje yapılandırması. |
| [kod/Core/Src/main.c](kod/Core/Src/main.c) | Uygulamanın ana kodu. TRIG üretimi, TIM4 kesme akışı, darbe süresi ölçümü ve mesafe hesabı burada bulunur. |
| [kod/Core/Inc/main.h](kod/Core/Inc/main.h) | Ana uygulamanın ortak başlık dosyası. Pin ve fonksiyon bildirimleri burada yer alır. |
| [kod/Core/Src/stm32f4xx_it.c](kod/Core/Src/stm32f4xx_it.c) | Kesme yönlendirmeleri ve interrupt handler yapısı. |
| [kod/Core/Src/stm32f4xx_hal_msp.c](kod/Core/Src/stm32f4xx_hal_msp.c) | HAL seviyesinde çevre birimi başlangıç ayarları. |
| [kod/Core/Startup/startup_stm32f407vgtx.s](kod/Core/Startup/startup_stm32f407vgtx.s) | Başlangıç assembly kodu ve vektör tablosu. |
| [kod/STM32F407VGTX_FLASH.ld](kod/STM32F407VGTX_FLASH.ld) | Flash bellek yerleşim dosyası. |
| [kod/STM32F407VGTX_RAM.ld](kod/STM32F407VGTX_RAM.ld) | RAM bellek yerleşim dosyası. |
| [devre_sema.jpeg](devre_sema.jpeg) | Donanım bağlantı şeması. |

## Donanım Bağlantıları

Mevcut kod ve CubeMX yapılandırmasına göre temel bağlantılar şöyledir:

- TRIG: PB9
- ECHO: PB8 / TIM4 CH3
- Besleme: 5V ve GND

Bağlantı şemasını [devre_sema.jpeg](devre_sema.jpeg) içinde görebilirsiniz.

## Çalışma Mantığı

1. Sistem açılır ve mikrosaniye tabanlı zamanlama hazırlanır.
2. TIM4, giriş yakalama kesmesiyle başlatılır.
3. Ana döngüde HC-SR04'e düzenli olarak TRIG darbesi gönderilir.
4. ECHO sinyalinin başlangıç ve bitiş anları TIM4 üzerinden ölçülür.
5. Ölçülen süre mesafeye dönüştürülür ve debug sırasında izlenebilir.

## Kurulum ve Kullanım

1. Projeyi STM32CubeIDE ile açın.
2. [kod/HedefTespitSistemi.ioc](kod/HedefTespitSistemi.ioc) dosyasını kullanarak proje ayarlarını yükleyin.
3. Gerekirse kod üretimini yeniden çalıştırın.
4. Kartı ve sensörü şemaya göre bağlayın.
5. Projeyi derleyin ve karta yükleyin.

## Notlar

- Ölçümler arasında yaklaşık 60 ms bekleme bırakılır.
- `distance_cm` ve `echo_pulse_us` değişkenleri CubeIDE Debug > Live Expressions bölümünden izlenebilir.

## Gereksinimler

- STM32CubeIDE
- STM32CubeMX uyumlu yapılandırma
- STM32F407 tabanlı kart
- HC-SR04 ultrasonik sensör