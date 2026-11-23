SBC1200R MPPT: passive UART capture on COM7

Working receive configuration:
4800 baud, 8 data bits, no parity, 1 stop bit, no flow control.
Adapter: Silicon Labs CP210x, VID:PID 10C4:EA60, serial 0001.
No bytes were transmitted. RTS and DTR were set false before opening.
The port was closed after capture.

Validation:
30 seconds, 1440 bytes, 120 complete frames, 120 valid checksums.
Median frame interval: 0.24917 seconds (approximately 4 Hz).
Both 8E1 and 8O1 caused parity errors. 8N2 also received the frames;
the transmitted stop-bit count cannot be established from these captures.
Windows reported CE_OVERRUN (flag 2) once during the 30-second capture;
all 120 captured frames were complete and checksum-valid.

Example frame (12 bytes; offsets below are zero-based):
FE FE FE FE 07 CE 16 00 00 18 08 04

0..3: FE FE FE FE, synchronization header.
4:    07, likely length of the following six data bytes plus checksum.
5..6: uint16 little-endian / 100 = output voltage (58.38..58.40 V).
7..8: zero in this recording; candidate current field. Its units and
      scaling require a capture with nonzero current.
9..10:uint16 little-endian / 100 = input voltage (20.70..20.72 V).
11:   checksum = sum(bytes at offsets 5 through 10) modulo 256.

The user confirmed displayed input about 20.7 V, output 58.3..58.4 V,
and current zero. Voltage field assignment is supported by this match;
testing with changing voltage/current will provide further validation.

Main files:
mppt_4800_8N1_30s.bin          - unmodified received byte stream
mppt_4800_8N1_30s_frames.json  - parsed frames and timestamps
mppt_4800_8N1_30s_chunks.json  - received chunks and host timestamps
mppt_summary.json             - capture statistics
scan.json, verify.json        - baud/format comparison results

Chunk timestamps are host read-completion times, not individual UART
edge/byte timestamps. Captures at other baud rates contain misdecoded
data and are retained only as diagnostic comparisons.
