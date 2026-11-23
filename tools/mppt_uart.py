#!/usr/bin/env python3
"""Passive SBC1200R UART capture and offline decoder. Python 3.10+."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
import time

HEADER = b"\xfe\xfe\xfe\xfe"
FRAME_SIZE = 12


@dataclass(frozen=True)
class Reading:
    offset: int
    output_voltage_V: float
    output_current_A: float
    input_voltage_V: float
    output_power_W: float
    hex: str


class Decoder:
    """Accept arbitrarily chunked bytes and resynchronize after corruption."""

    def __init__(self) -> None:
        self.buffer = bytearray()
        self.offset = 0
        self.discarded_bytes = 0
        self.bad_checksums = 0

    def _drop(self, count: int, *, discarded: bool = True) -> None:
        del self.buffer[:count]
        self.offset += count
        if discarded:
            self.discarded_bytes += count

    def feed(self, data: bytes) -> list[Reading]:
        self.buffer.extend(data)
        readings = []
        while self.buffer:
            position = self.buffer.find(HEADER)
            if position < 0:
                # Preserve a possible partial four-byte synchronization header.
                self._drop(max(0, len(self.buffer) - 3))
                break
            self._drop(position)
            if len(self.buffer) < 5:
                break
            if self.buffer[4] != 7:
                self._drop(1)
                continue
            if len(self.buffer) < FRAME_SIZE:
                break
            frame = bytes(self.buffer[:FRAME_SIZE])
            if sum(frame[5:11]) & 0xFF != frame[11]:
                self.bad_checksums += 1
                self._drop(1)
                continue
            vout, iout, vin = (
                int.from_bytes(frame[i : i + 2], "little") / 100
                for i in (5, 7, 9)
            )
            readings.append(Reading(
                self.offset, vout, iout, vin, round(vout * iout, 4),
                frame.hex(" ").upper(),
            ))
            self._drop(FRAME_SIZE, discarded=False)
        return readings


def decode_file(path: Path) -> tuple[Decoder, list[Reading]]:
    decoder = Decoder()
    readings = []
    with path.open("rb") as stream:
        while block := stream.read(4096):
            readings.extend(decoder.feed(block))
    return decoder, readings


def decode_command(args: argparse.Namespace) -> int:
    decoder, readings = decode_file(args.input)
    fieldnames = list(Reading.__dataclass_fields__)
    output = args.output.open("w", newline="", encoding="utf-8") if args.output else sys.stdout
    try:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(reading) for reading in readings)
    finally:
        if args.output:
            output.close()
    print(json.dumps({
        "valid_frames": len(readings),
        "bad_checksum_candidates": decoder.bad_checksums,
        "discarded_bytes": decoder.discarded_bytes,
        "trailing_buffer_bytes": len(decoder.buffer),
    }), file=sys.stderr)
    return 0 if readings else 1


def capture_command(args: argparse.Namespace) -> int:
    if args.seconds <= 0:
        raise ValueError("--seconds must be positive")
    import serial  # Optional dependency, only needed for live capture.

    chunk_path = args.output.with_suffix(args.output.suffix + ".chunks.json")
    if args.output.exists() or chunk_path.exists():
        raise FileExistsError("Capture or chunk file exists; choose another output path")
    port = serial.Serial(
        port=None, baudrate=args.baud, bytesize=args.data_bits,
        parity=args.parity, stopbits=args.stop_bits, timeout=0.02,
        xonxoff=False, rtscts=False, dsrdtr=False,
    )
    port.dtr = False
    port.rts = False
    port.port = args.port
    chunks = []
    byte_count = 0
    start = time.monotonic()
    try:
        port.open()
        start = time.monotonic()
        with args.output.open("xb") as output:
            try:
                while time.monotonic() - start < args.seconds:
                    data = port.read(4096)
                    if data:
                        output.write(data)
                        output.flush()
                        byte_count += len(data)
                        chunks.append({
                            "t": round(time.monotonic() - start, 6),
                            "hex": data.hex(" "),
                        })
            except KeyboardInterrupt:
                pass
    finally:
        port.close()
    chunk_path.write_text(json.dumps({
        "settings": {
            "port": args.port, "baud": args.baud, "data_bits": args.data_bits,
            "parity": args.parity, "stop_bits": args.stop_bits,
            "flow_control": "none", "transmitted_bytes": 0,
        },
        "elapsed_s": round(time.monotonic() - start, 6),
        "bytes": byte_count,
        "timestamp_note": "Host read completion, not UART edge timing",
        "chunks": chunks,
    }, indent=2), encoding="utf-8")
    print(f"Saved {byte_count} received bytes to {args.output}; port closed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    decode = commands.add_parser("decode", help="Decode a binary UART capture to CSV")
    decode.add_argument("input", type=Path)
    decode.add_argument("--output", type=Path)
    decode.set_defaults(func=decode_command)
    capture = commands.add_parser("capture", help="Receive only; never writes to the controller")
    capture.add_argument("--port", required=True)
    capture.add_argument("--seconds", type=float, default=60)
    capture.add_argument("--output", type=Path, required=True)
    capture.add_argument("--baud", type=int, default=4800)
    capture.add_argument("--data-bits", type=int, choices=[7, 8], default=8)
    capture.add_argument("--parity", choices=["N", "E", "O"], default="N")
    capture.add_argument("--stop-bits", type=int, choices=[1, 2], default=1)
    capture.set_defaults(func=capture_command)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
