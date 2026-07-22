# Hedef Tespit Sistemi

YOLO ve SORT kullanan, gercek zamanli hedef tespit ve takip uygulamasi.

Bu projenin tum calisan dosyalari `goruntu_isleme` klasoru icinde tutulur.

## Ozellikler

- Kamera uzerinden canli goruntu alir.
- `yolo11n.pt` modeli ile hedefleri tespit eder.
- SORT ile nesneleri kareler arasinda takip eder.
- Ekranda sinif adi, takip ID'si ve guven skoru gosterir.

## Gereksinimler

- Python 3.10 veya uzeri
- Kamera veya goruntu alabilen bir cihaz
- Kurulu Python paketleri icin `requirements.txt`

## Kurulum

Once klasore girin:

```bash
cd goruntu_isleme
```

Ardindan bagimliliklari kurun:

```bash
pip install -r requirements.txt
```

## Calistirma

Varsayilan kamera ile calistirmak icin:

```bash
python main.py
```

Farkli kamera veya ayarlarla calistirmak icin:

```bash
python main.py --camera 0 --conf 0.4 --imgsz 480
```

## Komut Satiri Parametreleri

- `--camera`: Kamera numarasi
- `--model`: YOLO model dosyasi
- `--conf`: Minimum tespit guveni
- `--imgsz`: YOLO isleme boyutu
- `--width`: Kamera goruntu genisligi
- `--height`: Kamera goruntu yuksekligi
- `--max-age`: Takibin kac kare boyunca korunacagi
- `--min-hits`: Takibin onaylanmasi icin gereken tespit sayisi
- `--track-iou`: SORT eslestirme IoU esigi

## Dosya Yapisi

- `main.py`: Uygulamanin ana akisi
- `sort.py`: SORT takip implementasyonu
- `requirements.txt`: Python bagimliliklari
- `.gitignore`: Git tarafinda yoksayilacak dosyalar
- `README.md`: Proje kullanimi ve kurulum bilgileri
- `yolo11n.pt`: Hazir YOLO model agirliklari