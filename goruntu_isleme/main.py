from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

try:
    from sort import Sort
except ImportError as exc:
    raise SystemExit(
        "sort.py bulunamadı veya SORT bağımlılıkları kurulu değil.\n"
        "sort.py dosyasının main.py ile aynı klasörde olduğundan emin olun."
    ) from exc


# COCO sınıf numaraları:
# 0: person, 1: bicycle, 2: car,
# 3: motorcycle, 5: bus, 7: truck
HEDEF_SINIFLAR = [0, 1, 2, 3, 5, 7]

SINIF_ADLARI = {
    0: "insan",
    1: "bisiklet",
    2: "otomobil",
    3: "motosiklet",
    5: "otobus",
    7: "kamyon",
}


def argumanlari_al() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="YOLO ve SORT tabanli gercek zamanli hedef tespit sistemi"
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Kamera numarasi. Varsayilan: 0",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolo11n.pt",
        help="YOLO model dosyasi. Varsayilan: yolo11n.pt",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.40,
        help="Minimum tespit guveni. Varsayilan: 0.40",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=480,
        help="YOLO isleme boyutu. Varsayilan: 480",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Kamera goruntu genisligi. Varsayilan: 640",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Kamera goruntu yuksekligi. Varsayilan: 480",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="Kayip takibin korunacagi kare sayisi. Varsayilan: 30",
    )
    parser.add_argument(
        "--min-hits",
        type=int,
        default=3,
        help="Takibin onaylanmasi icin gereken tespit sayisi. Varsayilan: 3",
    )
    parser.add_argument(
        "--track-iou",
        type=float,
        default=0.30,
        help="SORT eslestirme IoU esigi. Varsayilan: 0.30",
    )

    args = parser.parse_args()

    if not 0.0 < args.conf <= 1.0:
        parser.error("--conf degeri 0 ile 1 arasinda olmalidir.")

    if not 0.0 < args.track_iou <= 1.0:
        parser.error("--track-iou degeri 0 ile 1 arasinda olmalidir.")

    if args.imgsz <= 0 or args.width <= 0 or args.height <= 0:
        parser.error("Goruntu boyutlari sifirdan buyuk olmalidir.")

    return args


def iou_hesapla(kutu1: np.ndarray, kutu2: np.ndarray) -> float:
    """İki [x1, y1, x2, y2] kutusunun IoU değerini hesaplar."""

    kesisim_x1 = max(float(kutu1[0]), float(kutu2[0]))
    kesisim_y1 = max(float(kutu1[1]), float(kutu2[1]))
    kesisim_x2 = min(float(kutu1[2]), float(kutu2[2]))
    kesisim_y2 = min(float(kutu1[3]), float(kutu2[3]))

    kesisim_genisligi = max(0.0, kesisim_x2 - kesisim_x1)
    kesisim_yuksekligi = max(0.0, kesisim_y2 - kesisim_y1)
    kesisim_alani = kesisim_genisligi * kesisim_yuksekligi

    kutu1_alani = max(
        0.0,
        float(kutu1[2]) - float(kutu1[0]),
    ) * max(
        0.0,
        float(kutu1[3]) - float(kutu1[1]),
    )

    kutu2_alani = max(
        0.0,
        float(kutu2[2]) - float(kutu2[0]),
    ) * max(
        0.0,
        float(kutu2[3]) - float(kutu2[1]),
    )

    birlesim_alani = kutu1_alani + kutu2_alani - kesisim_alani

    if birlesim_alani <= 0.0:
        return 0.0

    return kesisim_alani / birlesim_alani


def tespitleri_takiplerle_eslestir(
    takipler: np.ndarray,
    yolo_tespitleri: list[dict[str, Any]],
    minimum_iou: float = 0.10,
) -> dict[int, int]:
    """
    SORT takiplerini YOLO tespitleriyle benzersiz olarak eşleştirir.

    Dönen sözlük:
        takip_indeksi -> YOLO tespit_indeksi
    """

    adaylar: list[tuple[float, int, int]] = []

    for takip_indeksi, takip in enumerate(takipler):
        takip_kutusu = takip[:4]

        for tespit_indeksi, tespit in enumerate(yolo_tespitleri):
            iou = iou_hesapla(
                takip_kutusu,
                tespit["kutu"],
            )

            if iou >= minimum_iou:
                adaylar.append(
                    (iou, takip_indeksi, tespit_indeksi)
                )

    # En yüksek IoU değerlerinden başlayarak eşleştir.
    adaylar.sort(key=lambda deger: deger[0], reverse=True)

    kullanilan_takipler: set[int] = set()
    kullanilan_tespitler: set[int] = set()
    eslesmeler: dict[int, int] = {}

    for _, takip_indeksi, tespit_indeksi in adaylar:
        if takip_indeksi in kullanilan_takipler:
            continue

        if tespit_indeksi in kullanilan_tespitler:
            continue

        eslesmeler[takip_indeksi] = tespit_indeksi
        kullanilan_takipler.add(takip_indeksi)
        kullanilan_tespitler.add(tespit_indeksi)

    return eslesmeler


