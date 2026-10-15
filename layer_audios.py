import argparse
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

SAMPLE_RATE = 44100
FILE_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}


def parse_input(spec):
    # split on last colon so Windows drive letters (C:\a.mp3) aren't read as a volume
    path, sep, tail = spec.rpartition(":")
    if sep:
        try:
            return path, float(tail)
        except ValueError:
            pass
    return spec, 1.0


def expand(spec):
    path, volume = parse_input(spec)
    if not Path(path).is_dir():
        return [(path, volume)]
    files = sorted(p for p in Path(path).iterdir() if p.suffix.lower() in FILE_EXTENSIONS)
    return [(str(p), volume) for p in files]


def layer(specs, output):
    entries = [entry for spec in specs for entry in expand(spec)]
    if len(entries) < 2:
        sys.exit("Need at least two audio files to layer.")
    if any(volume < 0 for _, volume in entries):
        sys.exit("Volume can't be negative.")

    output.parent.mkdir(parents=True, exist_ok=True)

    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error", "-stats"]
    filters = []
    for i, (path, volume) in enumerate(entries):
        command += ["-i", path]
        filters.append(
            f"[{i}:a]aformat=sample_rates={SAMPLE_RATE}:channel_layouts=stereo,"
            f"volume={volume}[a{i}]"
        )
    labels = "".join(f"[a{i}]" for i in range(len(entries)))
    # normalize=0 bc amix otherwise divides every input by track count which would undo chosen volumes
    filters.append(f"{labels}amix=inputs={len(entries)}:duration=shortest:normalize=0")
    command += ["-filter_complex", ";".join(filters), str(output)]

    returncode = subprocess.run(command).returncode
    if returncode:
        sys.exit(returncode)
    print(f"Wrote {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Layer audio files and trim the result to the shortest one."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="audio files or folders, each optionally followed by :VOLUME (e.g. bass.mp3:0.5)",
    )
    parser.add_argument("-o", "--output", default="layered.wav", help="output filename")
    parser.add_argument(
        "-d", "--output-dir", default="output", help="folder to save into (created if missing)"
    )
    args = parser.parse_args()

    layer(args.inputs, Path(args.output_dir) / args.output)


if __name__ == "__main__":
    main()