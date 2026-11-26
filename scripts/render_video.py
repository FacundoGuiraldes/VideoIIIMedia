#!/usr/bin/env python3
"""
Renderiza el video de III Media con el mismo estilo que VideoIVLiceo_final_v3:
  - fotos a pantalla completa (sin recortar) sobre fondo desenfocado de la misma foto
  - fundido cruzado entre fotos, sin texto durante las fotos
  - cierre: mosaico de fotos -> frases en italiano -> créditos con los nombres

Uso:
  python3 scripts/render_video.py --audio musica/cancion.mp3 --out salida.mp4 --scale 0.5   # borrador 960x540
  python3 scripts/render_video.py --audio musica/cancion.mp3 --out salida.mp4 --scale 1.0   # final 1920x1080
"""
import argparse
import csv
import glob
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 25
XFADE = 0.36  # segundos de fundido cruzado (igual al video de referencia)

# ---- portada (como el video de IV Liceo: fondo azul oscuro + título) ----
T_INTRO = 5.0  # los últimos T_INTRO_XFADE segundos se funde con la primera foto
T_INTRO_XFADE = 1.0
INTRO_TITULO = "III MEDIA"
INTRO_ANIO = "2026"
INTRO_PIE = "Scuole CCI · Scuola Alessandro Manzoni"

# ---- tiempos del cierre (segundos) ----
T_MOSAICO = 4.0
T_TEXTOS = [5.0, 3.5]
T_CREDITOS = 18.0
T_ESCUDO = 5.0  # cierre final con el escudo de la escuela

# ---- textos del cierre (en italiano). Tono sereno: es el cierre de III Media, no de la escuela ----
TEXTOS = [
    ("Grazie per questi anni!", ["Un ciclo si chiude, un altro sta per cominciare."]),
    ("Ci vediamo al Liceo!", []),
]
TITULO_CREDITOS = "III MEDIA 2026"
PIE_CREDITOS = INTRO_PIE

# Listado oficial (2º ES – III MEDIA 2026), como "Nombre Apellido"
ALUMNOS_CREDITOS = [
    "Julián Bogan", "Martina Belén Cálcena", "Bhianca Aylén Chacana", "Valentina Lucía Delgado",
    "Mateo Della Savia", "Paloma Sofía Fontan Rama", "Juan Martín García Diana",
    "Allegra Simona Gonzalez Pitronaci", "Luca Libertini", "Nicolás Augusto Mognoni",
    "Matías Ocampos", "Franco Perrone", "Bautista Nicolas Robledo Coria", "Anna Sabatte",
    "Felipe Schauffele", "Santino León Silva", "Liezel Brielle Velletri Cubilla",
    "Ivonne Zarini Antonini",
]


