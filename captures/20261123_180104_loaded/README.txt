SBC1200R UART: first capture with charging current

COM7, 4800 baud, 8N1, no flow control. Receive only; no bytes sent.
60 seconds, 2880 bytes, 240 complete checksum-valid frames.
All frames have the same format; no unclassified bytes were found.

Observed frame, zero-based byte offsets:
0..3  FE FE FE FE : synchronization header
4     07          : likely length of data plus checksum
5..6  uint16 LE / 100 : output voltage, volts
7..8  uint16 LE / 100 : current, amperes
9..10 uint16 LE / 100 : input voltage, volts
11    sum(bytes 5..10) modulo 256

Current scaling is supported by the user's displayed 2.8 A.
Output-current assignment is inferred from the displayed power:
approximately 66.3 V * 2.8 A = 186 W.
Calculated output power in this recording: 172.991..192.642 W,
mean 187.304 W. Display references were supplied asynchronously,
so they are approximate, not synchronized per-frame measurements.

User also reports a temperature of 26 C and an energy counter in kWh.
No separate temperature, power or energy field was identified in this
recording. Their absence here does not exclude other message types,
requests or a different interface.

The single Windows CE_OVERRUN flag (2) is retained in driver_errors.json.
Every captured frame is complete and checksum-valid.

loaded_4800_8N1.bin : unmodified received bytes
frames.csv / frames.json : decoded frames, host timestamps and raw hex
summary.json : ranges, capture statistics and display references
chunks.json : original receive chunks with host timestamps
