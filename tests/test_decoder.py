import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mppt_uart", ROOT / "tools" / "mppt_uart.py")
mppt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mppt
spec.loader.exec_module(mppt)

IDLE = bytes.fromhex("FE FE FE FE 07 CE 16 00 00 18 08 04")
LOADED = bytes.fromhex("FE FE FE FE 07 E0 19 19 01 4B 07 65")


class DecoderTests(unittest.TestCase):
    def test_documented_values(self):
        idle, loaded = mppt.Decoder().feed(IDLE + LOADED)
        self.assertEqual((idle.output_voltage_V, idle.output_current_A, idle.input_voltage_V),
                         (58.38, 0, 20.72))
        self.assertEqual((loaded.output_voltage_V, loaded.output_current_A, loaded.input_voltage_V),
                         (66.24, 2.81, 18.67))
        self.assertAlmostEqual(loaded.output_power_W, 186.1344)

    def test_real_captures(self):
        files = {
            "20261123_174721/mppt_4800_8N1_30s.bin": 120,
            "20261123_180104_loaded/loaded_4800_8N1.bin": 240,
            "20261123_180405_charging/charging_4800_8N1.bin": 240,
        }
        for filename, count in files.items():
            with self.subTest(filename=filename):
                decoder, readings = mppt.decode_file(ROOT / "captures" / filename)
                self.assertEqual(len(readings), count)
                self.assertEqual(decoder.bad_checksums, 0)
                self.assertEqual(decoder.discarded_bytes, 0)
                self.assertFalse(decoder.buffer)

    def test_arbitrary_read_boundaries(self):
        data = b"noise" + IDLE + LOADED
        for width in [1, 2, 3, 4, 7, 11, 12, 13, 4096]:
            with self.subTest(width=width):
                decoder = mppt.Decoder()
                readings = []
                for i in range(0, len(data), width):
                    readings.extend(decoder.feed(data[i:i + width]))
                self.assertEqual([r.hex for r in readings],
                                 [IDLE.hex(" ").upper(), LOADED.hex(" ").upper()])
                self.assertEqual([r.offset for r in readings], [5, 17])

    def test_corrupted_frame_rejected_then_recovers(self):
        corrupt = bytearray(IDLE)
        corrupt[6] ^= 1
        decoder = mppt.Decoder()
        readings = decoder.feed(bytes(corrupt) + LOADED)
        self.assertEqual([r.hex for r in readings], [LOADED.hex(" ").upper()])
        self.assertEqual(decoder.bad_checksums, 1)

    def test_lost_byte_and_extra_header_recover(self):
        data = IDLE[:8] + IDLE[9:] + b"\xfe\xfe" + LOADED
        self.assertEqual([r.hex for r in mppt.Decoder().feed(data)],
                         [LOADED.hex(" ").upper()])

    def test_unknown_type_not_accepted(self):
        other = bytearray(IDLE)
        other[4] = 8
        self.assertEqual([r.hex for r in mppt.Decoder().feed(bytes(other) + LOADED)],
                         [LOADED.hex(" ").upper()])

    def test_partial_frame_waits_for_remaining_bytes(self):
        decoder = mppt.Decoder()
        self.assertEqual(decoder.feed(IDLE[:11]), [])
        self.assertEqual(len(decoder.feed(IDLE[11:])), 1)

    def test_noise_does_not_grow_buffer_without_bound(self):
        decoder = mppt.Decoder()
        self.assertEqual(decoder.feed(b"\xaa" * 100000), [])
        self.assertLessEqual(len(decoder.buffer), 3)


if __name__ == "__main__":
    unittest.main()
