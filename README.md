# challengectl
Queues challenges and gr-osmosdr radios to transmit for the WCTF

`./challengectl.py [flags file] [devices file]`




## TODO

### Fix 11025bps SSTV files not playing with nbfm.
Add resampler block
```
Traceback (most recent call last):
  File "/usr/lib/python3.6/multiprocessing/process.py", line 258, in _bootstrap
    self.run()
  File "/usr/lib/python3.6/multiprocessing/process.py", line 93, in run
    self._target(*self._args, **self._kwargs)
  File "./challengectl.py", line 126, in fire_nbfm
    nbfm.main(wav_src, wav_rate, freq, device)
  File "/home/corey/WCTF/challengectl/challenges/nbfm.py", line 201, in main
    tb = top_block_cls()
  File "/home/corey/WCTF/challengectl/challenges/nbfm.py", line 90, in __init__
    fh=-1.0,
  File "/usr/local/lib/python3/dist-packages/gnuradio/analog/nbfm_tx.py", line 61, in __init__
    raise ValueError("quad_rate is not an integer multiple of audio_rate")
ValueError: quad_rate is not an integer multiple of audio_rate
```
