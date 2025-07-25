import os
import subprocess
import mutagen
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error

# Dossiers
local_dir = "F:/StVince.RAW"
wav_dir = os.path.join(local_dir,"wav")
flac_dir = os.path.join(local_dir,"flac")

github_dir = "F:Local/music/docs/assets"
mp3_dir = os.path.join(github_dir, "audio/mp3")
cover_dir = os.path.join(github_dir, "covers")

# Métadonnées globales
artist = "St Vince"
website = "https://vincentlagny.github.io/music/"

# Créer les dossiers si absents
os.makedirs(flac_dir, exist_ok=True)
os.makedirs(mp3_dir, exist_ok=True)

for filename in os.listdir(wav_dir):
    if not filename.endswith(".wav"):
        continue

    base = os.path.splitext(filename)[0]
    wav_path = os.path.join( wav_dir, filename)
    flac_path = os.path.join( flac_dir, f"{base}.flac")
    mp3_path = os.path.join( mp3_dir, f"{base}.mp3")
    cover_path = os.path.join( cover_dir, f"{base}.png")

    # ✅ Sauter si FLAC déjà encodé
    if os.path.exists(flac_path):
        print(f"⏭️  FLAC déjà présent, saut : {flac_path}")
        continue

    # ✅ Extraire partie après "CDxx." pour titre/album
    if "." in base:
        title_part = base.split(".", 1)[1]
    else:
        title_part = base  # fallback

    # 🎼 Encodage FLAC
    print(f"🎼 FLAC : {filename} → {flac_path}")
    subprocess.run(["flac", "--best", "-f", wav_path, "-o", flac_path], check=True)

    # 🖋️ Métadonnées FLAC
    print(f"🖋️ Métadonnées FLAC : {flac_path}")
    flac = FLAC(flac_path)
    flac["title"] = title_part
    flac["artist"] = artist
    flac["album"] = title_part
    flac["tracknumber"] = "1"
    flac["comment"] = website

    if os.path.exists(cover_path):
        with open(cover_path, "rb") as img:
            pic = Picture()
            pic.data = img.read()
            pic.type = 3
            pic.mime = "image/png"
            pic.desc = "Cover"
            flac.add_picture(pic)
    else:
        print(f"⚠️ Pochette FLAC manquante : {cover_path}")

    flac.save()

    # 🎧 Encodage MP3 avec lame
    print(f"🎧 MP3 : {filename} → {mp3_path}")
    subprocess.run(["lame", "-V2", wav_path, mp3_path], check=True)

    # 🖋️ Métadonnées MP3
    try:
        try:
            audio_id3 = EasyID3(mp3_path)
        except mutagen.id3.ID3NoHeaderError:
            audio_id3 = mutagen.File(mp3_path, easy=True)
            audio_id3.add_tags()
    except error:
        audio_id3 = MP3(mp3_path, ID3=ID3)
        audio_id3.add_tags()
        audio_id3 = EasyID3(mp3_path)

    audio_id3["title"] = title_part
    audio_id3["artist"] = artist
    audio_id3["album"] = title_part
    audio_id3["tracknumber"] = "1"
    audio_id3["website"] = website
    audio_id3.save()

    if os.path.exists(cover_path):
        with open(cover_path, "rb") as f:
            image_data = f.read()
        audio_mp3 = MP3(mp3_path, ID3=ID3)
        try:
            audio_mp3.add_tags()
        except error:
            pass
        audio_mp3.tags.add(APIC(
            encoding=3,
            mime='image/png',
            type=3,
            desc='Cover',
            data=image_data
        ))
        audio_mp3.save()
    else:
        print(f"⚠️  Pochette non trouvée : {cover_path}")

    print(f"✅ Fichiers terminés pour : {title_part}\n")
