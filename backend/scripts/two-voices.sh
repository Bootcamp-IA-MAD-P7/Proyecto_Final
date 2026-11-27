#!/bin/sh
# Synthetic class of two voices for `make e2e` (section 6 of add-diarized-transcription).
# Two espeak-ng voices, one low and one high, take turns in Spanish; the result is padded to
# 75 seconds (UPLOAD_MIN_SECONDS is 60) and written to stdout as Opus in Ogg. No real data.
# Runs in the worker-dev image, which carries espeak-ng and FFmpeg.
set -eu

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

say() { # <index> <voice> <pitch> <text>
    espeak-ng -v "$2" -p "$3" -s 145 -w "$work/turn-$1.wav" "$4"
}

say 1 es+m3 30 "Buenos días. Hoy vamos a repasar las fracciones y cómo se suman cuando tienen distinto denominador."
say 2 es+f4 80 "Vale. Yo las sumo directamente, arriba con arriba y abajo con abajo. ¿Está bien así?"
say 3 es+m3 30 "No del todo. Primero buscamos un denominador común. Por ejemplo, para sumar un medio y un tercio usamos sextos."
say 4 es+f4 80 "Entonces un medio son tres sextos, y un tercio son dos sextos. En total, cinco sextos."
say 5 es+m3 30 "Exacto, muy bien. Ahora prueba tú con tres cuartos más un octavo y explícame cada paso."
say 6 es+f4 80 "Tres cuartos son seis octavos. Seis octavos más un octavo son siete octavos."
say 7 es+m3 30 "Perfecto. La semana que viene haremos restas de fracciones con el mismo método."
say 8 es+f4 80 "De acuerdo, gracias. Practicaré en casa con los ejercicios del libro."

inputs=""
filter=""
for index in 1 2 3 4 5 6 7 8; do
    inputs="$inputs -i $work/turn-$index.wav"
    # Each turn followed by a short pause, so the change of voice is clear.
    filter="$filter[$((index - 1)):a]aresample=16000,apad=pad_dur=0.8[t$index];"
done
filter="${filter}[t1][t2][t3][t4][t5][t6][t7][t8]concat=n=8:v=0:a=1,apad=whole_dur=75[out]"

# shellcheck disable=SC2086
ffmpeg -nostdin -loglevel error $inputs -filter_complex "$filter" -map "[out]" \
    -ac 1 -c:a libopus -b:a 32k -f ogg pipe:1
