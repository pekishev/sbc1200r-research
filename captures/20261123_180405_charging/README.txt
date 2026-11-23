SBC1200R charging capture

COM7: 4800 8N1, no flow control, receive only. No bytes transmitted.
60 seconds, 2880 bytes, 240 complete frames, 240 valid checksums.
Frame format is documented in ../20261123_180104_loaded/README.txt.

Output: 65.88..66.00 V; mean 65.987 V.
Current: 0.80..1.24 A; mean 1.222 A.
Input: 19.22..19.79 V; mean 19.657 V.
Calculated output power: 52.704..81.84 W; mean 80.62 W.

The earlier user-reported 2.8 A and 186 W agree with the preceding
18:01 recording (mean calculated power 187.304 W). The power/current
had decreased by this recording; display references are not synchronized.

All frames are of the same observed type with six payload bytes.
No separate temperature or energy field was identified.
A single Windows CE_OVERRUN flag (2) is recorded in driver_errors.json.
The serial port was closed after recording.

charging_4800_8N1.bin: unmodified received bytes
frames.csv / frames.json: decoded frames and host read timestamps
summary.json: statistics and display-reference notes
chunks.json: original receive chunks
