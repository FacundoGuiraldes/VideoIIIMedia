# VideoIIIMedia

Video de fin de año de III Media (2º ES – III MEDIA 2026).

## Estructura
- Una carpeta por alumno con sus fotos (las que mandaron las familias).
- `plan.csv`: fotos elegidas y orden del video (de más chicos a más grandes).
- `scripts/build_plan.py`: genera `plan.csv` a partir de las edades estimadas por foto.
- `scripts/render_video.py`: arma el video (mismo estilo que VideoIVLiceo: fotos sobre fondo desenfocado, fundidos, mosaico, frases en italiano y créditos).
  - Borrador: `python3 scripts/render_video.py --audio musica/cancion.mp3 --out borrador.mp4 --scale 0.5`
  - Final: igual con `--scale 1.0 --crf 24` (1920x1080)

## Decisiones
- Cantidad pareja de fotos por alumno: máximo 8 (`N_POR_ALUMNO`); quien tiene menos usa todas las que tiene.
- Orden por edad estimada: bebé/jardín → primaria → fin de primaria → secundaria.
- Música: "Il più grande spettacolo dopo il Big Bang" (4:23). El archivo mp3 no se versiona (carpeta `musica/` ignorada).

## Pendiente
- Ivonne Zarini Antonini: no enviaron fotos, no aparece en el video.
- Confirmar si "Mateo 7.png" (carpeta Ocampos) es de Della Savia, y qué es "Juan Martín S (6).jpg" (carpeta Perrone).
