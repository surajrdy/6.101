"""
6.101 Lab:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    sound1 = {"rate": sound["rate"], "samples": sound["samples"][::-1]}

    return sound1


def mix(sound1, sound2, p):
    """
    Returns a new sound containing the mix of two different sounds controled 
    by the mixing parameter

    Args:
        sound1: a dictionary representing the first sound
        sound2: a dictionary representing the second sound
        p: the mixing parameter which is between 0 and 1 inclusively 

    Returns:
        A new mono sound dictionary with the mixed sound
    """
    # mix 2 good sounds
    if (
        "rate" not in sound1 or "rate" not in sound2
        or sound1["rate"] != sound2["rate"]
    ):

        print("no")
        return None

    r = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    if len(sound1) < len(sound2):
        leng = len(sound1)
    elif len(sound2) < len(sound1):
        leng = len(sound2)
    elif len(sound1) == len(sound2):
        leng = len(sound1)
    else:
        print("whoops")
        return None

    samps = []
    x = 0
    while x <= leng:
        s2, s1 = p * sound1[x], sound2[x] * (1 - p)
        samps.append(s1 + s2)  # add sounds
        x += 1
        if x == leng:  # end
            break

    return {"rate": r, "samples": samps}  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """

    # Relevant variables for inner-functions in the echo function
    sample_delay = round(delay * sound['rate'])
    original = sound["samples"][:]
    max_output = len(original) + (num_echoes * sample_delay)
    output = max_output * [0]
    #For loop to copy over the original input samples into our new memory area
    for i, var in enumerate(original):
        output[i] = var

    #Usage of an iteration variable to calculate the individual delays for the echoes
    echo_count = 1
    while echo_count <= num_echoes:
        #Offset of when to start the addition of new scaled samples
        offset = echo_count * sample_delay
        specific_scale = scale ** echo_count
        #considers the original sample length w/o 0s and finds the offset index
        for i, var in enumerate(original):
            off_i = i + offset
            #off_i will  never be larger than the length of the maximum output.
            output[off_i] += specific_scale * var
        echo_count += 1
    return {"rate": sound["rate"], "samples": output}


def pan(sound):
    """
    Compute a pan version of stereo sound where we modify/scale 
    the left and right samples

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new stereo sound dictionary resulting from applying the pan effect.
    """
    example = sound["left"]
    length = len(example)
    l_copy = length * [0]
    r_copy = length * [0]
    for i, var in enumerate(sound["left"]):
        scale = 1 - i/(length-1)
        if i == 0:
            l_copy[i] = var
        elif i == len(l_copy) - 1:
            l_copy[i] = 0
        else:
            l_copy[i] = var * scale
    for i, var in enumerate(sound["right"]):
        scale = i/(length-1)
        if i == 0:
            r_copy[i] = 0
        elif i == len(r_copy) - 1:
            r_copy[i] = var
        else:
            r_copy[i] = var * scale
    return {"rate": sound["rate"], "left": l_copy, "right": r_copy}
def remove_vocals(sound):
    """
    Compute a mono version of stereo sound where we remove the vocals from the sound

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary resulting from applying the remove_vocals effect.
    """
    #Initialize the mono_sample list as 0s
    mono_sample = len(sound["left"]) * [0]

    #Simple for loop for calculating the difference
    for i in range(len(sound["left"])):
        mono_sample[i] += sound["left"][i] - sound["right"][i]
    #Return the mono_sound instead of stereo
    return {"rate": sound["rate"], "samples": mono_sample}


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # Code placed inside the if __name__ == "__main__" statement will only
    # be executed when you run the lab.py file.

    # Code placed in this special if statement will not be executed when you run
    # the tests in the test.py file or when you submit your code to the submission
    # server.

    # This makes it a good place to put your code for generating and saving
    # sounds, or any other code you write for testing on your computer.

    # Note that your checkoff conversation with a staff member will likely involve
    # showing and discussing the code you wrote to generate the sounds that you
    # submitted on the lab page, so please do not delete that code. However, you
    # can comment it out.

    # Here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file):

    #print("Loading mystery file...")
    #hello = load_wav("sounds/mystery.wav")

    #write_wav(backwards(hello), "mystery_reversed.wav")

    print("Loading mystery file...")
    mount = load_wav("sounds/lookout_mountain.wav", stereo=True)

    write_wav(remove_vocals(mount), "lookout_mountain_no_vocals.wav")
