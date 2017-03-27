# Sylvia

Search pronunciations in the CMU Pronouncing Dictionary using a reglular-expression like syntax. Input-format regular expressions are lightly preprocessed into Python-format regular expressions, and then mapped over an encoded version of cmudict.

Sylvia's query format is nearly identical to traditional regular expressions, with the exception that it is intended not to match against patterns of characters, but rather patterns of phonemes. To construct a regular expression query for Sylvia, remember the following rules:

1. Whitespace must be used to delimit consecutive phoneme literals. It may also be used anywhere else in the regular expression, as whitespace is meaningless in the context of a phoneme sequence, and will be stripped during preprocessing.
1. `#` is a shortcut for "any consonant sound"
1. `@` is a shortcut for "any vowel sound"
1. `%` is a shortcut for "any syllable", and is equivalant to `#*@#*`
1. Otherwise, whatever flies with Python's regular expression format will work in Sylvia. Just use some common sense, as some things (such as character classes) will be wholly inapplicable to searches in phoneme-space.

Consult the cmudict documentation to learn more about the phoneme set: http://www.speech.cs.cmu.edu/cgi-bin/cmudict 

Consult the Python docs to learn more about Python's regex format: https://docs.python.org/2/library/re.html

# Examples

Find words starting with zero or more consonant sounds, followed by the "long E" sound (phoneme EY), followed by zero or more consonant sounds, followed by the "ed" sound (the phoneme sequence EH D):

```bash
> python -m sylvia --regex '#* IY #* EH D'
Beachhead
Behead
Retread
Seabed
Steelhead
```
Find all six syllable words where the first syllable uses the "short i" sound (phoneme IH), and ends in either the D or P phonemes.

```bash
> python -m sylvia --regex "#*IH%%%%%(D|P)"
Deteriorated
Differentiated
Disassociated
Discombobulated
Incapacitated
Individualized
Institutionalized
Insubstantiated
Internationalized
Interrelationship
Misappropriated
```
Note here that only five % symbols are needed, as a single vowel sound constitutes a single syllable, and we explicitly call out the first vowel sound via IH.

Find all words that start with the R sound, followed by some vowel, followed by the D sound, followed by another vowel, followed by the NG phoneme:

```bash
> python -m sylvia --regex "R@D@NG"
Raiding
Rawding
Reading
Redding
Reding
Ridding
Riding
Rodding
Ruding
```
If you just want to lookup the pronunciations for a word, you can do that too:

```bash
> python -m sylvia --lookup tomato
T AH M EY T OW
T AH M AA T OW
```

# Experimental Features

```bash
> python -m sylvia --rhyme closure
Composure
Crozier
Disclosure
Enclosure
Exposure
Foreclosure
Inclosure
Losure
Mosher
Mosier
Overexposure
```

```bash
> python -m sylvia --rhyme support
Laporte
Rapaport
Rapoport
Rappaport
Rappoport
Teleport
```

```bash
> python -m sylvia --near_rhyme support
Comport
Davenport
Davenport's
Gulfport
Gumport
Kennebunkport
Laporte
Rapaport
Rapoport
Rappaport
Rappoport
Supports
Teleport
Teleport's
Williamsport
```

```bash
> python -m sylvia --vowel_match ivanhoe
Amyotrophic
Ayatollah
Ayatollah's
Byelorussia
Cuyahoga
Cyclostome
Cyclostomes
Diagnose
Diagnosed
Diagnoses
Diagnosing
Diagnosis
Dialtone
Diantonio
Diaphonia
Dinotopia
Dynamo
Gyroscope
Gyroscopes
Iacocca
Iacocca's
Iacona
Iacono
Icenogle
Idaho
Idaho's
Idaho-falls
Isentrope
Isotope
Isotopes
Ivaco
Kaleidoscope
Kayapo
Microphone
Microscope
Microscopes
Piezoelectric
Stereomicroscope
Styrofoam
Titleholder
Virazole
Xylophone
Zydeco
```
