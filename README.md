# Hedef Tespit Sistemi

Bu depo, STM32F407 tabanlı bir kart üzerinde HC-SR04 ultrasonik sensör ile mesafe ölçümü yapan bir STM32CubeIDE projesidir. Ölçüm, TIM4 Input Capture ile ECHO darbe süresini okuyarak yapılır ve sonuç santimetre cinsinden hesaplanır.

## Proje Özeti

- HC-SR04 sensörüne 10 µs TRIG darbesi gönderir.
- ECHO sinyalinin yükselen ve düşen kenarlarını TIM4 ile yakalar.
- Darbe süresini mikrosaniye cinsinden ölçer.
- Mesafeyi yaklaşık olarak echo süresi / 58 formülüyle cm cinsine çevirir.

## Klasör Yapısı

Bu projede GitHub'a yüklemeden önce bilmeniz gereken ana dosya ve klasörler şunlardır:

| Yol | Açıklama |
| --- | --- |
| [Core/Src/main.c](Core/Src/main.c) | Uygulamanın ana kodu. TRIG üretimi, TIM4 kesme akışı, darbe süresi ölçümü ve mesafe hesabı burada bulunur. |
| [Core/Inc/main.h](Core/Inc/main.h) | Ana uygulamanın ortak başlık dosyası. Pin ve fonksiyon bildirimleri burada yer alır. |
| [HedefTespitSistemi.ioc](HedefTespitSistemi.ioc) | STM32CubeMX/STM32CubeIDE proje yapılandırması. Saat ayarları, pin atamaları ve çevre birimi konfigürasyonları burada tutulur. |
| [Core/Src/stm32f4xx_it.c](Core/Src/stm32f4xx_it.c) | Kesme yönlendirmeleri ve interrupt handler yapısı. |
| [Core/Src/stm32f4xx_hal_msp.c](Core/Src/stm32f4xx_hal_msp.c) | HAL seviyesinde çevre birimi başlangıç ayarları. |
| [Core/Startup/startup_stm32f407vgtx.s](Core/Startup/startup_stm32f407vgtx.s) | Başlangıç assembly kodu ve vektör tablosu. |
| [Drivers/STM32F4xx_HAL_Driver/](Drivers/STM32F4xx_HAL_Driver/) | STM32 HAL sürücüleri. Donanım soyutlama katmanı burada bulunur. |
| [Drivers/CMSIS/](Drivers/CMSIS/) | CMSIS çekirdek ve cihaz başlıkları. |
| [Middlewares/ST/STM32_USB_Host_Library/](Middlewares/ST/STM32_USB_Host_Library/) | CubeMX tarafından eklenmiş USB Host kütüphanesi. Bu projede yapılandırma içinde yer alıyor. |
| [USB_HOST/App/usb_host.c](USB_HOST/App/usb_host.c) | USB Host uygulama katmanı. |
| [USB_HOST/Target/usbh_conf.c](USB_HOST/Target/usbh_conf.c) | USB Host yapılandırması. |
| [USB_HOST/Target/usbh_platform.c](USB_HOST/Target/usbh_platform.c) | USB Host platform katmanı. |
| [STM32F407VGTX_FLASH.ld](STM32F407VGTX_FLASH.ld) | Flash bellek yerleşim dosyası. |
| [STM32F407VGTX_RAM.ld](STM32F407VGTX_RAM.ld) | RAM bellek yerleşim dosyası. |
| [devre_sema.jpeg](devre_sema.jpeg) | Donanım bağlantı şeması. Kart, HC-SR04 ve bağlantı noktalarının görsel özeti. |

## Donanım Bağlantıları

Mevcut kod ve CubeMX yapılandırmasına göre temel bağlantılar şöyledir:

- TRIG: PB9
- ECHO: PB8 / TIM4 CH3
- Besleme: 5V ve GND

Bağlantı şemasını [devre_sema.jpeg](devre_sema.jpeg) içinde görebilirsiniz.

## Çalışma Mantığı

1. Sistem açılır ve DWT tabanlı mikrosaniye gecikme sayacı hazırlanır.
2. TIM4, giriş yakalama kesmesiyle başlatılır.
3. Ana döngüde HC-SR04'e düzenli olarak TRIG darbesi gönderilir.
4. ECHO sinyalinin başlangıç ve bitiş anları TIM4 üzerinden ölçülür.
5. Ölçülen süre mesafeye dönüştürülür ve debug sırasında izlenebilir.

## Kurulum ve Kullanım

1. Projeyi STM32CubeIDE ile açın.
2. [HedefTespitSistemi.ioc](HedefTespitSistemi.ioc) dosyasını kullanarak proje ayarlarını yükleyin.
3. Gerekirse kod üretimini yeniden çalıştırın.
4. Kartı ve sensörü şemaya göre bağlayın.
5. Projeyi derleyin ve karta yükleyin.
6. Ölçüm sonuçlarını `distance_cm` ve `echo_pulse_us` değişkenlerinden takip edin.

## Notlar

- Ölçümler arasında yaklaşık 60 ms bekleme bırakılır.
- `distance_cm` ve `echo_pulse_us` değişkenleri CubeIDE Debug > Live Expressions bölümünden izlenebilir.
- GitHub'a yüklerken `Debug/` klasörü derleme çıktısı içerir; repoda tutmak istemiyorsanız hariç bırakabilirsiniz.

## Gereksinimler

- STM32CubeIDE
- STM32CubeMX uyumlu yapılandırma
- STM32F407 tabanlı kart
- HC-SR04 ultrasonik sensör
