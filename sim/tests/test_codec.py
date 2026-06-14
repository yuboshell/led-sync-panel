"""The panel shows a positional (mixed-radix) time-code: a fast 'fine' row that
sweeps one lit position per step, and a slower 'coarse' row that advances once
per fine wrap. fine is the low-order digit, coarse the high-order digit."""
from ledsync.codec import Codec


def test_encode_splits_count_into_fine_low_digit_and_coarse_high_digit():
    codec = Codec(fine_n=16, coarse_n=16)
    # 20 = 1*16 + 4  ->  fine position 4, coarse position 1
    reading = codec.encode(20)
    assert (reading.fine_pos, reading.coarse_pos) == (4, 1)


def test_decode_inverts_encode_across_the_unambiguous_range():
    codec = Codec(fine_n=16, coarse_n=16)
    assert codec.n_codes == 256
    for count in range(codec.n_codes):
        assert codec.decode(codec.encode(count)) == count


def test_count_beyond_range_wraps_modulo_n_codes():
    codec = Codec(fine_n=16, coarse_n=16)
    # the coarse row has only coarse_n positions, so the counter is cyclic
    assert codec.encode(256) == codec.encode(0)
    assert codec.decode(codec.encode(257)) == 1
