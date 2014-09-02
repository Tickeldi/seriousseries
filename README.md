seriousseries
=============

A small python script that will download a whole ton of episodes.

It needs youtube-dl as a dependency.

And a lot of work.



usage: seriousseries [-h] [-s season] [-e episode] name

positional arguments:
  name        name of the series you want to download

optional arguments:
  -h, --help  show this help message and exit
  -s season   the number of the season you want to download
  -e episode  the number of the episode you want to download

If you don't provide an episode this program will try to download the provided
season. If you don't provide a season it will try to download all seasons.




To do List:
- Add feature to automagically download the newest or latest n episodes of a series.
- Proper use of exceptions and corresponding, sane error messages.
- Add different verbosity levels
- Add options to change behaviour of downloader (names, skipping already downloaded files, prefering certain providers)
