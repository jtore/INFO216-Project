import random
import string

# Generate a hash to use as a ID for a nhterm:Event


def generate_uuid():
    # Makes 5 sections of different length, with random numbers
    start_sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))
    _2sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    _3sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    _4sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    end_sect = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(12))

    # Concatenates all the sections into one uuid
    _hash = start_sect + "-" + _2sect + "-" + _3sect + "-" + _4sect + "-" + end_sect
    # Returns the hash to be used in our aggregator
    return _hash


if __name__ == '__main__':
    generate_uuid()
