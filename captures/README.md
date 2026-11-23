# Capture inventory

Dates and folder times are local Europe/Moscow (UTC+3), 2026-11-23. Main recordings:

| Folder / binary | Duration | Bytes | Valid complete frames | State |
|---|---:|---:|---:|---|
| `20261123_174721/mppt_4800_8N1_30s.bin` | 30 s | 1440 | 120 | Zero current |
| `20261123_180104_loaded/loaded_4800_8N1.bin` | 60 s | 2880 | 240 | Around 2.8 A, derived mean 187.304 W |
| `20261123_180405_charging/charging_4800_8N1.bin` | 60 s | 2880 | 240 | Lower current, derived mean 80.62 W |

Binary UART streams are unmodified. JSON/CSV are derived records; text notes have had local workspace paths normalized for publication. Some original names still use `candidate_current_A` / `candidate_output_power_W`, reflecting uncertainty at capture time; see the protocol document for the current interpretation.

The first folder also includes the baud/format comparison and a 12-second verification capture. Files at the wrong baud rate are deliberately retained as evidence of misdecoding; **do not parse them as physical measurements**.

Each principal capture includes one Windows driver overrun indication (flag 2). Captured complete frames all pass the additive checksum; complete losslessness is not claimed. Chunk timestamps are host read-completion times. Display references are approximate, asynchronous and not frame-synchronized.

USB adapter serial/location and local absolute paths are not needed to reproduce the protocol. No Wi-Fi/network secrets or firmware images are included. UART `.bin` files here contain the controller's observed measurement bytes, not firmware.
