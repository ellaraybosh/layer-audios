# layer-audios

A small Python CLI for layering audio files. Mix multiple tracks together, adjust their volumes individually, and automatically trim the output to the length of the shortest track.

## Requirements

- Python 3.8+
- FFmpeg
- Dependencies listed in `requirements.txt`

## Setup

```bash
git clone https://github.com/ellaraybosh/layer-audios.git
cd layer-audios
pip install -r requirements.txt
```

## Usage

```bash
python layer_audios.py INPUT [INPUT ...] [-o OUTPUT] [-d OUTPUT_DIR]
```

Pass at least two audio files, folders, or a mix of both. By default, the result is saved as `output/layered.wav`.

### Mixing tracks

```bash
python layer_audios.py drums.mp3 bass.mp3 vocals.wav -o mix.wav
```

You can use different input formats in the same command. The output format is determined by the extension you give it.

### Adjusting volume

Add `:VOLUME` to an input to change its volume. This is a multiplier, so `1.0` keeps the original volume, `0.5` halves it, and `2.0` doubles it. Use `0` to mute a track.

```bash
python layer_audios.py drums.mp3 bass.mp3:0.5 vocals.wav:1.5 -o mix.wav
```

Inputs without a specified volume stay at `1.0`. Volume settings also work with folders.

### Using folders

Pass a folder to include all supported audio files inside it. Subfolders are ignored.

```bash
python layer_audios.py my_tracks -o mix.wav
python layer_audios.py my_tracks:0.5 -o mix.wav
python layer_audios.py drums_folder:0.8 vocals.wav:1.5 -o mix.mp3
```

Supported formats: `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, and `.aac`.

**Note:** Don't save the output inside a folder you're using as an input. Otherwise, a later run may include the previous output in the mix.

### Choosing where to save the result

Use `-o` to set the output filename and `-d` to choose the output directory. The directory is created automatically if it doesn't exist.

```bash
python layer_audios.py a.mp3 b.mp3 -o mix.mp3 -d myoutput
```

This saves the result to `myoutput/mix.mp3`.

### File paths

Put paths containing spaces in quotes. If you're setting a volume, include it inside the quotes.

```bash
python layer_audios.py "my tracks/a.mp3:0.5" "my tracks/b.mp3" -o mix.wav
```

For the full list of options:

```bash
python layer_audios.py -h
```

## How it works

- All tracks start at `0:00` and the output ends at the shortest input.
- Audio is processed through FFmpeg rather than loading entire files into memory, so longer recordings can be mixed without holding them all in RAM.
- Output is always 44.1 kHz stereo.
- Tracks are added together, so mixing too many tracks or using high volume multipliers can cause clipping. Try lowering the individual volumes if the result sounds distorted.

The script requires at least two audio files, rejects negative volume values, and requires the output filename to have a valid extension.

## License

MIT