def etiket_ciz(
    goruntu: np.ndarray,
    kutu: tuple[int, int, int, int],
    etiket: str,
) -> None:
    """Takip kutusunu ve okunabilir etiket alanını çizer."""

    x1, y1, x2, y2 = kutu
    renk = (0, 255, 0)

    cv2.rectangle(
        goruntu,
        (x1, y1),
        (x2, y2),
        renk,
        2,
    )

    yazi_boyutu, taban = cv2.getTextSize(
        etiket,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        2,
    )

    yazi_genisligi, yazi_yuksekligi = yazi_boyutu

    etiket_alt_y = max(y1, yazi_yuksekligi + 12)
    etiket_ust_y = etiket_alt_y - yazi_yuksekligi - 10
    etiket_sag_x = min(
        x1 + yazi_genisligi + 10,
        goruntu.shape[1] - 1,
    )

    cv2.rectangle(
        goruntu,
        (x1, etiket_ust_y),
        (etiket_sag_x, etiket_alt_y + taban),
        renk,
        -1,
    )

    cv2.putText(
        goruntu,
        etiket,
        (x1 + 5, etiket_alt_y - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )


def durum_paneli_ciz(
    goruntu: np.ndarray,
    fps: float,
    aktif_hedef: int,
) -> None:
    """FPS ve aktif hedef sayısını ekranın üstünde gösterir."""

    cv2.rectangle(
        goruntu,
        (0, 0),
        (goruntu.shape[1], 38),
        (0, 0, 0),
        -1,
    )

    durum_metni = (
        f"FPS: {fps:.1f}  |  "
        f"Aktif hedef: {aktif_hedef}  |  "
        "Cikis: Q veya ESC"
    )

    cv2.putText(
        goruntu,
        durum_metni,
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def main() -> int:
    args = argumanlari_al()

    print("Model yukleniyor...")

    try:
        model = YOLO(args.model)
    except Exception as exc:
        print(
            f"YOLO modeli yuklenemedi: {exc}",
            file=sys.stderr,
        )
        return 1

    takipci = Sort(
        max_age=args.max_age,
        min_hits=args.min_hits,
        iou_threshold=args.track_iou,
    )

    kamera = cv2.VideoCapture(args.camera)

    if not kamera.isOpened():
        print(
            f"Kamera acilamadi. Kamera numarasi: {args.camera}",
            file=sys.stderr,
        )
        return 1

    kamera.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    kamera.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # Desteklenmeyen kameralarda etkisiz kalabilir.
    kamera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    takip_bilgileri: dict[int, dict[str, Any]] = {}

    kare_numarasi = 0
    yumusatilmıs_fps = 0.0

    print("Sistem hazir.")
    print("Cikmak icin Q veya ESC tusuna basin.")

    try:
        while True:
            kare_baslangici = time.perf_counter()

            basarili, goruntu = kamera.read()

            if not basarili:
                print(
                    "Kameradan goruntu alinamadi.",
                    file=sys.stderr,
                )
                break

            kare_numarasi += 1

            sonuclar = model.predict(
                source=goruntu,
                classes=HEDEF_SINIFLAR,
                conf=args.conf,
                imgsz=args.imgsz,
                device="cpu",
                verbose=False,
            )

            kutular = sonuclar[0].boxes

            sort_tespitleri: list[list[float]] = []
            yolo_tespitleri: list[dict[str, Any]] = []

            if kutular is not None and len(kutular) > 0:
                koordinatlar = kutular.xyxy.cpu().numpy()
                guvenler = kutular.conf.cpu().numpy()
                siniflar = kutular.cls.cpu().numpy().astype(int)

                for koordinat, guven, sinif_id in zip(
                    koordinatlar,
                    guvenler,
                    siniflar,
                ):
                    x1, y1, x2, y2 = koordinat

                    sort_tespitleri.append(
                        [
                            float(x1),
                            float(y1),
                            float(x2),
                            float(y2),
                            float(guven),
                        ]
                    )

                    yolo_tespitleri.append(
                        {
                            "kutu": np.array(
                                [x1, y1, x2, y2],
                                dtype=np.float32,
                            ),
                            "guven": float(guven),
                            "sinif_id": int(sinif_id),
                        }
                    )

            if sort_tespitleri:
                tespit_dizisi = np.asarray(
                    sort_tespitleri,
                    dtype=np.float32,
                )
            else:
                tespit_dizisi = np.empty(
                    (0, 5),
                    dtype=np.float32,
                )

            takip_sonuclari = takipci.update(
                tespit_dizisi
            )

            eslesmeler = tespitleri_takiplerle_eslestir(
                takip_sonuclari,
                yolo_tespitleri,
            )

            for takip_indeksi, takip in enumerate(
                takip_sonuclari
            ):
                x1, y1, x2, y2, takip_id_degeri = takip
                takip_id = int(takip_id_degeri)

                tespit_indeksi = eslesmeler.get(
                    takip_indeksi
                )

                if tespit_indeksi is not None:
                    tespit = yolo_tespitleri[
                        tespit_indeksi
                    ]

                    sinif_id = tespit["sinif_id"]

                    takip_bilgileri[takip_id] = {
                        "sinif": SINIF_ADLARI.get(
                            sinif_id,
                            model.names.get(
                                sinif_id,
                                "hedef",
                            ),
                        ),
                        "guven": tespit["guven"],
                        "son_gorulme": kare_numarasi,
                    }

                bilgi = takip_bilgileri.get(
                    takip_id,
                    {
                        "sinif": "hedef",
                        "guven": 0.0,
                        "son_gorulme": kare_numarasi,
                    },
                )

                goruntu_yuksekligi, goruntu_genisligi = (
                    goruntu.shape[:2]
                )

                x1 = int(
                    np.clip(
                        x1,
                        0,
                        goruntu_genisligi - 1,
                    )
                )
                y1 = int(
                    np.clip(
                        y1,
                        0,
                        goruntu_yuksekligi - 1,
                    )
                )
                x2 = int(
                    np.clip(
                        x2,
                        0,
                        goruntu_genisligi - 1,
                    )
                )
                y2 = int(
                    np.clip(
                        y2,
                        0,
                        goruntu_yuksekligi - 1,
                    )
                )

                etiket = (
                    f"{bilgi['sinif']} | "
                    f"ID: {takip_id} | "
                    f"%{bilgi['guven'] * 100:.0f}"
                )

                etiket_ciz(
                    goruntu,
                    (x1, y1, x2, y2),
                    etiket,
                )

            # Artık kullanılmayan eski ID bilgilerini temizle.
            eski_id_siniri = args.max_age * 5

            silinecek_idler = [
                takip_id
                for takip_id, bilgi
                in takip_bilgileri.items()
                if (
                    kare_numarasi
                    - bilgi["son_gorulme"]
                    > eski_id_siniri
                )
            ]

            for takip_id in silinecek_idler:
                takip_bilgileri.pop(takip_id, None)

            kare_suresi = (
                time.perf_counter() - kare_baslangici
            )
            anlik_fps = 1.0 / max(kare_suresi, 0.000001)

            if yumusatilmıs_fps == 0.0:
                yumusatilmıs_fps = anlik_fps
            else:
                yumusatilmıs_fps = (
                    0.90 * yumusatilmıs_fps
                    + 0.10 * anlik_fps
                )

            durum_paneli_ciz(
                goruntu,
                yumusatilmıs_fps,
                len(takip_sonuclari),
            )

            cv2.imshow(
                "YOLO ve SORT Hedef Tespit Sistemi",
                goruntu,
            )

            tus = cv2.waitKey(1) & 0xFF

            if tus == ord("q") or tus == 27:
                break

    except KeyboardInterrupt:
        print("\nProgram kullanici tarafindan durduruldu.")

    except Exception as exc:
        print(
            f"Calisma sirasinda hata olustu: {exc}",
            file=sys.stderr,
        )
        return 1

    finally:
        kamera.release()
        cv2.destroyAllWindows()

    print("Program kapatildi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())