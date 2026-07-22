# Hedef Tespit Sistemi

Bu depo iki ayrı çalışma alanı içerir:

- [goruntu_isleme/](goruntu_isleme/) içinde YOLO ve SORT tabanlı gerçek zamanlı hedef tespit ve takip uygulaması bulunur.
- [proje/](proje/) içinde STM32F407 tabanlı HC-SR04 mesafe ölçüm projesi bulunur.

Kök dizinde ayrıca donanım şeması için [devre_sema.jpeg](devre_sema.jpeg) yer alır.

## Klasörler

| Yol | Açıklama |
| --- | --- |
| [goruntu_isleme/](goruntu_isleme/) | Kamera üzerinden çalışan, YOLO ve SORT kullanan hedef tespit uygulaması. |
| [goruntu_isleme/README.md](goruntu_isleme/README.md) | Görüntü işleme projesinin kendi kurulum ve kullanım rehberi. |
| [goruntu_isleme/main.py](goruntu_isleme/main.py) | Görüntü işleme uygulamasının ana girişi. |
| [goruntu_isleme/requirements.txt](goruntu_isleme/requirements.txt) | Python bağımlılıkları. |
| [goruntu_isleme/yolo11n.pt](goruntu_isleme/yolo11n.pt) | Varsayılan YOLO ağırlıkları. |
| [proje/](proje/) | STM32CubeIDE ile açılan gömülü sistem projesi. |
| [proje/README.md](proje/README.md) | STM32 projesinin kurulum, bağlantı ve kullanım rehberi. |
| [proje/Core/Src/main.c](proje/Core/Src/main.c) | STM32 uygulamasının ana kodu. |
| [proje/HedefTespitSistemi.ioc](proje/HedefTespitSistemi.ioc) | STM32CubeMX proje yapılandırması. |
| [devre_sema.jpeg](devre_sema.jpeg) | STM32 tarafı için bağlantı şeması. |

## Görüntü İşleme Projesi

Bu bölüm, kameradan görüntü alıp seçili sınıfları tespit eden ve SORT ile takip eden uygulamayı içerir.

Çalıştırmak için:

```bash
cd goruntu_isleme
pip install -r requirements.txt
python main.py
```

Ayrıntılı açıklama ve komut satırı seçenekleri için [goruntu_isleme/README.md](goruntu_isleme/README.md) dosyasına bakın.

## STM32 Projesi

Bu bölüm, HC-SR04 sensörü ile TIM4 Input Capture tabanlı mesafe ölçümü yapan STM32CubeIDE projesini içerir.

Detaylı kurulum ve çalışma adımları için [proje/README.md](proje/README.md) dosyasına bakın. Projeyi açmak için [proje/HedefTespitSistemi.ioc](proje/HedefTespitSistemi.ioc) dosyasını STM32CubeIDE içinde kullanın. Donanım bağlantı detayı için [devre_sema.jpeg](devre_sema.jpeg) dosyasına bakabilirsiniz.

## GitHub Düzeni

Bu depo doğrudan iki farklı çalışma alanını birlikte barındırır. Yeni değişiklik eklerken ilgili klasörde çalışmak en temiz yaklaşımdır:

- Görüntü işleme için [goruntu_isleme/](goruntu_isleme/)
- Gömülü sistem için [proje/](proje/)