def font(kind, size):
    pats = {
        "serif": ["/usr/share/fonts/truetype/**/*Serif.ttf", "/usr/share/fonts/**/DejaVuSerif.ttf"],
        "sans": ["/usr/share/fonts/**/DejaVuSans.ttf"],
        "sansbold": ["/usr/share/fonts/**/DejaVuSans-Bold.ttf"],
    }[kind]
    for p in pats:
        for f in glob.glob(p, recursive=True):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def cargar(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((2400, 2400))
    return im


def componer(im, W, H):
    """Foto completa centrada sobre fondo desenfocado de la misma foto."""
    chico = ImageOps.fit(im, (max(W // 8, 8), max(H // 8, 8)))
    chico = chico.filter(ImageFilter.GaussianBlur(5))
    bg = np.asarray(chico.resize((W, H), Image.BICUBIC), dtype=np.float32) * 0.72
    fg = ImageOps.contain(im, (W, H), Image.LANCZOS)
    out = bg.astype(np.uint8)
    x, y = (W - fg.width) // 2, (H - fg.height) // 2
    out[y:y + fg.height, x:x + fg.width] = np.asarray(fg)
    return out


def mezcla(a, b, alpha):
    w = int(round(alpha * 256))
    return ((a.astype(np.uint16) * (256 - w) + b.astype(np.uint16) * w) >> 8).astype(np.uint8)


def lienzo(W, H):
    return Image.new("RGB", (W, H), (0, 0, 0)), Image.new("L", (W, H), 0)


def texto_centrado(rgb, mask, y, txt, f, color, track=0):
    """Texto centrado; `track` = separación extra entre letras en píxeles."""
    d1, d2 = ImageDraw.Draw(rgb), ImageDraw.Draw(mask)
    if not track:
        w = d1.textlength(txt, font=f)
        x = (rgb.width - w) / 2
        d1.text((x, y), txt, font=f, fill=color)
        d2.text((x, y), txt, font=f, fill=255)
        return
    w = sum(d1.textlength(c, font=f) + track for c in txt) - track
    x = (rgb.width - w) / 2
    for c in txt:
        d1.text((x, y), c, font=f, fill=color)
        d2.text((x, y), c, font=f, fill=255)
        x += d1.textlength(c, font=f) + track


def fondo_portada(W, H):
    """Degradé azul oscuro (arriba) a casi negro (abajo), como la portada de IV Liceo."""
    arriba, abajo = np.array([12, 28, 54], np.float32), np.array([2, 6, 14], np.float32)
    k = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    fila = arriba * (1 - k) + abajo * k
    return np.repeat(fila, W, axis=1).astype(np.uint8)


def slide_portada(W, H):
    s = H / 1080
    rgb, mask = lienzo(W, H)
    y = int(H * 0.27)
    texto_centrado(rgb, mask, y, INTRO_TITULO, font("serif", int(132 * s)), (248, 248, 248), track=int(18 * s))
    linea_tricolor(rgb, mask, y + int(190 * s), int(180 * s))
    texto_centrado(rgb, mask, y + int(225 * s), INTRO_ANIO, font("sans", int(46 * s)), (215, 215, 215), track=int(14 * s))
    texto_centrado(rgb, mask, y + int(335 * s), INTRO_PIE, font("sans", int(32 * s)), (165, 175, 190), track=int(3 * s))
    return np.asarray(rgb), np.asarray(mask, dtype=np.float32)[..., None] / 255.0


def linea_tricolor(rgb, mask, y, ancho):
    d1, d2 = ImageDraw.Draw(rgb), ImageDraw.Draw(mask)
    x0 = (rgb.width - ancho) // 2
    t = max(3, ancho // 40)
    for i, c in enumerate([(0, 146, 70), (240, 240, 240), (206, 43, 55)]):
        d1.rectangle([x0 + i * ancho // 3, y, x0 + (i + 1) * ancho // 3, y + t], fill=c)
        d2.rectangle([x0 + i * ancho // 3, y, x0 + (i + 1) * ancho // 3, y + t], fill=255)


def slide_texto(W, H, titulo, lineas):
    s = H / 1080
    rgb, mask = lienzo(W, H)
    ft, fs = font("serif", int(92 * s)), font("sans", int(46 * s))
    y = int(H * 0.38)
    texto_centrado(rgb, mask, y, titulo, ft, (245, 245, 245))
    linea_tricolor(rgb, mask, y + int(140 * s), int(200 * s))
    for i, l in enumerate(lineas):
        texto_centrado(rgb, mask, y + int(190 * s) + i * int(66 * s), l, fs, (210, 210, 210))
    return np.asarray(rgb), np.asarray(mask, dtype=np.float32)[..., None] / 255.0


def lienzo_creditos(W, H):
    s = H / 1080
    paso = int(86 * s)
    alto = int(320 * s) + paso * len(ALUMNOS_CREDITOS) + int(300 * s)
    rgb, mask = lienzo(W, alto)
    y = int(40 * s)
    texto_centrado(rgb, mask, y, TITULO_CREDITOS, font("sansbold", int(46 * s)), (240, 240, 240), track=int(9 * s))
    linea_tricolor(rgb, mask, y + int(90 * s), int(170 * s))
    fn = font("sans", int(54 * s))
    y0 = y + int(190 * s)
    for i, n in enumerate(ALUMNOS_CREDITOS):
        texto_centrado(rgb, mask, y0 + i * paso, n, fn, (232, 232, 232))
    y_pie = y0 + len(ALUMNOS_CREDITOS) * paso + int(130 * s)
    texto_centrado(rgb, mask, y_pie, PIE_CREDITOS, font("serif", int(44 * s)), (205, 205, 205))
    return np.asarray(rgb), np.asarray(mask, dtype=np.float32)[..., None] / 255.0, y_pie + int(30 * s)


def componer_texto(bg, rgb, mask, e):
    """bg + capa de texto con opacidad e (0..1)."""
    out = bg.astype(np.float32) + (rgb.astype(np.float32) - bg.astype(np.float32)) * mask * e
    return out.clip(0, 255).astype(np.uint8)


def escudo_rgba(H):
    """Escudo con el fondo blanco exterior transparente (lo interior del escudo queda blanco)."""
    import cv2
    im = np.asarray(Image.open(os.path.join(ROOT, "assets", "escudo.jpg")).convert("RGB"))
    blanco = (im.min(axis=2) >= 235).astype(np.uint8)
    _, lab = cv2.connectedComponents(blanco, connectivity=4)
    exterior = (lab == lab[0, 0]).astype(np.uint8)
    interior = 1 - exterior
    interior = cv2.erode(interior, np.ones((5, 5), np.uint8))  # saca el halo claro del borde
    alfa = cv2.GaussianBlur(interior.astype(np.float32), (0, 0), 1.2)
    ys, xs = np.where(interior > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb, alfa = im[y0:y1, x0:x1], alfa[y0:y1, x0:x1]
    alto = int(H * 0.62)
    ancho = int(rgb.shape[1] * alto / rgb.shape[0])
    rgb = cv2.resize(rgb, (ancho, alto), interpolation=cv2.INTER_AREA)
    alfa = cv2.resize(alfa, (ancho, alto), interpolation=cv2.INTER_AREA)
    return rgb, alfa[..., None]


def mosaico(fotos, W, H, cols=6, filas=4):
    cw, ch = W // cols, H // filas
    celdas = []
    paso = len(fotos) / (cols * filas)
    for k in range(cols * filas):
        im = fotos[int(k * paso)]
        celdas.append(np.asarray(ImageOps.fit(im, (cw, ch), Image.LANCZOS)))
    return celdas, cw, ch, cols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--max-fotos", type=int, default=0, help="solo para pruebas rápidas")
    ap.add_argument("--crf", type=int, default=26)
    a = ap.parse_args()

    W, H = int(1920 * a.scale) // 2 * 2, int(1080 * a.scale) // 2 * 2
    dur_audio = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio]))
    with open(os.path.join(ROOT, "plan.csv"), encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if a.max_fotos:
        filas = filas[:a.max_fotos]
    n = len(filas)
    t_cierre = T_MOSAICO + sum(T_TEXTOS) + T_CREDITOS + T_ESCUDO
    D = (dur_audio - T_INTRO - t_cierre) / n if not a.max_fotos else 1.7
    total = T_INTRO + n * D + t_cierre
    print(f"{n} fotos, {D:.3f} s por foto, portada {T_INTRO:.1f} s, cierre {t_cierre:.1f} s, total {total:.1f} s, {W}x{H}")

    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", a.audio,
         "-af", f"afade=t=out:st={total - 2.5:.2f}:d=2.5",
         "-map", "0:v", "-map", "1:a", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", a.out], stdin=subprocess.PIPE)
    emit = enc.stdin.write

    # ---------------- fotos ----------------
    ims = []
    negro = np.zeros((H, W, 3), np.uint8)
    cache = {}

    def frame_foto(i):
        if i >= n:
            return negro
        if i not in cache:
            for k in [k for k in cache if k < i - 1]:
                del cache[k]
            im = cargar(os.path.join(ROOT, filas[i]["archivo"]))
            mini = im.copy()
            mini.thumbnail((520, 520))  # solo para el mosaico final
            ims.append(mini)
            cache[i] = componer(im, W, H)
        return cache[i]

    # ---------------- portada ----------------
    gris = fondo_portada(W, H)
    prgb, pmask = slide_portada(W, H)
    for f in range(int(T_INTRO * FPS)):
        t = f / FPS
        fr = componer_texto(gris, prgb, pmask, min(t / 1.0, 1))
        if t >= T_INTRO - T_INTRO_XFADE:
            fr = mezcla(fr, frame_foto(0), (t - (T_INTRO - T_INTRO_XFADE)) / T_INTRO_XFADE)
        emit(fr.tobytes())

    n_frames_fotos = int(round(n * D * FPS))
    actual, actual_bytes = -1, None
    for f in range(n_frames_fotos):
        t = f / FPS
        i = min(int(t / D), n - 1)
        u = t - i * D
        if u >= D - XFADE:
            fr = mezcla(frame_foto(i), frame_foto(i + 1), (u - (D - XFADE)) / XFADE)
            emit(fr.tobytes())
        else:
            if i != actual:
                actual, actual_bytes = i, frame_foto(i).tobytes()
            emit(actual_bytes)

    # ---------------- mosaico ----------------
    celdas, cw, ch, cols = mosaico(ims, W, H)
    for f in range(int(T_MOSAICO * FPS)):
        t = f / FPS
        fr = np.zeros((H, W, 3), np.uint8)
        for k, c in enumerate(celdas):
            al = min(max((t - k * 0.09) / 0.4, 0), 1)
            if al > 0:
                y, x = (k // cols) * ch, (k % cols) * cw
                fr[y:y + ch, x:x + cw] = (c * al).astype(np.uint8)
        emit(fr.tobytes())
    base = negro.copy()
    for k, c in enumerate(celdas):
        y, x = (k // cols) * ch, (k % cols) * cw
        base[y:y + ch, x:x + cw] = c
    # el mosaico se oscurece para que se lea el texto
    fondo = (base.astype(np.float32) * 0.28).astype(np.uint8)

    # ---------------- frases ----------------
    for (titulo, lineas), dur in zip(TEXTOS, T_TEXTOS):
        rgb, mask = slide_texto(W, H, titulo, lineas)
        for f in range(int(dur * FPS)):
            t = f / FPS
            e = min(t / 0.7, 1, (dur - t) / 0.7)
            emit(componer_texto(fondo, rgb, mask, max(e, 0)).tobytes())

    # ---------------- créditos ----------------
    rgb, mask, y_pie = lienzo_creditos(W, H)
    alto = rgb.shape[0]
    y_ini = H  # el lienzo entra por abajo
    y_fin = H // 2 - y_pie  # termina con el pie centrado
    t_scroll = T_CREDITOS - 3.5
    nfc = int(T_CREDITOS * FPS)
    for f in range(nfc):
        t = f / FPS
        p = min(t / t_scroll, 1)
        top = int(y_ini + (y_fin - y_ini) * p)
        r = np.zeros((H, W, 3), np.uint8)
        m = np.zeros((H, W, 1), np.float32)
        a0, b0 = max(top, 0), min(top + alto, H)
        if b0 > a0:
            r[a0:b0] = rgb[a0 - top:b0 - top]
            m[a0:b0] = mask[a0 - top:b0 - top]
        e_in = min(t / 0.7, 1)
        out = componer_texto(fondo, r, m, e_in)
        fade = min((T_CREDITOS - t) / 1.5, 1)
        emit((out.astype(np.float32) * max(fade, 0)).astype(np.uint8).tobytes())

    # ---------------- escudo final ----------------
    erg, ea = escudo_rgba(H)
    fondo_e = fondo_portada(W, H).astype(np.float32)
    y0, x0 = (H - erg.shape[0]) // 2, (W - erg.shape[1]) // 2
    fondo_e[y0:y0 + erg.shape[0], x0:x0 + erg.shape[1]] = (
        fondo_e[y0:y0 + erg.shape[0], x0:x0 + erg.shape[1]] * (1 - ea) + erg * ea)
    fondo_e = fondo_e.clip(0, 255).astype(np.uint8)
    for f in range(int(T_ESCUDO * FPS)):
        t = f / FPS
        k = max(min(t / 1.2, 1, (T_ESCUDO - t) / 1.0), 0)
        emit((fondo_e.astype(np.float32) * k).astype(np.uint8).tobytes())

    enc.stdin.close()
    enc.wait()
    print("listo:", a.out)


if __name__ == "__main__":
    main()
